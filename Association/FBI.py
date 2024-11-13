import os, sys, time, inspect, tomli
from Association.ExclusiveNames import *
from Association.Soul import ExpParas
from Association.Housekeeper import Maid
from Association.Roads import user_dep_config_folder, machine_IP_table
from numpy import linspace, arange, ndarray
from types import FunctionType
from functools import partial
from Association import Exp_Encyclopedia

def owned_attribute(obj, attr):
    return hasattr(obj, attr) and attr in obj.__dict__


class Canvasser():
    def __init__(self,exp_type:str, target_qs:list):
        self.exp_type:str=exp_type
        self.exp_target_qs:list = target_qs if exp_type.lower() != 's0' else []

    def __callExp__(self):
        return getattr(Exp_Encyclopedia,[name for name, obj in inspect.getmembers(Exp_Encyclopedia,inspect.isclass) if owned_attribute(obj,"get_ExpLabel") and obj().get_ExpLabel() == self.exp_type][0])()#if self.exp_type == getattr(Exp_Encyclopedia,name)().get_ExpLabel() and isinstance(getattr(Exp_Encyclopedia,name), type)]:
            
        
    def generate_ExpParas_servey(self):
        # Get all attributes of the class excluding built-in ones
        self.file_path=f"{self.exp_type}_{SurveyUniqueName}.toml"
        self.brain = self.__callExp__()
        
        with open(self.file_path, "w") as file:
            file.write(f"# Measurement Parameters Survey for {self.brain.get_ExpLabel()}_{self.brain.__class__.__name__} \n\n")
            file.write(f"machine_IP = '  ' # Important !")
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

    def toml_decoder(self,survey_path:str=None):
        if survey_path is None:
            survey_path = [os.path.join(user_dep_config_folder,name) for name in os.listdir(user_dep_config_folder) if (os.path.isfile(os.path.join(user_dep_config_folder,name)) and SurveyUniqueName in name)][0]

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
            if section != "machine_IP":
                assigned_paras[section] = attributes
        
        # make parameters dependence  
        joint_qbs = [name for name in assigned_paras if name not in dir(self.brain)]
        self.assigned_paras = {}
        if len(joint_qbs) > 0:
            for item in assigned_paras[joint_qbs[0]]:
                self.assigned_paras[item] = {}
                for q in joint_qbs:
                    self.assigned_paras[item][q] = assigned_paras[q][item]
            for q in joint_qbs:
                del assigned_paras[q]
            
        self.assigned_paras.update(assigned_paras)

       
        
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
    Survey.toml_decoder(r"c:\ExpQueue\192_168_1_10\S0_ExpParasSurvey_cc90e236.toml")
    # maid = Maid(Survey.__assined_paras__,True) # register a new sample
    # data_folder_path = maid.sample_data_folder # to be saved into your config or QD_file
    # S1_main_roles = Survey.__toml_decoder__()
    # print(S1_main_roles)

