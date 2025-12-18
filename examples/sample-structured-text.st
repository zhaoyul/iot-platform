PROGRAM ProductionControl
(* Example IEC 61131-3 Structured Text Program *)
(* Production line control with recipe management *)

VAR
    (* Input Variables *)
    Start_Button : BOOL;           (* Start production button *)
    Stop_Button : BOOL;            (* Stop production button *)
    Emergency_Stop : BOOL;         (* Emergency stop input *)
    Part_Present : BOOL;           (* Part detection sensor *)
    Temperature_PV : REAL;         (* Temperature process value *)
    Pressure_PV : REAL;            (* Pressure process value *)
    
    (* Output Variables *)
    Motor_Run : BOOL;              (* Motor run command *)
    Heater_Enable : BOOL;          (* Heater enable *)
    Alarm_Light : BOOL;            (* Alarm indicator *)
    
    (* Internal Variables *)
    Production_State : INT := 0;   (* State machine: 0=Idle, 1=Running, 2=Fault *)
    Cycle_Counter : DINT := 0;     (* Production cycle counter *)
    Fault_Code : INT := 0;         (* Active fault code *)
    
    (* Recipe Parameters *)
    Recipe_Temp_SP : REAL := 75.0; (* Temperature setpoint *)
    Recipe_Pressure_SP : REAL := 5.0; (* Pressure setpoint *)
    Recipe_Time : TIME := T#30s;   (* Cycle time *)
    
    (* Timers *)
    Cycle_Timer : TON;             (* Production cycle timer *)
    Fault_Delay : TOF;             (* Fault delay timer *)
    
    (* PID Controller *)
    Temp_PID : PID_Controller;     (* Temperature PID *)
END_VAR

(* Main Program Logic *)

(* Emergency Stop Handling *)
IF Emergency_Stop THEN
    Production_State := 2;  (* Fault state *)
    Fault_Code := 100;      (* Emergency stop fault *)
    Motor_Run := FALSE;
    Heater_Enable := FALSE;
    Alarm_Light := TRUE;
    RETURN;
END_IF;

(* State Machine *)
CASE Production_State OF
    
    0: (* Idle State *)
        Motor_Run := FALSE;
        Heater_Enable := FALSE;
        Alarm_Light := FALSE;
        Cycle_Counter := 0;
        
        (* Start condition *)
        IF Start_Button AND NOT Stop_Button THEN
            Production_State := 1;
        END_IF;
    
    1: (* Running State *)
        Motor_Run := TRUE;
        
        (* Temperature Control *)
        Temp_PID.SetPoint := Recipe_Temp_SP;
        Temp_PID.ProcessValue := Temperature_PV;
        Temp_PID.Execute := TRUE;
        
        Heater_Enable := Temp_PID.Output > 0.0;
        
        (* Cycle Timer *)
        Cycle_Timer(IN := Part_Present, PT := Recipe_Time);
        
        IF Cycle_Timer.Q THEN
            Cycle_Counter := Cycle_Counter + 1;
            Cycle_Timer(IN := FALSE);  (* Reset timer *)
        END_IF;
        
        (* Fault Detection *)
        IF Temperature_PV > (Recipe_Temp_SP + 10.0) THEN
            Production_State := 2;
            Fault_Code := 201;  (* Temperature high fault *)
        ELSIF Pressure_PV > (Recipe_Pressure_SP + 2.0) THEN
            Production_State := 2;
            Fault_Code := 202;  (* Pressure high fault *)
        END_IF;
        
        (* Stop condition *)
        IF Stop_Button THEN
            Production_State := 0;
        END_IF;
    
    2: (* Fault State *)
        Motor_Run := FALSE;
        Heater_Enable := FALSE;
        Alarm_Light := TRUE;
        
        (* Fault handling with delay *)
        Fault_Delay(IN := TRUE, PT := T#5s);
        
        (* Fault reset condition *)
        IF Fault_Delay.Q AND NOT Emergency_Stop THEN
            IF Start_Button THEN
                Production_State := 0;
                Fault_Code := 0;
                Fault_Delay(IN := FALSE);  (* Reset delay *)
            END_IF;
        END_IF;
        
END_CASE;

(* Safety Interlocks *)
IF Temperature_PV > 100.0 OR Pressure_PV > 10.0 THEN
    (* Critical fault - immediate shutdown *)
    Motor_Run := FALSE;
    Heater_Enable := FALSE;
    Production_State := 2;
    Fault_Code := 999;  (* Critical safety fault *)
END_IF;

END_PROGRAM


FUNCTION_BLOCK PID_Controller
(* Simple PID Controller *)
VAR_INPUT
    SetPoint : REAL;        (* Desired value *)
    ProcessValue : REAL;    (* Measured value *)
    Execute : BOOL;         (* Enable PID *)
END_VAR

VAR_OUTPUT
    Output : REAL;          (* Control output 0-100% *)
END_VAR

VAR
    Error : REAL;           (* Error term *)
    Integral : REAL := 0.0; (* Integral term *)
    Derivative : REAL;      (* Derivative term *)
    LastError : REAL := 0.0;(* Previous error *)
    
    (* PID Gains *)
    Kp : REAL := 2.0;       (* Proportional gain *)
    Ki : REAL := 0.5;       (* Integral gain *)
    Kd : REAL := 0.1;       (* Derivative gain *)
    
    dt : REAL := 0.1;       (* Sample time in seconds *)
END_VAR

IF Execute THEN
    (* Calculate error *)
    Error := SetPoint - ProcessValue;
    
    (* Integral term with anti-windup *)
    Integral := Integral + (Error * dt);
    IF Integral > 100.0 THEN
        Integral := 100.0;
    ELSIF Integral < 0.0 THEN
        Integral := 0.0;
    END_IF;
    
    (* Derivative term *)
    Derivative := (Error - LastError) / dt;
    
    (* PID output *)
    Output := (Kp * Error) + (Ki * Integral) + (Kd * Derivative);
    
    (* Clamp output *)
    IF Output > 100.0 THEN
        Output := 100.0;
    ELSIF Output < 0.0 THEN
        Output := 0.0;
    END_IF;
    
    (* Save error for next cycle *)
    LastError := Error;
ELSE
    Output := 0.0;
    Integral := 0.0;
    LastError := 0.0;
END_IF;

END_FUNCTION_BLOCK
