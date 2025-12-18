(ns iot-platform.config
  "Configuration management using aero"
  (:require [aero.core :as aero]
            [clojure.java.io :as io]))

(defn load-config
  "Load configuration from resources/config.edn"
  []
  (aero/read-config (io/resource "config.edn")))
