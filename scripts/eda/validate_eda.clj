(ns eda-validator
  "EDA design file validation script"
  (:require [clojure.string :as str]
            [clojure.java.io :as io])
  (:gen-class))

(defn validate-kicad-schematic
  "Validate KiCad schematic file"
  [file-path]
  (let [content (slurp file-path)
        errors (atom [])
        warnings (atom [])]
    
    ;; Check file format
    (when-not (str/starts-with? content "(kicad_sch")
      (swap! errors conj (str file-path ": Not a valid KiCad schematic file")))
    
    ;; Check for required fields
    (doseq [field ["version" "symbol" "sheet"]]
      (when-not (str/includes? content field)
        (swap! warnings conj (str file-path ": Missing recommended field '" field "'"))))
    
    {:file file-path
     :valid (empty? @errors)
     :errors @errors
     :warnings @warnings}))

(defn validate-kicad-pcb
  "Validate KiCad PCB file"
  [file-path]
  (let [content (slurp file-path)
        errors (atom [])
        warnings (atom [])]
    
    ;; Check file format
    (when-not (str/starts-with? content "(kicad_pcb")
      (swap! errors conj (str file-path ": Not a valid KiCad PCB file")))
    
    ;; Check for layers
    (when-not (str/includes? content "layers")
      (swap! errors conj (str file-path ": No layers defined")))
    
    ;; Check for copper layers
    (when-not (or (str/includes? content "F.Cu")
                  (str/includes? content "B.Cu"))
      (swap! warnings conj (str file-path ": No copper layers found")))
    
    {:file file-path
     :valid (empty? @errors)
     :errors @errors
     :warnings @warnings}))

(defn validate-gerber
  "Validate Gerber file"
  [file-path]
  (let [content (slurp file-path)
        warnings (atom [])]
    
    (when-not (or (str/includes? content "%FSLAX")
                  (str/includes? content "G04"))
      (swap! warnings conj (str file-path ": May not be a valid Gerber file")))
    
    {:file file-path
     :valid true
     :errors []
     :warnings @warnings}))

(defn validate-eda-file
  "Validate an EDA file based on extension"
  [file-path]
  (let [name (.getName (io/file file-path))
        ext (last (str/split name #"\."))]
    (cond
      (= ext "kicad_sch") (validate-kicad-schematic file-path)
      (= ext "kicad_pcb") (validate-kicad-pcb file-path)
      (contains? #{"gbr" "gko"} ext) (validate-gerber file-path)
      :else {:file file-path
             :valid false
             :errors [(str "Unsupported file type: " ext)]
             :warnings []})))

(defn -main
  "Main entry point for EDA validation"
  [& args]
  (if (empty? args)
    (println "Usage: clojure -M eda_validator.clj <path>")
    (let [path (first args)
          file (io/file path)
          results (if (.isDirectory file)
                    ;; Directory - find all EDA files
                    (let [eda-files (->> (file-seq file)
                                         (filter #(.isFile %))
                                         (filter #(re-matches #".*\.(kicad_sch|kicad_pcb|gbr|gko|brd|sch)" 
                                                             (.getName %))))]
                      (map #(validate-eda-file (.getPath %)) eda-files))
                    ;; Single file
                    [(validate-eda-file path)])
          total (count results)
          errors (mapcat :errors results)
          warnings (mapcat :warnings results)
          passed (every? :valid results)]
      
      (println (str "\n" (apply str (repeat 50 "="))))
      (println "EDA Validation Report")
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
