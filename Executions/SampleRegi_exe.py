import os
from Association.TrafficBureau import Queuer
from qblox_drive_AS.support.UserFriend import eyeson_print
from Association.FBI import Canvasser
from Association.Housekeeper import Maid

Supervisor = Queuer()
items = Supervisor.QueueIn() # 
SampleName = Supervisor.sample_name
MachineIP = Supervisor.machine_IP

Survey = Canvasser()
Survey.para_decoder(items["Survey_path"])
maid = Maid(Survey.assigned_paras, True)
for item in items:
    os.remove(items[item])

eyeson_print("Registeration done !")

