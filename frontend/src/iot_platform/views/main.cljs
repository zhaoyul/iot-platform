(ns iot-platform.views.main
  "Main application view"
  (:require [reagent.core :as r]
            [re-frame.core :as rf]
            [iot-platform.components.dependency-graph :as dep-graph]
            [iot-platform.components.plc-visualizer :as plc-viz]
            [iot-platform.components.asset-list :as assets]))

(defn header
  "Application header"
  []
  [:header.app-header
   [:h1 "IoT Platform"]
   [:nav
    [:button {:on-click #(rf/dispatch [:set-active-view :home])} "Home"]
    [:button {:on-click #(rf/dispatch [:set-active-view :dependencies])} "Dependencies"]
    [:button {:on-click #(rf/dispatch [:set-active-view :plc])} "PLC Programs"]
    [:button {:on-click #(rf/dispatch [:set-active-view :assets])} "Assets"]]])

(defn home-view
  "Home page view"
  []
  [:div.home
   [:h2 "Welcome to IoT Platform"]
   [:p "Git-based management for heterogeneous industrial assets"]
   [:div.features
    [:div.feature
     [:h3 "Git Management"]
     [:p "Version control for all asset types"]]
    [:div.feature
     [:h3 "PLC Programs"]
     [:p "Parse and visualize industrial automation code"]]
    [:div.feature
     [:h3 "EDA Designs"]
     [:p "Manage electronic design files"]]
    [:div.feature
     [:h3 "Visualization"]
     [:p "Interactive dependency graphs and diagrams"]]]])

(defn main-view
  "Main application view with routing"
  []
  (let [current-view @(rf/subscribe [:current-view])
        loading? @(rf/subscribe [:loading?])]
    [:div.app-container
     [header]
     [:main.app-content
      (when loading?
        [:div.loading "Loading..."])
      (case current-view
        :home [home-view]
        :dependencies [dep-graph/dependency-graph-view]
        :plc [plc-viz/plc-visualizer-view]
        :assets [assets/asset-list-view]
        [home-view])]]))
