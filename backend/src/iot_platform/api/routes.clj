(ns iot-platform.api.routes
  "API route definitions"
  (:require [iot-platform.git.handler :as git]
            [iot-platform.assets.handler :as assets]
            [iot-platform.plc.handler :as plc]
            [iot-platform.eda.handler :as eda]))

(defn app-routes
  "Define all application routes"
  [config]
  [["/api"
    ["/v1"
     ["/health" {:get {:handler (fn [_] {:status 200 
                                          :body {:status "healthy" 
                                                 :service "iot-platform"}})}}]
     
     ;; Git operations
     ["/repos/:repo"
      ["/commits/:hash" {:get git/get-commit}]
      ["/diff" {:get git/analyze-diff}]
      ["/dependencies" {:get git/get-dependencies}]]
     
     ;; Asset management
     ["/assets"
      ["" {:get assets/list-assets
           :post assets/upload-asset}]
      ["/:id" {:get assets/get-asset
               :delete assets/delete-asset}]]
     
     ;; PLC operations
     ["/plc"
      ["/parse" {:post plc/parse-program}]
      ["/validate" {:post plc/validate-program}]
      ["/visualize" {:post plc/visualize-ladder}]]
     
     ;; EDA operations
     ["/eda"
      ["/parse" {:post eda/parse-design}]
      ["/validate" {:post eda/validate-design}]
      ["/diff" {:post eda/compare-designs}]]]]])
