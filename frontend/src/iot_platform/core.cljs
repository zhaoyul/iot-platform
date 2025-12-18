(ns iot-platform.core
  "Frontend application entry point"
  (:require [reagent.dom :as rdom]
            [re-frame.core :as rf]
            [iot-platform.events]
            [iot-platform.subs]
            [iot-platform.views.main :as main]))

(defn mount-root
  "Mount the root component"
  []
  (rf/clear-subscription-cache!)
  (rdom/render [main/main-view]
               (.getElementById js/document "app")))

(defn ^:export init
  "Initialize the application"
  []
  (rf/dispatch-sync [:initialize-db])
  (mount-root))
