import os, sys
machine_IP_table = r"C:\ExpMachineIP\MachineIP_rec.toml"
IP_port_table = r"C:\ExpMachineIP\MachinePort_rec.toml"

queue_folder = r"C:\ExpQueue"
data_folder = r"C:\ExpData"
user_dep_config_folder = os.path.join(os.path.expanduser("~"),"MeasConfigs")

for folder in [queue_folder,data_folder,user_dep_config_folder]:
    if not os.path.exists(folder):
        os.mkdir(folder)