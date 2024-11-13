
from Association.TrafficBureau import Queuer
from Association.Conductor import Executor

Supervisor = Queuer()
items = Supervisor.QueueIn()

Worker = Executor(Supervisor.machine_system, items["Survey_path"], items["Config_path"])
Worker.__ExpParasCollects__()