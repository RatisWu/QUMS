import os
from Association.TrafficBureau import Queuer
from Association.Conductor import Executor
from Association.FBI import Canvasser
from Association.Housekeeper import Maid

Supervisor = Queuer()
items = Supervisor.QueueIn()
SampleName = Supervisor.sample_name

Worker = Executor(Supervisor.machine_system, items["Survey_path"], items["Config_path"])
raw_data_path = Worker.MeasWorkFlow()

gifts = Supervisor.QueueOut(raw_data_path)
Maid().save_process(gifts, SampleName)

