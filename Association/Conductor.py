import os, tomli
from Housekeeper import Maid
from FBI import Canvasser


class Coordinator():
    
    def __init__(self):
       pass


    def __ExpParasCollects__(self, *args, **kwargs):
        Survey = Canvasser("",[])
        Survey.__toml_decoder__(r"C:\Users\ratis_wu\Documents\GitHub\UQMS\S1_ExpParasSurvey.toml")
        self.Exp = Survey.__callExp__()
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
    CO = Coordinator()
    CO.__ExpParasCollects__()