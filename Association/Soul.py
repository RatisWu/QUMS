from numpy import ndarray
from types import FunctionType
from abc import ABC, abstractmethod
import inspect

# Exp framework
class ExpSpirit(ABC):
    def __init__(self):
        self.save_data_folder:int = ""
        self.machine_type:str = ""
        self.connections:list = []
        self.JOBID:str = ""
        self.provide_ExpSurveyInfo()

    @abstractmethod
    def get_ExpLabel(self,*args)->str:
        ''' Return the exp label "S1", "S2", ... '''
        pass
    
    @abstractmethod
    def provide_ExpSurveyInfo(self,*args):
        """ Let FBI.Canvasser know what parameters for measurement should be in the ExpParasSurvey.toml """
        pass
    
    @abstractmethod
    def set_variables(self,*args):
        """ What is the parameters for this measurement ? Set them in attributes. """
        pass


    @abstractmethod
    def start_measurement(self,system:str,*args):
        """ After connceted to the machine, prepare and run the pulse schedule and get the exp raw data. """
        pass

    @abstractmethod
    def start_analysis(self,*args):
        """ Have raw data, analyze it here. """
        pass

    def workflow(self,hardware_info:dict):
        """ Good looking """
        pass

# Exp parameter type
class ExpParas():
    def __init__(self,name:str,custom_type:str,uniqueness:int=1):
        """
        Level your exp parameters. Because in your measurement the exp parameters have different works, some are shared with every qubits, 
        another are exp variables but keep same between different qubits, the other are exactly unique for qubit.

        ### Parameters:
        - name (`str`): The name of this parameter, will be shown on ExpParasSurvey.
        - uniqueness (`int`): Specifying how unique is this parameter for the qubits.\n
         - uniqueness = 1 (common), for the parameter which is (1) **NOT** a exp-variable and (2) keeps the same for all qubits in this measurement, Ex. `avg_n`\n 
         - uniqueness = 2 (middle), for the parameter which is (1) a exp-variable and (2) keeps the same for all qubits in this measurement, Ex. `bias` when FluxCavity \n 
         - uniqueness = 3 (unique), for the parameter which is (1) a exp-variable and (2) **totally different** for all qubits in this measurement, Ex. `freq` when FluxCavity \n
        - custom_type (`str`): Makes user know what type to fill into the questions for ExpParasSurvey, common python type like [str, int, list, function, ...] is supported.
        
        ### Attributes:
            1. self.uniqueness, return the uniqueness of it.
            2. self.value, return the name of it. 
            3. self.readable, helps program know where the PulseSchedule needs it, **Only** for uniqueness= 2 or 3 parameters.
                -- for those which can be translated to readable it should includes the following keywords: ["freq", "power", "bias", "z_amp", "time", "shots"].
        
        ### Raises:
        - **ValueError**: If uniqueness is higher than 3. 
        """

        self.name:str = name
        self.type:str = custom_type
        self.uniqueness:int = uniqueness
    
    def __check_uniqueness__(self):
        if int(self.uniqueness) > 3:
            raise ValueError("Uniqueness must lower than or equal to 3 !")
        
    
    def __giveProgramReadable__(self):
        if self.uniqueness >= 2:
            if "freq" in self.name.lower():
                self.readable = "freq_samples"
            elif "power" in self.name.lower():
                self.readable = "power_samples"
            elif "bias" in self.name.lower():
                self.readable = "bias_samples"
            elif "z_amp" in self.name.lower():
                self.readable = "z_samples"
            elif "time" in self.name.lower():
                self.readable = "time_samples"
            elif "sots" in self.name.lower():
                self.readable = "shots"
            else:
                self.readable = "dummy_samples"



  

