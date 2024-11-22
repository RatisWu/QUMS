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

except Exception as err:
    Supervisor.QueueOutUrgently()
    warning_print(f"When executed the requests got the error: {err}")
    traceback.print_exc()

    

