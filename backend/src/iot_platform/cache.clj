(ns iot-platform.cache
  "Redis cache operations using Carmine"
  (:require [taoensso.carmine :as car]
            [taoensso.timbre :as log]))

(def ^:dynamic *redis-conn* nil)

(defmacro wcar*
  "Execute Redis commands with current connection"
  [& body]
  `(car/wcar *redis-conn* ~@body))

(defn init-cache!
  "Initialize Redis cache connection"
  [{:keys [redis]}]
  (let [conn {:pool {} 
              :spec {:host (:host redis)
                     :port (:port redis)}}]
    (alter-var-root #'*redis-conn* (constantly conn))
    (log/info "Redis cache initialized")))

(defn get-cached
  "Get value from cache"
  [key]
  (wcar* (car/get key)))

(defn set-cached
  "Set value in cache with optional TTL"
  ([key value]
   (wcar* (car/set key value)))
  ([key value ttl-seconds]
   (wcar* (car/setex key ttl-seconds value))))

(defn del-cached
  "Delete value from cache"
  [key]
  (wcar* (car/del key)))
