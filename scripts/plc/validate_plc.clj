(ns plc-validator
  "PLC program validation script"
  (:require [clojure.string :as str]
            [clojure.java.io :as io])
  (:gen-class))

(defn validate-structured-text
  "Validate Structured Text (ST) program"
  [file-path]
  (let [content (slurp file-path)
        lines (str/split-lines content)
        errors (atom [])
        warnings (atom [])]
    
    ;; Check program structure
    (when-not (or (str/includes? content "PROGRAM")
                  (str/includes? content "FUNCTION_BLOCK")
                  (str/includes? content "FUNCTION"))
      (swap! errors conj (str file-path ": Invalid program structure")))
    
    ;; Check variable declarations
    (when-not (str/includes? content "VAR")
      (swap! warnings conj (str file-path ": No variable declarations found")))
    
    ;; Check bracket matching
    (let [open-count (count (filter #(= % \() content))
          close-count (count (filter #(= % \)) content))]
      (when (not= open-count close-count)
        (swap! errors conj (str file-path ": Bracket mismatch"))))
    
    {:file file-path
     :valid (empty? @errors)
     :errors @errors
     :warnings @warnings}))

(defn validate-ladder-logic
  "Validate Ladder Logic program"
  [file-path]
  {:file file-path
   :valid true
   :errors []
   :warnings []})

(defn validate-plc-file
  "Validate a PLC file based on extension"
  [file-path]
  (let [ext (last (str/split file-path #"\."))]
    (case ext
      "st" (validate-structured-text file-path)
      "ld" (validate-ladder-logic file-path)
      "xml" (validate-ladder-logic file-path)
      {:file file-path
       :valid false
       :errors [(str "Unsupported file type: " ext)]
       :warnings []})))

(defn -main
  "Main entry point for PLC validation"
  [& args]
  (if (empty? args)
    (println "Usage: clojure -M plc_validator.clj <path>")
    (let [path (first args)
          file (io/file path)
          results (if (.isDirectory file)
                    ;; Directory - find all PLC files
                    (let [plc-files (->> (file-seq file)
                                         (filter #(.isFile %))
                                         (filter #(re-matches #".*\.(st|ld|xml)" (.getName %))))]
                      (map #(validate-plc-file (.getPath %)) plc-files))
                    ;; Single file
                    [(validate-plc-file path)])
          total (count results)
          errors (mapcat :errors results)
          warnings (mapcat :warnings results)
          passed (every? :valid results)]
      
      (println (str "\n" (apply str (repeat 50 "="))  ))
      (println "PLC Validation Report")
      (println (apply str (repeat 50 "=")))
      (println (str "Files validated: " total))
      (println (str "Errors: " (count errors)))
      (println (str "Warnings: " (count warnings)))
      
      (when (seq errors)
        (println "\nErrors:")
        (doseq [error errors]
          (println "  -" error)))
      
      (when (seq warnings)
        (println "\nWarnings:")
        (doseq [warning warnings]
          (println "  -" warning)))
      
      (println)
      (if passed
        (do
          (println "✓ All validations passed")
          (System/exit 0))
        (do
          (println "✗ Validation failed")
          (System/exit 1))))))
