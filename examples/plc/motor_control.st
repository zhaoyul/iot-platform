PROGRAM MotorControl
VAR
    StartButton : BOOL;           (* 启动按钮 *)
    StopButton : BOOL;            (* 停止按钮 *)
    EmergencyStop : BOOL;         (* 急停 *)
    MotorRunning : BOOL;          (* 电机运行状态 *)
    MotorSpeed : INT;             (* 电机转速 *)
    Timer1 : TON;                 (* 定时器 *)
END_VAR

(* 主程序逻辑 *)
IF StartButton AND NOT EmergencyStop THEN
    MotorRunning := TRUE;
    MotorSpeed := 1500;  (* RPM *)
END_IF;

IF StopButton OR EmergencyStop THEN
    MotorRunning := FALSE;
    MotorSpeed := 0;
END_IF;

(* 定时器控制 *)
Timer1(IN := MotorRunning, PT := T#5s);

IF Timer1.Q THEN
    (* 5秒后执行的逻辑 *)
    MotorSpeed := MotorSpeed + 100;
END_IF;

END_PROGRAM
