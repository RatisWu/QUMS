import os, sys
machine_IP_table = "/opt/UQMS/Server/Machines/MachineIP_rec.toml"

queue_folder = "/opt/UQMS/Server/Queues"
data_folder = "/opt/UQMS/Server/RawData"
user_dep_config_folder = f"/home/{os.getlogin()}/MeasConfigs"

for folder in [queue_folder,data_folder,user_dep_config_folder]:
    if not os.path.exists(folder):
        os.mkdir(folder)

