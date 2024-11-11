import sys, os, time, tomli
from Modularize.support.QDmanager import QDmanager
from .FBI import  user_dep_config_folder
data_folder = "C:\ExpData"

class Maid():
    """ Connected to Conductor.Coordinator, it's responsible for build up some folders like Data-saving, """
    def __init__(self, exp_paras:dict, sample_register:bool=False):
        self.__exp_paras__ = exp_paras
        if sample_register:
            self.__registerSample__()

    def __registerSample__(self):
        # Create sample data folder
        self.sample_data_folder = os.path.join(data_folder,self.__exp_paras__["sample_name"].replace(" ",""))
        if os.path.exists(self.sample_data_folder):
            raise NameError("This sample name had been registered, please try the other name to register it like add '_v2' after the name.")
        else :
            os.mkdir(self.sample_data_folder)
        # build up sample info toml
        with open(os.path.join(self.sample_data_folder,"sample_info.toml"), "w") as file:
            for item in self.__exp_paras__:
                file.write(f"{item} = '{self.__exp_paras__[item]}'\n")  # Inline comments
                file.write("\n")  #
        
        print(f"sample '{self.__exp_paras__['sample_name'].replace(' ','')}' successfully registered !")


    def __getSampleInfo__(self,sample_folder_path:str):
        info = {}
        with open(os.path.join(sample_folder_path,"sample_info.toml"), "rb") as file:
            sample_info = tomli.load(file)
        for info_name, value in sample_info.items():
            info[info_name] = value.replace(" ","")
        return info
    
    def __createNewQD__(self,sample_folder_path:str):
        """ For qblox system """
        sample_info = self.__getSampleInfo__(sample_folder_path)
        Qmanager = QDmanager(user_dep_config_folder)
        # Check HCFG is in the config folder 
        
        if 
        hcfg = 
        Qmanager.build_new_QD(int(sample_info['how_many_qubits']),int(sample_info['how_many_couplers']),cfg,sample_info['Instrument_IP'],sample_info['cool_down_dr'],chip_name=sample_info['sample_name'],chip_type=sample_info['chip_type'])
        Qmanager.refresh_log("new-born!")



if __name__ == "__main__":
    m = Maid({})
    sample_info = m.__getSampleInfo__(r"C:\ExpData\5Q4C_Test")
    print(sample_info)



