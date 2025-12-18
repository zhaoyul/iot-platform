package main

import (
	"context"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/go-git/go-git/v5"
	"github.com/go-git/go-git/v5/plumbing"
	"github.com/go-git/go-git/v5/plumbing/object"
	"github.com/go-redis/redis/v8"
)

type GitParserService struct {
	redisClient *redis.Client
	repoPath    string
}

type CommitInfo struct {
	Hash      string    `json:"hash"`
	Message   string    `json:"message"`
	Author    string    `json:"author"`
	Email     string    `json:"email"`
	Date      time.Time `json:"date"`
	FileCount int       `json:"file_count"`
}

type DiffAnalysis struct {
	FilesChanged int      `json:"files_changed"`
	Additions    int      `json:"additions"`
	Deletions    int      `json:"deletions"`
	Files        []string `json:"files"`
}

func NewGitParserService(redisURL, repoPath string) *GitParserService {
	opt, err := redis.ParseURL(redisURL)
	if err != nil {
		log.Fatalf("Failed to parse Redis URL: %v", err)
	}

	return &GitParserService{
		redisClient: redis.NewClient(opt),
		repoPath:    repoPath,
	}
}

func (gps *GitParserService) GetCommitInfo(w http.ResponseWriter, r *http.Request) {
	repoName := chi.URLParam(r, "repo")
	commitHash := chi.URLParam(r, "commit")

	// 尝试从缓存获取
	cacheKey := "commit:" + repoName + ":" + commitHash
	cached, err := gps.redisClient.Get(context.Background(), cacheKey).Result()
	if err == nil {
		w.Header().Set("Content-Type", "application/json")
		w.Header().Set("X-Cache", "HIT")
		w.Write([]byte(cached))
		return
	}

	// 打开仓库
	repoPath := gps.repoPath + "/" + repoName
	repo, err := git.PlainOpen(repoPath)
	if err != nil {
		http.Error(w, "Repository not found", http.StatusNotFound)
		return
	}

	// 获取提交对象
	hash := plumbing.NewHash(commitHash)
	commit, err := repo.CommitObject(hash)
	if err != nil {
		http.Error(w, "Commit not found", http.StatusNotFound)
		return
	}

	// 统计文件数量
	tree, _ := commit.Tree()
	fileCount := 0
	tree.Files().ForEach(func(f *object.File) error {
		fileCount++
		return nil
	})

	commitInfo := CommitInfo{
		Hash:      commit.Hash.String(),
		Message:   commit.Message,
		Author:    commit.Author.Name,
		Email:     commit.Author.Email,
		Date:      commit.Author.When,
		FileCount: fileCount,
	}

	// 缓存结果
	jsonData, _ := json.Marshal(commitInfo)
	gps.redisClient.Set(context.Background(), cacheKey, jsonData, 1*time.Hour)

	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("X-Cache", "MISS")
	json.NewEncoder(w).Encode(commitInfo)
}

func (gps *GitParserService) AnalyzeDiff(w http.ResponseWriter, r *http.Request) {
	repoName := chi.URLParam(r, "repo")
	fromCommit := r.URL.Query().Get("from")
	toCommit := r.URL.Query().Get("to")

	repoPath := gps.repoPath + "/" + repoName
	repo, err := git.PlainOpen(repoPath)
	if err != nil {
		http.Error(w, "Repository not found", http.StatusNotFound)
		return
	}

	fromHash := plumbing.NewHash(fromCommit)
	toHash := plumbing.NewHash(toCommit)

	fromCommitObj, err := repo.CommitObject(fromHash)
	if err != nil {
		http.Error(w, "From commit not found", http.StatusNotFound)
		return
	}

	toCommitObj, err := repo.CommitObject(toHash)
	if err != nil {
		http.Error(w, "To commit not found", http.StatusNotFound)
		return
	}

	fromTree, _ := fromCommitObj.Tree()
	toTree, _ := toCommitObj.Tree()

	changes, err := fromTree.Diff(toTree)
	if err != nil {
		http.Error(w, "Failed to compute diff", http.StatusInternalServerError)
		return
	}

	analysis := DiffAnalysis{
		FilesChanged: len(changes),
		Files:        []string{},
	}

	for _, change := range changes {
		patch, _ := change.Patch()
		if patch != nil {
			for _, filePatch := range patch.FilePatches() {
				from, to := filePatch.Files()
				if to != nil {
					analysis.Files = append(analysis.Files, to.Path())
				} else if from != nil {
					analysis.Files = append(analysis.Files, from.Path())
				}

				for _, chunk := range filePatch.Chunks() {
					if chunk.Type() == 1 { // Addition
						analysis.Additions += len(chunk.Content())
					} else if chunk.Type() == 2 { // Deletion
						analysis.Deletions += len(chunk.Content())
					}
				}
			}
		}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(analysis)
}

func (gps *GitParserService) HealthCheck(w http.ResponseWriter, r *http.Request) {
	// 检查Redis连接
	_, err := gps.redisClient.Ping(context.Background()).Result()
	if err != nil {
		http.Error(w, "Redis connection failed", http.StatusServiceUnavailable)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{
		"status": "healthy",
		"service": "git-parser",
	})
}

func main() {
	redisURL := os.Getenv("REDIS_URL")
	if redisURL == "" {
		redisURL = "redis://localhost:6379"
	}

	repoPath := os.Getenv("REPO_PATH")
	if repoPath == "" {
		repoPath = "/repositories"
	}

	service := NewGitParserService(redisURL, repoPath)

	r := chi.NewRouter()
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)
	r.Use(middleware.RealIP)
	r.Use(middleware.Timeout(60 * time.Second))

	// 路由
	r.Get("/health", service.HealthCheck)
	r.Get("/api/v1/repos/{repo}/commits/{commit}", service.GetCommitInfo)
	r.Get("/api/v1/repos/{repo}/diff", service.AnalyzeDiff)

	log.Println("Git Parser Service starting on :8080")
	http.ListenAndServe(":8080", r)
}
