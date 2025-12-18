(ns iot-platform.git.handler
  "Git repository operations handler"
  (:require [clojure.data.json :as json]
            [clj-jgit.porcelain :as git]
            [clj-jgit.querying :as git-query]
            [taoensso.timbre :as log]
            [iot-platform.cache :as cache]))

(defn get-commit
  "Get commit information by hash"
  [{:keys [path-params]}]
  (let [{:keys [repo hash]} path-params
        cache-key (str "commit:" repo ":" hash)
        cached (cache/get-cached cache-key)]
    
    (if cached
      {:status 200
       :headers {"X-Cache" "HIT"}
       :body (json/read-str cached :key-fn keyword)}
      
      (try
        (let [repo-path (str "/repositories/" repo)
              repository (git/load-repo repo-path)
              commit (git-query/find-rev-commit repository hash)
              commit-info {:hash (.getName commit)
                           :message (.getFullMessage commit)
                           :author (-> commit .getAuthorIdent .getName)
                           :email (-> commit .getAuthorIdent .getEmailAddress)
                           :date (-> commit .getCommitTime (* 1000))
                           :parents (map #(.getName %) (.getParents commit))}
              json-response (json/write-str commit-info)]
          
          ;; Cache for 1 hour
          (cache/set-cached cache-key json-response 3600)
          
          {:status 200
           :headers {"X-Cache" "MISS"
                     "Content-Type" "application/json"}
           :body commit-info})
        
        (catch Exception e
          (log/error e "Failed to get commit" hash)
          {:status 404
           :body {:error "Commit not found"}})))))

(defn analyze-diff
  "Analyze differences between two commits"
  [{:keys [path-params query-params]}]
  (let [{:keys [repo]} path-params
        {:keys [from to]} query-params]
    
    (try
      (let [repo-path (str "/repositories/" repo)
            repository (git/load-repo repo-path)
            from-commit (git-query/find-rev-commit repository from)
            to-commit (git-query/find-rev-commit repository to)
            
            ;; Simplified diff analysis
            diff-info {:from from
                       :to to
                       :files-changed 0
                       :additions 0
                       :deletions 0
                       :files []}]
        
        {:status 200
         :body diff-info})
      
      (catch Exception e
        (log/error e "Failed to analyze diff")
        {:status 500
         :body {:error "Failed to analyze diff"}}))))

(defn get-dependencies
  "Get repository dependencies and generate dependency graph"
  [{:keys [path-params query-params]}]
  (let [{:keys [repo]} path-params
        {:keys [branch]} (merge {:branch "main"} query-params)]
    
    {:status 200
     :body {:modules []
            :dependencies []}}))
