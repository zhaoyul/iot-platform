(ns iot-platform.core
  "Main entry point for IoT Platform backend service"
  (:require [reitit.ring :as ring]
            [ring.adapter.jetty :as jetty]
            [ring.middleware.json :refer [wrap-json-response wrap-json-body]]
            [ring.middleware.params :refer [wrap-params]]
            [taoensso.timbre :as log]
            [iot-platform.api.routes :as routes]
            [iot-platform.config :as config]
            [iot-platform.db :as db]
            [iot-platform.cache :as cache])
  (:gen-class))

(defn create-app
  "Create the Ring application with all middleware"
  [config]
  (ring/ring-handler
   (ring/router
    (routes/app-routes config)
    {:data {:middleware [wrap-params
                         wrap-json-body
                         wrap-json-response]}})
   (ring/create-default-handler)))

(defn start-server
  "Start the HTTP server"
  [{:keys [port] :as config}]
  (log/info "Starting IoT Platform server on port" port)
  (jetty/run-jetty (create-app config)
                   {:port port
                    :join? false}))

(defn -main
  "Main entry point"
  [& args]
  (let [config (config/load-config)]
    (log/info "Initializing database connection pool...")
    (db/init-db! config)
    
    (log/info "Initializing Redis cache...")
    (cache/init-cache! config)
    
    (log/info "Starting server...")
    (start-server config)
    
    (log/info "IoT Platform backend is running!")))
