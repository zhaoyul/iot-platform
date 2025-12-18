(ns iot-platform.components.asset-list
  "Asset list and management component"
  (:require [reagent.core :as r]
            [re-frame.core :as rf]))

(defn asset-item
  "Single asset item"
  [{:keys [id name type size hash]}]
  [:div.asset-item
   [:div.asset-name name]
   [:div.asset-type type]
   [:div.asset-size (str size " bytes")]
   [:div.asset-hash (subs hash 0 16)]
   [:div.asset-actions
    [:button "Download"]
    [:button "Delete"]]])

(defn asset-list-view
  "Asset list view"
  []
  (let [assets @(rf/subscribe [:assets])]
    [:div.asset-list
     [:h2 "Asset Management"]
     [:div.asset-upload
      [:h3 "Upload Asset"]
      [:input {:type "file"
               :on-change (fn [e]
                            (let [file (-> e .-target .-files (aget 0))
                                  form-data (js/FormData.)]
                              (.append form-data "file" file)
                              (.append form-data "asset-type" "binary")
                              (.append form-data "repository" "default")
                              (.append form-data "branch" "main")
                              (rf/dispatch [:upload-asset form-data])))}]
      [:button "Upload"]]
     [:div.assets
      (if (seq assets)
        (for [asset assets]
          ^{:key (:id asset)}
          [asset-item asset])
        [:p "No assets uploaded yet"])]]))
