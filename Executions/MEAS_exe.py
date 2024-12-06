import os, traceback
from Association.TrafficBureau import Queuer
from Association.Conductor import Executor
from Association.FBI import Canvasser
from Association.Housekeeper import Maid
from qblox_drive_AS.support.UserFriend import *

beta_test:bool = 0       # bypass connecting to machine 

Supervisor = Queuer()
Supervisor.QueueIn()
SampleName = Supervisor.sample_name
EXP_tag = Supervisor.exp_type
slightly_print(f"{EXP_tag} executing ...")
try:
    if not Supervisor.EnforcedQueueOut:
        Worker = Executor(Supervisor.machine_system, Supervisor.program_requirements["Survey_path"],  Supervisor.program_requirements["Config_path"])
        Worker.MeasWorkFlow(beta_test)
        if beta_test:
            Supervisor.QueueOutUrgently()
        else:
            # qm analyze then queue out
            if Supervisor.machine_system.lower() == 'qm':
                Worker.__ExpResultsAnalyzes__()
            items = Supervisor.QueueOut()
            # qblox queue out then analyze 
            if Supervisor.machine_system.lower() == 'qblox':
                Worker.__ExpResultsAnalyzes__(ana_need_items=items)
            highlight_print(f"Measurement Complete! check the JobID: {Supervisor.readableJOBID}")

except BaseException as err:
    if EXP_tag not in ["A1","A2"]:
        Supervisor.QueueOutUrgently()
        warning_print(f"When executed the requests got the error: {err}")
    else:
        items = Supervisor.QueueOut()
        print(f"{EXP_tag} measurement had been manually closed and normally queued out !")
    
    traceback.print_exc()

    

