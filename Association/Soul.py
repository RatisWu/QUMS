from numpy import ndarray
from types import FunctionType
from abc import abstractmethod
import inspect

def empty_func():FunctionType

class ExpSpirit():
    def __init__(self):
        pass
    
    @abstractmethod
    def provide_ExpSurveyInfo(self,*args):
        pass
    
    @abstractmethod
    def set_SurveyDecodeProtocol(self,*args):
        """ name attributes end with '_protocol' like `self.ROelements_protocol` """
        pass

    @abstractmethod
    def set_qubitUnique_variables(self,*args):
        pass
    
    @abstractmethod
    def set_qubitShared_variables(self,*args):
        """ name attributes start and end with '_' like `self._avg_n_` """
        pass

    @abstractmethod
    def set_pulseSchedule(self,system:str,*args):
        pass

    @abstractmethod
    def set_analysis(self,*args):
        pass




class S0_MeasInit():
    def __init__(self):
        self.Instrument_IP:str = "" 
        self.how_many_couplers:int = 0
        self.how_many_qubits:int = 0
        self.cool_down_date:str = ""
        self.cool_down_dr:str = ""
        self.sample_name:str = ""
        self.chip_type:str = ""


class S1_CS(ExpSpirit):
    def __init__(self):
        super().__init__()


    def set_qubitUnique_variables(self):
        self.freq_range = list([])
        
    def set_SurveyDecodeProtocol(self):
        # This part will be replace by a function built in parent
        self.ro_elements_protocol:dict = {"layer":2,"1F":{"name":"joint_qbs","value":"2F"},"2F":[{"name":"freq_samples","value":"freq_range"}]} # The value in "2F" shoud exist in the ExpParasSurvey.toml 

    def set_qubitShared_variables(self):
        self._machine_IP_:str = ""
        self._avg_n_:int = 0
        self._list_sampling_func_:FunctionType = empty_func

    def provide_ExpSurveyInfo(self):
        self.set_qubitShared_variables()
        self.set_qubitUnique_variables()


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
    
    s1 = S1_CS()
    s1.provide_ExpSurveyInfo()
    shared_Paras = [name for name in [name for name, _ in inspect.getmembers(s1) if not name.startswith("__")] if  name.startswith("_") and name.endswith("_")]
    print(shared_Paras)
    unique_Paras = [name for name in list(vars(s1).keys()) if name not in shared_Paras and name.split("_")[-1].lower() != 'protocol']
    print(unique_Paras)


