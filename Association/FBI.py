import os, sys, time, inspect, tomli
from ExclusiveNames import *
from Soul import ExpParas
from Housekeeper import Maid, user_dep_config_folder, machine_IP_table
from numpy import linspace, arange, ndarray
from types import FunctionType
from functools import partial
import Exp_Encyclopedia

def owned_attribute(obj, attr):
    return hasattr(obj, attr) and attr in obj.__dict__


class Canvasser():
    def __init__(self,exp_type:str, target_qs:list):
        self.exp_type:str=exp_type
        self.exp_target_qs:list = target_qs if exp_type.lower() != 's0' else []

    def __callExp__(self):
        return getattr(Exp_Encyclopedia,[name for name, obj in inspect.getmembers(Exp_Encyclopedia,inspect.isclass) if owned_attribute(obj,"get_ExpLabel") and obj().get_ExpLabel() == self.exp_type][0])()#if self.exp_type == getattr(Exp_Encyclopedia,name)().get_ExpLabel() and isinstance(getattr(Exp_Encyclopedia,name), type)]:
            

    def __CoordsDecode__(self,coordsProtocol:dict,joint_qbs:list,function:callable=None,**kwargs):
        result = {}
        layer_2_configs = coordsProtocol["2F"]
    
        for qb in joint_qbs:
            result[qb] = {}
     
            for config in layer_2_configs:
                field_name = config["name"]
                variable_name = config["value"]

                if variable_name in kwargs:
                    result[qb][field_name] = kwargs[variable_name][qb] if type(kwargs[variable_name][qb]) != list else function(kwargs[variable_name][qb])
                else:
                    raise KeyError(f"Missing the variable {variable_name} for layer '2F' in kwargs !")
            
        return result  
        
    def __generate_ExpParas_servey__(self):
        # Get all attributes of the class excluding built-in ones
        self.file_path=f"{self.exp_type}_{SurveyUniqueName}.toml"
        self.brain = self.__callExp__()
        
        with open(self.file_path, "w") as file:
            file.write(f"# Measurement Parameters Survey for {self.brain.get_ExpLabel()}_{self.brain.__class__.__name__} \n\n")
            # common parameters
            for attr_name in [name for name, _ in inspect.getmembers(self.brain) if not name.startswith("__") and isinstance(getattr(self.brain,name),ExpParas) and getattr(self.brain,name).uniqueness != 3]:
                attr:ExpParas = getattr(self.brain,attr_name)
                match attr.uniqueness:
                    case 1:
                        match attr.type.lower():
                            case 'str'|'function'|'func':
                                file.write(f"{attr.name} = '  ' # type in {'str, options [linspace/ arange/ logsapce/ maually]' if attr.type.lower() in ['function','func'] else attr.type} \n")
                            case _:
                                file.write(f"{attr.name} =      # type in {attr.type if attr.type.lower() != 'list' else 'list, rule: [ start, end, pts/step ] depends on its sampling function or [fixed value]'}\n")
                    case 2:
                        match attr.type.lower():
                            case 'str':
                                file.write(f"{attr.name} = '  ' # type in str \n")
                            case _:
                                file.write(f"{attr.name} =      # type in {attr.type if attr.type.lower() != 'list' else 'list, rule: [ start, end, pts/step ] depends on its sampling function or [fixed value]'}\n")
                file.write("\n")
            # most unique parameters
            for target in self.exp_target_qs:
                file.write(f'[{target}]\n')    
                for attr_name in [name for name, _ in inspect.getmembers(self.brain) if not name.startswith("__") and isinstance(getattr(self.brain,name),ExpParas) and getattr(self.brain,name).uniqueness == 3]:
                    attr:ExpParas = getattr(self.brain,attr_name)
                    match attr.type.lower():
                        case 'str':
                            file.write(f"   {attr.name} = '  ' # type in str \n")
                        case _:
                            file.write(f"   {attr.name} =      # type in {attr.type if attr.type.lower() != 'list' else 'list, rule: [ start, end, pts/step ] depends on its sampling function or [fixed value]'}\n")
                file.write("\n")

    def __toml_decoder__(self,survey_path:str=None):
        if survey_path is None:
            survey_path = [os.path.join(user_dep_config_folder,name) for name in os.listdir(user_dep_config_folder) if (os.path.isfile(os.path.join(user_dep_config_folder,name)) and name.split(".")[0].split("_")[-1]==SurveyUniqueName)][0]

        # Load exp parameters from TOML file
        with open(survey_path, "rb") as file:
            toml_data = tomli.load(file)
        
        self.exp_type = os.path.split(survey_path)[-1].split("_")[0]
        self.brain = self.__callExp__()
        #! Get parameters
        assigned_paras = {}
        # Assign values to object attributes
        # Dynamically create attributes for each section in the TOML data
        
        for section, attributes in toml_data.items():
            assigned_paras[section] = attributes
        
        # make parameters dependence  
        joint_qbs = [name for name in assigned_paras if name not in dir(self.brain)]
        self.assigned_paras = {}
        for item in assigned_paras[joint_qbs[0]]:
            self.assigned_paras[item] = {}
            for q in joint_qbs:
                self.assigned_paras[item][q] = assigned_paras[q][item]
        for q in joint_qbs:
            del assigned_paras[q]
            
        self.assigned_paras.update(assigned_paras)

        # if self.exp_type.lower() != 's0':
        #     #! Determine the instruments according to the given IP
        #     self.exp_machine_type:str = ""   # should be "Qblox" or "QM"
        #     with open(machine_IP_table, "rb") as file:
        #         machine_IPs = tomli.load(file)
        #     for IP, Machine_type in machine_IPs.items():
        #         if IP == self.assigned_paras["machine_IP"].replace(" ",""):
        #             self.exp_machine_type = Machine_type.replace(" ","")
                
        #     if self.exp_machine_type == "" :
        #         raise ValueError(f"Unknown machine IP was given = {self.assined_paras['machine_IP']}")
        #     print(f"Trying to use {self.exp_machine_type} to do the exp.")
            
            #! Trying to build up ro_elements for meas
            # self.brain = Exp_Encyclopedia(self.exp_type, self.exp_machine_type)   
            # Paras_attr = [name for name, _ in inspect.getmembers(self.brain) if (not name.startswith("__")) and (name not in self.brain.__shared_attr__)]
            # joint_qbs = [item for item in self.assigned_paras if item not in self.brain.__shared_attr__]
            # if "list_sampling_func" in self.assigned_paras and self.assigned_paras["list_sampling_func"].replace(" ","") in ["linspace", "arange"]: sampling_func = eval(self.assigned_paras["list_sampling_func"])
            # else: sampling_func = linspace
            
        
        
        
    # def __buildGeneralSettings__(self):
    #     shared_settings = {}
    #     for item_name in self.assigned_paras:
    #         if item_name in self.brain.__shared_attr__:
    #             shared_settings[item_name] = self.assigned_paras[item_name]

    #     return shared_settings
    
    # def __buildROelements__(self,attrs:list,joint_qubits:list,sampling_func:callable=None):
    #     if sampling_func is None: sampling_func = linspace
    #     match self.exp_machine_type.lower():
    #         case "qblox":
    #             kwargs_dict = {}
    #             for attr in attrs:
    #                 kwargs_dict[attr] = {}
    #                 for q in joint_qubits:

    #                     kwargs_dict[attr][q] = self.assigned_paras[q][attr]
    #             sampler = partial(self.__listTypePara_decoder__, generate_samples_function =sampling_func)
    #             ro_elements = self.__CoordsDecode__(self.brain.__ro_elements_coords__,joint_qubits,sampler,**kwargs_dict)
    #         case "qm":
    #             pass

    #         case "_":
    #             raise TypeError(f"Unsupported instrumenet type = {self.exp_machine_type}")

    #     return ro_elements
    
    # def __buildZelements__(self):
    #     #TODO 
    #     pass


        
if __name__ == "__main__":

    # Create meas parameters survey
    # Survey = Canvasser('S1', ['q0','q1'])
    # Survey.__generate_ExpParas_servey__()

    # get assigned meas parameters
    Survey = Canvasser("",[])
    Survey.__toml_decoder__(r"C:\Users\ratis_wu\Documents\GitHub\UQMS\S1_ExpParasSurvey.toml")
    # maid = Maid(Survey.__assined_paras__,True) # register a new sample
    # data_folder_path = maid.sample_data_folder # to be saved into your config or QD_file
    # S1_main_roles = Survey.__toml_decoder__()
    # print(S1_main_roles)

