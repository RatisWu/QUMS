from abc import ABC, abstractmethod


# Exp framework
class ExpSpirit(ABC):
    def __init__(self):
        self.__save_data_folder:int = ""
        self.__machine_type:str = ""
        self.__connections:list = []
        self.__JOBID:str = ""
        self.__BetaMode:bool = False
        self.provide_ExpSurveyInfo()
    @property
    def BetaMode(self):
        return self.__BetaMode
    @BetaMode.setter
    def BetaMode(self, beta:bool):
        self.__BetaMode = beta
    
    @property
    def save_data_folder(self):
        return self.__save_data_folder
    @save_data_folder.setter
    def save_data_folder(self, path:str):
        self.__save_data_folder = path
    
    @property
    def machine_type(self):
        return self.__machine_type
    @machine_type.setter
    def machine_type(self, type:str):
        self.__machine_type = type
    
    @property
    def connections(self):
        return self.__connections
    @connections.setter
    def connections(self, items:list):
        self.__connections = items
    
    @property
    def JOBID(self):
        return self.__JOBID
    @JOBID.setter
    def JOBID(self, ID:str):
        self.__JOBID = ID

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
    
    
    def show_assigned_paras(self):
        # Filter attributes that don't start with '__' and some properties
        assigned_paras = [
            (attr, getattr(self, attr)) for attr in dir(self) if not attr.startswith("__") 
            and not attr.startswith("_") and not callable(getattr(self, attr)) 
            and not isinstance(getattr(type(self), attr, None), property)
            and not isinstance(getattr(self, attr), ExpParas)
        ]
        for item in assigned_paras:
            print(f"{item[0]}: {item[1]}, type: {type(item[1])}\n")


# Exp parameter type
class ExpParas():
    def __init__(self,name:str,custom_type:str,uniqueness:int=1,message:str="",pre_fill:str=None):
        """
        Level your exp parameters. Because in your measurement the exp parameters have different works, some are shared with every qubits, 
        another are exp variables but keep same between different qubits, the other are exactly unique for qubit.

        ### Parameters:
        - name (`str`): The name of this parameter, will be shown on ExpParasSurvey. Please keep it the same as the attribute name in Exp_Encyclopedia.
        - uniqueness (`int`): Specifying how unique is this parameter for the qubits.\n
         - uniqueness = 1 (common), for the parameter which is (1) **NOT** a exp-variable and (2) keeps the same for all qubits in this measurement, Ex. `avg_n`\n 
         - uniqueness = 2 (middle), for the parameter which is (1) a exp-variable and (2) keeps the same for all qubits in this measurement, Ex. `bias` when FluxCavity \n 
         - uniqueness = 3 (unique), for the parameter which is (1) a exp-variable and (2) **totally different** for all qubits in this measurement, Ex. `freq` when FluxCavity \n
         - uniqueness = 4 (QM-only), for the parameter which is only applied for QM \n
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
        self.pre_fill:str = pre_fill
        self.type:str = custom_type
        self.uniqueness:int = uniqueness
        self.message:str = message
        self.__check_uniqueness__()
    
    def __check_uniqueness__(self):
        if int(self.uniqueness) > 4:
            raise ValueError("Uniqueness must lower than or equal to 4 !")
        if int(self.uniqueness)==4 and self.pre_fill is None:
            raise ValueError(f"Your Exp para '{self.name}' uniqueness == 4 but pre_fill is None, check it! The pre_fill must not be None when the uniqueness is 4.")




  

