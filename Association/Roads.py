import os, sys
machine_IP_table = "/home/UQMS/Server/ExpMachineIP/MachineIP_rec.toml"

queue_folder = "/home/UQMS/Server/ExpQueue"
data_folder = "/home/UQMS/Server/ExpData"
user_dep_config_folder = os.path.join(os.path.expanduser("~"),"MeasConfigs")

for folder in [queue_folder,data_folder,user_dep_config_folder]:
    if not os.path.exists(folder):
        os.mkdir(folder)

