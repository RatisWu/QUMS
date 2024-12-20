import traceback
from Association.TrafficBureau import Queuer
from Association.Conductor import Executor
from qblox_drive_AS.support.UserFriend import *

beta_test:bool = 0       # bypass connecting to machine 

Supervisor = Queuer()
Supervisor.QueueIn()

try:
    if not Supervisor.EnforcedQueueOut:
        SampleName = Supervisor.sample_name
        EXP_tag = Supervisor.exp_type
        slightly_print(f"{EXP_tag} executing ...")
        Worker = Executor(Supervisor.machine_system, Supervisor.program_requirements["Survey_path"], Supervisor.program_requirements["Config_path"], Supervisor.program_requirements["Script_path"])
        Worker.MeasWorkFlow(beta_test)
        if beta_test:
            Supervisor.QueueOutUrgently()
        else:
            items = Supervisor.QueueOut() # {"Data":[paths], "Config":path/to/folder}
            Worker.__ExpResultsAnalyzes__(ana_need_items=items)

            highlight_print(f"Measurement Complete! data in the dir: {Supervisor.JOB_folder}")

except BaseException as err:
    if EXP_tag not in ["A1","A2"]:
        if Supervisor.InQueueMark:
            Supervisor.QueueOutUrgently()
            warning_print(f"When executed the requests got the error: {err}")
            traceback.print_exc()
        else:
            traceback.print_exc()
            eyeson_print("This error is caught after queue out.")

    else:
        items = Supervisor.QueueOut()
        print(f"{EXP_tag} measurement had been manually closed and normally queued out !")
    
    
    

