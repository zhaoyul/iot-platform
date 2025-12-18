(ns iot-platform.db
  "Database connection and operations"
  (:require [next.jdbc :as jdbc]
            [next.jdbc.connection :as connection]
            [hikari-cp.core :as hikari]
            [taoensso.timbre :as log])
  (:import [com.zaxxer.hikari HikariDataSource]))

(def ^:dynamic *db* nil)

(defn init-db!
  "Initialize database connection pool"
  [{:keys [database]}]
  (let [datasource-options {:adapter "postgresql"
                            :username (:user database)
                            :password (:password database)
                            :database-name (:name database)
                            :server-name (:host database)
                            :port-number (:port database)
                            :maximum-pool-size 10}
        datasource (hikari/make-datasource datasource-options)]
    (alter-var-root #'*db* (constantly {:datasource datasource}))
    (log/info "Database connection pool initialized")))

(defn execute!
  "Execute a SQL query"
  [sql-vec]
  (jdbc/execute! *db* sql-vec))

(defn execute-one!
  "Execute a SQL query and return one result"
  [sql-vec]
  (jdbc/execute-one! *db* sql-vec))
