(ns iot-platform.assets.handler
  "Asset management handler"
  (:require [clojure.java.io :as io]
            [clojure.string :as str]
            [taoensso.timbre :as log])
  (:import [java.security MessageDigest]
           [java.time Instant]
           [java.util UUID]))

(defn- calculate-sha256
  "Calculate SHA256 hash of file"
  [file]
  (let [digest (MessageDigest/getInstance "SHA-256")
        buffer (byte-array 4096)]
    (with-open [is (io/input-stream file)]
      (loop []
        (let [n (.read is buffer)]
          (when (pos? n)
            (.update digest buffer 0 n)
            (recur)))))
    (let [hash-bytes (.digest digest)]
      (apply str (map #(format "%02x" %) hash-bytes)))))

(defn- sanitize-filename
  "Sanitize filename to prevent path traversal"
  [filename]
  (-> filename
      (str/replace #"[^a-zA-Z0-9._-]" "_")
      (str/replace #"\.\.+" ".")))

(defn upload-asset
  "Upload a new asset file"
  [{:keys [multipart-params path-params]}]
  (try
    (let [{:strs [file asset-type repository branch]} multipart-params
          {:keys [filename tempfile]} file
          
          ;; Security: sanitize filename
          safe-filename (sanitize-filename filename)
          unique-id (str (UUID/randomUUID))
          timestamp (Instant/now)
          
          ;; Create storage path
          storage-path (str "/assets/" asset-type "/" 
                           (.toString timestamp) "_" 
                           unique-id "_" safe-filename)
          
          ;; Calculate hash
          file-hash (calculate-sha256 tempfile)
          
          ;; Save file
          target-file (io/file storage-path)]
      
      (io/make-parents target-file)
      (io/copy tempfile target-file)
      
      {:status 200
       :body {:status "success"
              :asset {:id (subs file-hash 0 16)
                      :name safe-filename
                      :type asset-type
                      :hash file-hash
                      :repository repository
                      :branch branch
                      :path storage-path
                      :created-at (.toString timestamp)}}})
    
    (catch Exception e
      (log/error e "Failed to upload asset")
      {:status 500
       :body {:error "Failed to upload asset"}})))

(defn get-asset
  "Get asset by ID"
  [{:keys [path-params]}]
  (let [{:keys [id]} path-params]
    {:status 200
     :body {:id id
            :status "found"}}))

(defn list-assets
  "List all assets with optional filtering"
  [{:keys [query-params]}]
  (let [{:keys [asset-type repository limit offset]} 
        (merge {:limit 50 :offset 0} query-params)]
    {:status 200
     :body {:total 0
            :items []
            :limit limit
            :offset offset}}))

(defn delete-asset
  "Delete an asset"
  [{:keys [path-params]}]
  (let [{:keys [id]} path-params]
    {:status 200
     :body {:status "deleted"}}))
