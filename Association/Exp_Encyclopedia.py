
from Association.Soul import ExpParas, ExpSpirit
import inspect

class SampleRegister():
    def __init__(self):
        self.provide_ExpSurveyInfo()
    
    def get_ExpLabel(self)->str:
        return "S0"

    def provide_ExpSurveyInfo(self):
        self.Instrument_IP = ExpParas("Machine_IP","str",1)
        self.cool_down_date = ExpParas("cool_down_date","str",1)
        self.cool_down_dr = ExpParas("cool_down_dr","str",1)
        self.sample_name = ExpParas("sample_name","str",1)
        


class BbCavitySearch(ExpSpirit):
    def __init__(self):
        super().__init__()

    def get_ExpLabel(self)->str:
        return "S1"

    def set_variables(self):
        self.freq_range = ExpParas("freq_range","list",3)
        self.bias_range = ExpParas("bias_range","list",2)
        self.avg_n = ExpParas("avg_n","int",1)
        self.freq_sampling_func = ExpParas("freq_sampling_func","func",1)
        self.bias_sampling_func = ExpParas("bias_sampling_func","func",1)

    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def set_pulseSchedule(self,):
        match self.machine_type:
            case qblox:
                # from A import B_ps, B_ana
                self.raw_data = []

    
    def set_analysis(self,*args):
        pass #fig = B_ana(self.raw_data)

    
    def workflow(self):
        self.machine_type = ""
        # self.ro_elements, self.machine_type = FBI.decode()
        self.set_pulseSchedule()
        self.set_analysis()


if __name__ == "__main__":
    
    s1 = BbCavitySearch()
    s1.provide_ExpSurveyInfo()
    shared_Paras = [name for name in [name for name, _ in inspect.getmembers(s1) if not name.startswith("__")] if  name.startswith("_") and name.endswith("_")]
    print(shared_Paras)
    unique_Paras = [name for name in list(vars(s1).keys()) if name not in shared_Paras and name.split("_")[-1].lower() != 'protocol']
    print(unique_Paras)