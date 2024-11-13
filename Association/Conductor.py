import os, tomli
from Association.FBI import Canvasser


class Executor():
    
    def __init__(self,machine_type:str,survey_path:str,configs_path:str):
       self.survey_path = survey_path
       self.config_path = configs_path
       self.machine_type = machine_type


    def __ExpParasCollects__(self, *args, **kwargs):
        Survey = Canvasser("",[])
        Survey.toml_decoder(self.survey_path)
        self.Exp = Survey.brain
        parameters = Survey.assigned_paras
        for para_name in parameters :
            setattr(self.Exp, para_name, parameters[para_name])

            print(para_name,": ",getattr(self.Exp, para_name))
        
    def __ExpExecutes__(self, *args, **kwargs):
        pass

    def __ExpResultsAnalyzes__(self, *args, **kwargs):
        pass

    def MeasWorkFlow(self):
        self.__ExpParasCollects__()

        self.__ExpExecutes__()

        self.__ExpResultsAnalyzes__()



if __name__ == "__main__":
    CO = Executor("",r"C:\Users\ratis_wu\Documents\GitHub\UQMS\S1_ExpParasSurvey.toml","")
    CO.__ExpParasCollects__()