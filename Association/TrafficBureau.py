import os, sys, tomli, random, shutil, json
from datetime import datetime
from Association.Roads import machine_IP_table, queue_folder, user_dep_config_folder, data_folder
from Association.ExclusiveNames import SurveyUniqueName, ConfigUniqueName, IdentityUniqueName
from qblox_drive_AS.support.UserFriend import *


class Queuer():
    def __init__(self):
        self.__CheckAllQueues__()
        self.EnforcedQueueOut:bool = False
    
    def __JOBIDconnector__(self):
        return "_"

    def __JobIDAssigner__(self):
        self.readableJOBID:str = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.JOBID:str = self.readableJOBID.replace("_","")
    
    def __Interchanges__(self):
        """ Reject the request into queue"""
        return self.Requirements
    
    def __JOBIDeraser__(self,name:str):
        last_idx_by_underscore = name.rfind(self.__JOBIDconnector__())
        if last_idx_by_underscore != -1:
            name = name[:last_idx_by_underscore]
        return name

    def __CheckMachineStatus__(self):
        if len([name for name in os.listdir(self.queue) if (os.path.isdir(os.path.join(self.queue,name)) or os.path.isfile(os.path.join(self.queue,name)))]) != 0:
            self.EnforcedQueueOut = True
            warning_print(f"Machine {self.machine_IP} is executing a mission now, deny queue in your request.")


    def __CheckAllQueues__(self):
        with open(machine_IP_table, "rb") as file:
            self.ip_table = tomli.load(file)
        
        for machine_queue in [os.path.join(queue_folder,ip.replace(".","_")) for ip, _ in self.ip_table.items()]:
            if not os.path.exists(machine_queue):
                os.mkdir(machine_queue)

    def __CheckSampleTodayFolder__(self):
        os.makedirs(os.path.join(data_folder,self.sample_name),exist_ok=True)
        self.this_sample_today_folder = os.path.join(data_folder,self.sample_name,datetime.now().strftime("%Y%m%d"))
        os.makedirs(self.this_sample_today_folder,exist_ok=True)
    
    def __TouchConfigNPara__(self)->dict:
        Config = [os.path.join(user_dep_config_folder,name) for name in os.listdir(user_dep_config_folder) if (os.path.isdir(os.path.join(user_dep_config_folder,name)) and ConfigUniqueName.lower() in name.lower())]
        Survey = [os.path.join(user_dep_config_folder,name) for name in os.listdir(user_dep_config_folder) if (os.path.isfile(os.path.join(user_dep_config_folder,name)) and SurveyUniqueName in name and name.split(".")[-1] == 'toml')][0]
        
        self.exp_type = os.path.split(Survey)[-1].split("_")[0].upper()
        if self.exp_type == "S0":
            print("!!!!!!",Survey)
            self.Requirements:dict = {"Survey_path":Survey}
            self.EnforcedQueueOut = True
        else:
            self.Identity = [os.path.join(user_dep_config_folder,name) for name in os.listdir(user_dep_config_folder) if (os.path.isfile(os.path.join(user_dep_config_folder,name)) and IdentityUniqueName == name.split(".")[0])][0]
            if len(Config) >= 1:
                self.Requirements:dict = {"Config_path":Config[0],"Survey_path":Survey}
            else:
                raise ValueError("Can't see any ExpConfigs folder")
    
    def __JOBIDLabels__(self):
        if not self.EnforcedQueueOut:
            with open(self.Identity, "r") as file:
                ID_card = json.load(file)
                self.sample_name = str(ID_card["Sample Name"]).replace(" ","")
                self.machine_IP = str(ID_card["Machine Address"]).replace(" ","")
        else:
            with open(self.Requirements["Survey_path"], "rb") as file:
                ID_card = tomli.load(file)
                self.sample_name = str(ID_card["sample_name"]).replace(" ","")
                self.machine_IP = str(ID_card["Machine_IP"]).replace(" ","")
        
        self.machine_system:str = self.ip_table[self.machine_IP]
        self.queue:str = os.path.join(queue_folder,self.machine_IP.replace(".","_"))

        # Check machine available 
        self.__CheckMachineStatus__()

        # assign JOBID
        self.__JobIDAssigner__()


    def QueueIn(self):
        # step_1 get in touch with the required data, ExpConfigs folder and ExpParasSurvey.toml are included
        self.__TouchConfigNPara__()

        # step_2 Get JOB_ID for this EXP request
        self.__JOBIDLabels__()

        # step_3 Rename the requirements and move it into queue folder according to the machine address.
        self.program_requirements = {}

        if not self.EnforcedQueueOut :
            for requirement in self.Requirements:
                match requirement:
                    case "Config_path":
                        JOBID_labeled_name = f"{os.path.split(self.Requirements['Config_path'])[-1]}{self.__JOBIDconnector__()}{self.JOBID}"
                    case "Survey_path":
                        JOBID_labeled_name = f"{os.path.split(self.Requirements['Survey_path'])[-1].split('.')[0]}{self.__JOBIDconnector__()}{self.JOBID}.toml"
                shutil.move(self.Requirements[requirement],os.path.join(self.queue,JOBID_labeled_name))
                self.program_requirements[requirement] = os.path.join(self.queue,JOBID_labeled_name)
                
        else:
            self.program_requirements = self.__Interchanges__()
            return self.program_requirements

    def QueueOut(self)->dict:
        # step_1 check this sample had been created a folder today
        self.__CheckSampleTodayFolder__()
        item_to_analyze:dict = {}
        # step_2 create a folder for this measurement by this JOBID
        self.JOB_folder = os.path.join(self.this_sample_today_folder,self.readableJOBID)
        os.makedirs(self.JOB_folder,exist_ok=True)

        # step_3 If use qblox, move the updated QD_file folder back to user belonged Config folder 
        if self.machine_system.lower() == 'qblox':
            # build a Updated_Configs folder to copy the QD file inside
            updated_QD_folder = os.path.join(self.queue,f"copied_{ConfigUniqueName}")
            # Copy
            shutil.copytree(self.program_requirements["Config_path"],updated_QD_folder)

            # move this folder back to user-dependent Config folder
            shutil.move(updated_QD_folder, user_dep_config_folder)

            # rename this config folder 
            os.rename(os.path.join(user_dep_config_folder,f"copied_{ConfigUniqueName}"),os.path.join(user_dep_config_folder,f"qblox_{ConfigUniqueName}"))
            item_to_analyze["Configs"] = os.path.join(user_dep_config_folder,f'qblox_{ConfigUniqueName}')
            eyeson_print(f"New QD-file folder had been name 'qblox_{ConfigUniqueName}' and moved to your 'MeasConfigs' folder, check the following path:")
            slightly_print(f"{os.path.join(user_dep_config_folder,f'qblox_{ConfigUniqueName}')}")

        # step_4 Move all the item in queue to the JOBID-folder, expected with: ExpConfigs folder (used), ExpParasSurvey.toml (used), EXP-results.nc and EXP-analysis.png
        for item_path in [os.path.join(self.queue, name) for name in os.listdir(self.queue)]:
            shutil.move(item_path, self.JOB_folder)

        for item_path in [os.path.join(self.JOB_folder, name) for name in os.listdir(self.JOB_folder)]:
            if ConfigUniqueName in os.path.split(item_path)[-1]:
                # expect only one 
                if self.machine_system.lower() == 'qm':
                    item_to_analyze["Configs"] = item_path
    
            if os.path.split(item_path)[-1].split(".")[-1] == "nc":
                # may have a lot, but no worries
                item_to_analyze["Data"] = item_path

        return item_to_analyze


    def QueueOutUrgently(self):
        """ Once Exp got an error, queue out the Configs and Survey back. """
        for requirement in self.program_requirements:
            match requirement:
                # Erase the JOBID
                case "Config_path":
                    JOBID_erased_name = self.__JOBIDeraser__(os.path.split(self.program_requirements['Config_path'])[-1])
                case "Survey_path":
                    JOBID_erased_name = f"{self.__JOBIDeraser__(os.path.split(self.program_requirements['Survey_path'])[-1].split('.')[0])}.toml"
            # send back to user config folder
            shutil.move(self.program_requirements[requirement],os.path.join(user_dep_config_folder,JOBID_erased_name))

        # delete all the rest item in the queue
        for item in os.listdir(self.queue):
            item = os.path.join(self.queue,item)
            if os.path.isfile(item) or os.path.islink(item):
                os.remove(item)
            elif os.path.isdir(item):
                shutil.rmtree(item)

        print("Queuer urgently queue out the exp requests.")


if __name__ == "__main__":
    Officer = Queuer()
    items = Officer.QueueIn()

