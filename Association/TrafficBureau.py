import os, sys, tomli, random, shutil
from Association.Roads import machine_IP_table, queue_folder, user_dep_config_folder
from Association.ExclusiveNames import SurveyUniqueName, ConfigUniqueName


class Queuer():
    def __init__(self):
        self.__CheckAllQueues__()

    def __JobIDAssigner__(self):
        self.JOBID:str = '{:08x}'.format(random.randint(0,0xFFFFFFFF))

    def __CheckAllQueues__(self):
        with open(machine_IP_table, "rb") as file:
            self.ip_table = tomli.load(file)
        
        for machine_queue in [os.path.join(queue_folder,ip.replace(".","_")) for ip, _ in self.ip_table.items()]:
            if not os.path.exists(machine_queue):
                os.mkdir(machine_queue)
    
    def __TouchConfigNPara__(self)->dict:
        Config = [os.path.join(user_dep_config_folder,name) for name in os.listdir(user_dep_config_folder) if (os.path.isdir(os.path.join(user_dep_config_folder,name)) and ConfigUniqueName.lower() in name.lower())][0]
        Survey = [os.path.join(user_dep_config_folder,name) for name in os.listdir(user_dep_config_folder) if (os.path.isfile(os.path.join(user_dep_config_folder,name)) and SurveyUniqueName in name and name.split(".")[-1] == 'toml')][0]
        self.Requirements:dict = {"Config_path":Config,"Survey_path":Survey}
    
    def __JOBIDLabels__(self):
        with open(self.Requirements["Survey_path"], "rb") as file:
            para_setting = tomli.load(file)

        IP:str = str(para_setting["machine_IP"]).replace(" ","")
        self.machine_system:str = self.ip_table[IP]
        self.queue:str = os.path.join(queue_folder,IP.replace(".","_"))

        self.__JobIDAssigner__()


    def QueueIn(self):
        # step_1 get in touch with the required data, ExpConfigs folder and ExpParasSurvey.toml are included
        self.__TouchConfigNPara__()

        # step_2 Get JOB_ID for this EXP request
        self.__JOBIDLabels__()

        # step_3 Rename the requirements and move it into queue folder according to the machine address.
        program_requirements = {}
        for requirement in self.Requirements:
            match requirement:
                case "Config_path":
                    JOBID_labeled_name = f"{os.path.split(self.Requirements['Config_path'])[-1]}_{self.JOBID}"
                case _:
                    JOBID_labeled_name = f"{os.path.split(self.Requirements['Survey_path'])[-1].split('.')[0]}_{self.JOBID}.toml"

            shutil.move(self.Requirements[requirement],os.path.join(self.queue,JOBID_labeled_name))
            program_requirements[requirement] = os.path.join(self.queue,JOBID_labeled_name)
        
        return program_requirements

    def QueueOut(self,raw_data_path:str=None):
        pass


    
    

if __name__ == "__main__":
    Officer = Queuer()
    items = Officer.QueueIn()

