import os, tomli
from Association.FBI import Canvasser
from Association.Soul import ExpSpirit


class Executor():
    
    def __init__(self,machine_type:str,survey_path:str,configs_path:str):
       self.survey_path = survey_path
       self.config_path = configs_path
       self.machine_type = machine_type
       self.Survey = Canvasser()


    def __ExpParasCollects__(self, *args, **kwargs):
        self.Survey.para_decoder(self.survey_path)
        self.Exp:ExpSpirit = self.Survey.brain
        self.Exp.save_data_folder = os.path.split(self.survey_path)[0]
        self.Exp.JOBID = os.path.split(self.survey_path)[-1].split("_")[-1].split(".")[0]
        parameters = self.Survey.assigned_paras
        for para_name in parameters :
            setattr(self.Exp, para_name, parameters[para_name])

        
    def __ExpExecutes__(self, *args, **kwargs):
        self.Survey.config_decoder(self.machine_type,self.config_path)
        self.Exp.machine_type = self.machine_type
        self.Exp.connections = self.Survey.hardware_connections
        self.Exp.start_measurement()

    def __ExpResultsAnalyzes__(self, *args, **kwargs):
        self.Exp.start_analysis()

    def MeasWorkFlow(self,bypass:bool=False):
        ''' Use arg `bypass` skip connecting to machine '''
        self.__ExpParasCollects__()

        if not bypass:
            self.__ExpExecutes__()

            self.__ExpResultsAnalyzes__()




if __name__ == "__main__":
    CO = Executor("",r"C:\Users\ratis_wu\Documents\GitHub\UQMS\S1_ExpParasSurvey.toml","")
    CO.__ExpParasCollects__()