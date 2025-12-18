(ns iot-platform.subs
  "Re-frame subscriptions"
  (:require [re-frame.core :as rf]))

(rf/reg-sub
 :current-view
 (fn [db _]
   (:current-view db)))

(rf/reg-sub
 :loading?
 (fn [db _]
   (:loading db)))

(rf/reg-sub
 :repositories
 (fn [db _]
   (:repositories db)))

(rf/reg-sub
 :assets
 (fn [db _]
   (:assets db)))

(rf/reg-sub
 :plc-programs
 (fn [db _]
   (:plc-programs db)))

(rf/reg-sub
 :error
 (fn [db _]
   (:error db)))
