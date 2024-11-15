import os
from Association.TrafficBureau import Queuer
from Association.Conductor import Executor
from Association.FBI import Canvasser
from Association.Housekeeper import Maid
from qblox_drive_AS.support.UserFriend import *

Supervisor = Queuer()
Supervisor.QueueIn()
SampleName = Supervisor.sample_name

if not Supervisor.EnforcedQueueOut:
    Worker = Executor(Supervisor.machine_system, Supervisor.program_requirements["Survey_path"],  Supervisor.program_requirements["Config_path"])
    Worker.MeasWorkFlow()

    Supervisor.QueueOut()
    highlight_print("Measurement Complete! check the following path:")
    slightly_print(Supervisor.JOB_folder)

    

