import sys, os, time, tomli
from qblox_drive_AS.support.UserFriend import slightly_print
from Association.Roads import data_folder




class Maid():
    """ Connected to Conductor.Coordinator, it's responsible for build up some folders like Data-saving, """
    def __init__(self, exp_paras:dict={}, sample_register:bool=False):
        self.__exp_paras__ = exp_paras
        if sample_register:
            self.__registerSample__()

    def __registerSample__(self):
        # Create sample data folder
        self.sample_data_folder = os.path.join(data_folder,str(self.__exp_paras__["sample_name"]).replace(" ",""))
        if not os.path.exists(self.sample_data_folder):
            os.mkdir(self.sample_data_folder)
        else:
            slightly_print("This sample had been measured ! Use the original folder.")
        
        # build up sample info toml
        with open(os.path.join(self.sample_data_folder,"sample_info.toml"), "w") as file:
            for item in self.__exp_paras__:
                file.write(f"{item} = '{self.__exp_paras__[item]}'\n")  # Inline comments
                file.write("\n")  #
        
        print(f"sample '{str(self.__exp_paras__['sample_name']).replace(' ','')} successfully registered !")


    def getSampleInfo(self,sample_folder_path:str):
        info = {}
        with open(os.path.join(sample_folder_path,"sample_info.toml"), "rb") as file:
            sample_info = tomli.load(file)
        for info_name, value in sample_info.items():
            info[info_name] = str(value).replace(" ","")
        return info
    
    def save_process(self,queue_out_gift:list|dict,sameple_name:str):
        pass
    


if __name__ == "__main__":
    m = Maid({})
    




