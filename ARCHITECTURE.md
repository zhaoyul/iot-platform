# IoT Platform - Clojure/ClojureScript架构

## 技术栈

**核心语言：** Clojure (后端) + ClojureScript (前端)

### 为什么选择 Clojure/ClojureScript？

1. **函数式编程范式** - 不可变数据、纯函数、易于测试
2. **JVM生态** - 访问Java库、优秀性能
3. **代码即数据** - 强大的宏系统、DSL构建
4. **前后端统一** - 共享代码和数据结构

## 系统架构

### 后端服务（Clojure）

**核心组件：**
- Ring + Reitit（Web框架）
- next.jdbc（数据库）
- Carmine（Redis）
- clj-jgit（Git操作）

**示例代码：**
```clojure
(ns iot-platform.git.handler
  (:require [clj-jgit.porcelain :as git]))

(defn analyze-commit [repo-path commit-hash]
  (let [repo (git/load-repo repo-path)
        commit (git-query/find-rev-commit repo commit-hash)]
    {:hash (.getName commit)
     :message (.getFullMessage commit)
     :author (-> commit .getAuthorIdent .getName)}))
```

### 前端应用（ClojureScript）

**核心组件：**
- Reagent（React封装）
- Re-frame（状态管理）
- Shadow-cljs（构建工具）

**示例代码：**
```clojure
(ns iot-platform.views.main
  (:require [reagent.core :as r]
            [re-frame.core :as rf]))

(defn main-view []
  (let [current-view @(rf/subscribe [:current-view])]
    [:div.app-container
     [header]
     [:main (case current-view
              :home [home-view]
              :dependencies [dependency-graph-view]
              :plc [plc-visualizer-view])]]))
```

## 资产管理

### PLC程序解析
```clojure
(defn parse-structured-text [content]
  (->> (str/split-lines content)
       (reduce (fn [acc line]
                 (cond
                   (str/starts-with? line "VAR")
                   (assoc acc :in-var true)
                   (str/starts-with? line "PROGRAM")
                   (update acc :programs conj (extract-program line))
                   :else acc))
               {:variables [] :programs []})))
```

### EDA设计解析
```clojure
(defn parse-kicad-schematic [content]
  (if (str/starts-with? content "(kicad_sch")
    {:tool "KiCad"
     :components (extract-components content)
     :nets (extract-nets content)}
    {:error "Invalid format"}))
```

## 部署

### Docker Compose
```yaml
services:
  backend:
    build: ./backend
    ports: ["8080:8080"]
  frontend:
    build: ./frontend
    ports: ["8081:80"]
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: backend
        image: iot-platform/backend:latest
        ports:
        - containerPort: 8080
```

## 安全

### 认证授权
```clojure
(defn generate-token [user]
  (jwt/sign {:user-id (:id user)
             :roles (:roles user)}
            secret-key))

(defn has-permission? [user permission resource]
  (or (contains? (get-permissions user) :all)
      (contains? (get-permissions user) permission)))
```

## 优势

1. **函数式编程** - 代码简洁、易维护
2. **不可变数据** - 并发安全
3. **REPL驱动开发** - 交互式开发
4. **前后端统一** - 技术栈一致

参考项目：https://github.com/RedCreationTech/front_backend_template
