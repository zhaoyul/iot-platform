(ns iot-platform.events
  "Re-frame events"
  (:require [re-frame.core :as rf]
            [ajax.core :as ajax]))

(rf/reg-event-db
 :initialize-db
 (fn [_ _]
   {:current-view :home
    :repositories []
    :assets []
    :plc-programs []
    :loading false}))

(rf/reg-event-db
 :set-active-view
 (fn [db [_ view]]
   (assoc db :current-view view)))

(rf/reg-event-db
 :set-loading
 (fn [db [_ loading?]]
   (assoc db :loading loading?)))

;; Fetch repositories
(rf/reg-event-fx
 :fetch-repositories
 (fn [{:keys [db]} _]
   {:db (assoc db :loading true)
    :http-xhrio {:method :get
                 :uri "/api/v1/repos"
                 :response-format (ajax/json-response-format {:keywords? true})
                 :on-success [:fetch-repositories-success]
                 :on-failure [:fetch-repositories-failure]}}))

(rf/reg-event-db
 :fetch-repositories-success
 (fn [db [_ response]]
   (-> db
       (assoc :repositories response)
       (assoc :loading false))))

(rf/reg-event-db
 :fetch-repositories-failure
 (fn [db [_ error]]
   (-> db
       (assoc :error error)
       (assoc :loading false))))

;; Upload asset
(rf/reg-event-fx
 :upload-asset
 (fn [{:keys [db]} [_ form-data]]
   {:db (assoc db :loading true)
    :http-xhrio {:method :post
                 :uri "/api/v1/assets"
                 :body form-data
                 :response-format (ajax/json-response-format {:keywords? true})
                 :on-success [:upload-asset-success]
                 :on-failure [:upload-asset-failure]}}))

(rf/reg-event-db
 :upload-asset-success
 (fn [db [_ response]]
   (-> db
       (update :assets conj (:asset response))
       (assoc :loading false))))

(rf/reg-event-db
 :upload-asset-failure
 (fn [db [_ error]]
   (-> db
       (assoc :error error)
       (assoc :loading false))))
