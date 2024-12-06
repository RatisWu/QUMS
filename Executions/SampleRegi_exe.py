import os, json
from Association.TrafficBureau import Queuer
from Association.Roads import user_dep_config_folder
from qblox_drive_AS.support.UserFriend import eyeson_print, slightly_print
from Association.FBI import Canvasser
from Association.Housekeeper import Maid

Supervisor = Queuer()
items = Supervisor.QueueIn() # 
SampleName = Supervisor.sample_name
MachineIP = Supervisor.machine_IP

Survey = Canvasser()
Survey.para_decoder(items["Survey_path"])

whodowhat = {
    "Sample Name":SampleName,
    "Machine Address":MachineIP 
}

maid = Maid(Survey.assigned_paras, True)
for item in items:
    os.remove(items[item])

slightly_print("Creating the meas ID card ...")
path = os.path.join(user_dep_config_folder,'WhoDoWhat.json')
with open(path, "w") as file:
    json.dump(whodowhat, file, indent=4)

eyeson_print("Registeration done !")

