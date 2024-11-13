import os, sys, tomli, random, shutil, json
from Association.Roads import machine_IP_table, queue_folder, user_dep_config_folder
from Association.ExclusiveNames import SurveyUniqueName, ConfigUniqueName, IdentityUniqueName
from Association.Housekeeper import Maid

class Queuer():
    def __init__(self):
        self.__CheckAllQueues__()

    def __JobIDAssigner__(self):
        self.JOBID:str = '{:08x}'.format(random.randint(0,0xFFFFFFFF))
    
    def __interchanges__(self):
        """ Reject the request into queue"""
        return self.Requirements


    def __CheckAllQueues__(self):
        with open(machine_IP_table, "rb") as file:
            self.ip_table = tomli.load(file)
        
        for machine_queue in [os.path.join(queue_folder,ip.replace(".","_")) for ip, _ in self.ip_table.items()]:
            if not os.path.exists(machine_queue):
                os.mkdir(machine_queue)
    
    def __TouchConfigNPara__(self)->dict:
        Config = [os.path.join(user_dep_config_folder,name) for name in os.listdir(user_dep_config_folder) if (os.path.isdir(os.path.join(user_dep_config_folder,name)) and ConfigUniqueName.lower() in name.lower())]
        Survey = [os.path.join(user_dep_config_folder,name) for name in os.listdir(user_dep_config_folder) if (os.path.isfile(os.path.join(user_dep_config_folder,name)) and SurveyUniqueName in name and name.split(".")[-1] == 'toml')][0]
        Identity = [os.path.join(user_dep_config_folder,name) for name in os.listdir(user_dep_config_folder) if (os.path.isfile(os.path.join(user_dep_config_folder,name)) and IdentityUniqueName == name.split(".")[0])][0]
        
        if os.path.split(Survey)[-1].split("_")[0].upper() == "S0":
            self.Requirements:dict = {"Survey_path":Survey,"ID_path":Identity}
        else:
            if len(Config) >= 1:
                self.Requirements:dict = {"Config_path":Config[0],"Survey_path":Survey,"ID_path":Identity}
            else:
                raise ValueError("Can't see any ExpConfigs folder")
    
    def __JOBIDLabels__(self):
        with open(self.Requirements["ID_path"], "r") as file:
            ID_card = json.load(file)

        self.sample_name = ID_card["Sample Name"].replace(" ","")
        self.machine_IP = ID_card["Machine Address"].replace(" ","")
            
        self.machine_system:str = self.ip_table[self.machine_IP]
        self.queue:str = os.path.join(queue_folder,self.machine_IP)

        self.__JobIDAssigner__()


    def QueueIn(self):
        # step_1 get in touch with the required data, ExpConfigs folder and ExpParasSurvey.toml are included
        self.__TouchConfigNPara__()

        # step_2 Get JOB_ID for this EXP request
        self.__JOBIDLabels__()

        # step_3 Rename the requirements and move it into queue folder according to the machine address.
        program_requirements = {}
        if "Config_path" in self.Requirements:
            for requirement in self.Requirements:
                match requirement:
                    case "Config_path":
                        JOBID_labeled_name = f"{os.path.split(self.Requirements['Config_path'])[-1]}_{self.JOBID}"
                    case _:
                        JOBID_labeled_name = f"{os.path.split(self.Requirements['Survey_path'])[-1].split('.')[0]}_{self.JOBID}.toml"

                shutil.move(self.Requirements[requirement],os.path.join(self.queue,JOBID_labeled_name))
                program_requirements[requirement] = os.path.join(self.queue,JOBID_labeled_name)
        else:
            program_requirements = self.__interchanges__()
        
        return program_requirements

    def QueueOut(self,raw_data_path:str=None)->dict:
        pass




    
    

if __name__ == "__main__":
    Officer = Queuer()
    items = Officer.QueueIn()

