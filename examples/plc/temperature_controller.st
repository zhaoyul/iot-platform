FUNCTION_BLOCK TemperatureController
VAR_INPUT
    CurrentTemp : REAL;           (* 当前温度 *)
    SetPoint : REAL;              (* 设定点 *)
    Enable : BOOL;                (* 使能 *)
END_VAR

VAR_OUTPUT
    HeaterOn : BOOL;              (* 加热器开关 *)
    CoolerOn : BOOL;              (* 冷却器开关 *)
    Alarm : BOOL;                 (* 报警 *)
END_VAR

VAR
    Hysteresis : REAL := 2.0;     (* 回差 *)
    MaxTemp : REAL := 100.0;      (* 最高温度 *)
    MinTemp : REAL := 0.0;        (* 最低温度 *)
END_VAR

(* 温度控制逻辑 *)
IF Enable THEN
    (* 检查温度范围 *)
    IF CurrentTemp > MaxTemp OR CurrentTemp < MinTemp THEN
        Alarm := TRUE;
        HeaterOn := FALSE;
        CoolerOn := FALSE;
    ELSE
        Alarm := FALSE;
        
        (* PID控制（简化版） *)
        IF CurrentTemp < (SetPoint - Hysteresis) THEN
            HeaterOn := TRUE;
            CoolerOn := FALSE;
        ELSIF CurrentTemp > (SetPoint + Hysteresis) THEN
            HeaterOn := FALSE;
            CoolerOn := TRUE;
        ELSE
            (* 在死区内保持当前状态 *)
        END_IF;
    END_IF;
ELSE
    HeaterOn := FALSE;
    CoolerOn := FALSE;
    Alarm := FALSE;
END_IF;

END_FUNCTION_BLOCK
