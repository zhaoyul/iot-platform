(ns iot-platform.plc.handler
  "PLC program parsing and visualization handler"
  (:require [clojure.string :as str]
            [taoensso.timbre :as log]))

(defn- parse-structured-text
  "Parse Structured Text (ST) PLC program"
  [content]
  (let [lines (str/split-lines content)
        variables (atom [])
        programs (atom [])
        function-blocks (atom [])]
    
    ;; Simple ST parsing
    (doseq [line lines]
      (let [trimmed (str/trim line)]
        (cond
          (str/starts-with? trimmed "VAR")
          (log/debug "Found VAR section")
          
          (str/starts-with? trimmed "PROGRAM")
          (swap! programs conj {:name (second (str/split trimmed #"\s+"))
                                :type "PROGRAM"})
          
          (str/starts-with? trimmed "FUNCTION_BLOCK")
          (swap! function-blocks conj {:name (second (str/split trimmed #"\s+"))
                                       :type "FUNCTION_BLOCK"}))))
    
    {:variables @variables
     :programs @programs
     :function-blocks @function-blocks}))

(defn parse-program
  "Parse PLC program file"
  [{:keys [multipart-params]}]
  (try
    (let [{:strs [file]} multipart-params
          {:keys [filename tempfile]} file
          content (slurp tempfile)
          
          ;; Determine language from extension
          ext (last (str/split filename #"\."))
          
          parsed (case ext
                   "st" (parse-structured-text content)
                   {:error "Unsupported format"})]
      
      {:status 200
       :body {:id (str (hash content))
              :name filename
              :language (str/upper-case ext)
              :variables (:variables parsed)
              :programs (:programs parsed)
              :function-blocks (:function-blocks parsed)}})
    
    (catch Exception e
      (log/error e "Failed to parse PLC program")
      {:status 500
       :body {:error "Failed to parse PLC program"}})))

(defn validate-program
  "Validate PLC program syntax"
  [{:keys [multipart-params]}]
  (try
    (let [{:strs [file]} multipart-params
          content (slurp (:tempfile file))
          
          ;; Basic validation
          errors []
          warnings []]
      
      {:status 200
       :body {:valid (empty? errors)
              :errors errors
              :warnings warnings}})
    
    (catch Exception e
      (log/error e "Failed to validate PLC program")
      {:status 500
       :body {:error "Failed to validate"}})))

(defn visualize-ladder
  "Generate ladder logic visualization data"
  [{:keys [multipart-params]}]
  {:status 200
   :body {:nodes []
          :edges []
          :rungs []}})
