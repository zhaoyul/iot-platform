(ns iot-platform.components.plc-visualizer
  "PLC ladder logic visualizer component"
  (:require [reagent.core :as r]
            [re-frame.core :as rf]))

(defn plc-visualizer-view
  "PLC ladder logic visualization"
  []
  [:div.plc-visualizer
   [:h2 "PLC Ladder Logic Diagram"]
   [:div.plc-controls
    [:input {:type "file" 
             :accept ".st,.ld"
             :on-change (fn [e]
                          (let [file (-> e .-target .-files (aget 0))
                                form-data (js/FormData.)]
                            (.append form-data "file" file)
                            (rf/dispatch [:upload-plc-program form-data])))}]
    [:button "Parse"]
    [:button "Validate"]]
   [:div.ladder-diagram
    [:svg {:width "100%" :height "600"}
     ;; Ladder logic rungs would be rendered here
     [:g
      ;; Power rails
      [:line {:x1 50 :y1 50 :x2 50 :y2 500 :stroke "black" :stroke-width 3}]
      [:line {:x1 750 :y1 50 :x2 750 :y2 500 :stroke "black" :stroke-width 3}]
      
      ;; Example rung
      [:g
       [:text {:x 100 :y 100 :font-size 14} "START_BTN"]
       [:rect {:x 150 :y 85 :width 60 :height 30 :fill "none" :stroke "green" :stroke-width 2}]
       [:text {:x 250 :y 100 :font-size 14} "MOTOR_RUN"]
       [:circle {:cx 700 :cy 100 :r 20 :fill "none" :stroke "orange" :stroke-width 2}]]]]]])
