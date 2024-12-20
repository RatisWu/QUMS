import os, importlib.util, inspect, tomli
from Association.ExclusiveNames import *
import Association.Exp_Encyclopedia
from Association.Soul import ExpParas
import Association
from qblox_drive_AS.support.UserFriend import *

def owned_attribute(obj, attr):
    return hasattr(obj, attr) and attr in obj.__dict__


class Canvasser():
    def __init__(self):
        pass

    def __callExp__(self,decode:bool=False,script_path:str=None)->Association.Exp_Encyclopedia.ExpSpirit:
        """ If arg `script_path` was given, search the ExpSpirit in it, this is designed for a developing measurement script"""
        if script_path is not None:
            script_name = os.path.splitext(os.path.basename(script_path))[0]

            # Load the module
            spec = importlib.util.spec_from_file_location(script_name, script_path)
            Exp_Encyclopedia = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(Exp_Encyclopedia)
        else:
            Exp_Encyclopedia = Association.Exp_Encyclopedia

        page = [name for name, obj in inspect.getmembers(Exp_Encyclopedia,inspect.isclass) if owned_attribute(obj,"get_ExpLabel") and name != "ExpSpirit"] 
        method = [getattr(Exp_Encyclopedia,exp)() for exp in page if getattr(getattr(Exp_Encyclopedia,exp)(),"get_ExpLabel")().lower() == self.exp_type.lower()][0]
        if decode:
            if self.exp_type.lower() in ["s8","r1b"]:
                setattr(method,OneshotUniqueVariableName,[])  # method.target_qs = []
            
        return method
            
        
    def generate_ExpParas_servey(self,exp_type:str,target_qs:list,generate_2_this_folder:str='',script_path:str=None):
        self.exp_type = exp_type.upper()
        # Get all attributes of the class excluding built-in ones
        if generate_2_this_folder == "":
            self.file_path=os.path.join(os.path.expanduser("~"),f"{self.exp_type}_{SurveyUniqueName}.{survey_file_fmt}")
        else:
            self.file_path=os.path.join(generate_2_this_folder,f"{self.exp_type}_{SurveyUniqueName}.{survey_file_fmt}")

        if script_path == "":
            script_path = None

        self.brain = self.__callExp__(script_path=script_path)
        if len(target_qs) == 0:
            dependency = [1,2,3]
        else:
            dependency = [1,2]
        
        with open(self.file_path, "w") as file:
            file.write(f"# Measurement Parameters Survey for {self.brain.get_ExpLabel()}_{self.brain.__class__.__name__} \n")
            file.write(f"# *** Unit: Frequency (Hz), Time (s). \n\n")
            
            # common parameters
            for attr_name in [name for name, _ in inspect.getmembers(self.brain) if not name.startswith("__") and isinstance(getattr(self.brain,name),ExpParas) and getattr(self.brain,name).uniqueness in dependency]:
                attr:ExpParas = getattr(self.brain,attr_name)
                
                if attr.pre_fill is not None and attr.pre_fill != "":
                    if attr.type.lower() in ['str','func']:
                        file.write(f"{attr.name} = ' {attr.pre_fill} '  # ({attr.type}), {attr.message} \n")
                    else:
                        file.write(f"{attr.name} =  {attr.pre_fill}     # ({attr.type}), {attr.message} \n")
                else:
                    if attr.type.lower() in ['str','func']:
                        file.write(f"{attr.name} = '  '  # ({attr.type}), {attr.message} \n")
                    else:
                        file.write(f"{attr.name} =       # ({attr.type}), {attr.message} \n")
                    
                file.write("\n")
            
            # QM unique para
            if len(target_qs) == 0:
                but = False
                for idx, attr_name in enumerate([name for name, _ in inspect.getmembers(self.brain) if not name.startswith("__") and isinstance(getattr(self.brain,name),ExpParas) and getattr(self.brain,name).uniqueness == 4]):
                    attr:ExpParas = getattr(self.brain,attr_name)
                    if idx == 0:
                        but = True
                        file.write(f"# QM unique zone =================================== (Qblox skip it)\n")
                        file.write("\n")
                    
                    if attr.pre_fill is not None and attr.pre_fill != "":
                        if attr.type.lower() in ['str','func','dict']:
                            file.write(f'   {attr.name} = " {attr.pre_fill} "  # ({attr.type}), {attr.message} \n')
                        else:
                            file.write(f"   {attr.name} =  {attr.pre_fill}     # ({attr.type}), {attr.message} \n")
                    else:
                        if attr.type.lower() in ['str','func','dict']:
                            file.write(f'   { attr.name} = "  "  # ({attr.type}), {attr.message} \n')
                        else:
                            file.write(f"   { attr.name} =       # ({attr.type}), {attr.message} \n")
                    
                    file.write("\n")
                    
                if but:
                    file.write(f"# QM zone end ===================================\n")
                    file.write("\n")
            
            # Qblox unique parameters
            if len(target_qs) != 0:
                file.write("# Qblox unique zone =================================== (QM skip it)\n")
                file.write("\n")
                if self.exp_type.lower() not in ["s8","r1b"]:
                    
                    for target in target_qs:
                        file.write(f'[{target}]\n')    
                        for attr_name in [name for name, _ in inspect.getmembers(self.brain) if not name.startswith("__") and isinstance(getattr(self.brain,name),ExpParas) and getattr(self.brain,name).uniqueness == 3]:
                            attr:ExpParas = getattr(self.brain,attr_name)
                            if attr.pre_fill is not None and attr.pre_fill != "":
                                if attr.type.lower() in ['str','func']:
                                    file.write(f"   {attr.name} = ' {attr.pre_fill} '  # ({attr.type}), {attr.message} \n")
                                else:
                                    file.write(f"   {attr.name} =  {attr.pre_fill}     # ({attr.type}), {attr.message} \n")
                            else:
                                if attr.type.lower() in ['str','func']:
                                    file.write(f"   {attr.name} = '  '  # ({attr.type}), {attr.message} \n")
                                else:
                                    file.write(f"   {attr.name} =       # ({attr.type}), {attr.message} \n")

                            file.write("\n")   
                else:
                    file.write(f"{OneshotUniqueVariableName} = {target_qs}  # type in list \n")
                    file.write("\n")
                file.write("# Qblox zone end =================================== \n")
                file.write("\n")

        eyeson_print("ParameterSurvey had been assigned to you at:")
        slightly_print(f"{self.file_path}")

    def para_decoder(self,survey_path:str=None,script_path:str=None):
        """ If you want it do your assigned measurement, please give the arg `script_path` and make sure the object inside inherit [ExpSpirit](file:///opt/UQMS/Script/UQMS/Association/Soul.py) """
        
        # Load exp parameters from TOML file
        with open(survey_path, "rb") as file:
            toml_data = tomli.load(file)

        self.exp_type = os.path.split(survey_path)[-1].split("_")[0]
        self.brain = self.__callExp__(decode=True,script_path=script_path)
        
        #! Get parameters
        assigned_paras = {}
        for section, attributes in toml_data.items():
            if type(attributes) == str:
                attributes = attributes.replace(" ","")
            assigned_paras[section] = attributes

        # make parameters dependence  
        joint_qbs = [name for name in assigned_paras if name not in dir(self.brain)] # ExpParas.name not in self.brain.attributes
        if len(joint_qbs) != 0:
            print("measure qs: ",joint_qbs)
        self.assigned_paras = {}
        if len(joint_qbs) > 0:
            for item in assigned_paras[joint_qbs[0]]:
                self.assigned_paras[item] = {}
                for q in joint_qbs:
                    self.assigned_paras[item][q] = assigned_paras[q][item]
            for q in joint_qbs:
                del assigned_paras[q]
            
        self.assigned_paras.update(assigned_paras) # completed
        
    
    def config_decoder(self,machine_type:str,config_path:str)->list:
        """ Remember: config_path is a folder ! """
        match machine_type.lower():
            case 'qblox':
                # [ QD_path ]
                self.hardware_connections:list = [os.path.join(config_path,name) for name in os.listdir(config_path) if os.path.isfile(os.path.join(config_path,name)) and name.split(".")[-1] == 'pkl']
            case 'qm':
                from config_component.configuration import import_config
                from qspec.channel_info import import_spec
                for idx, item_name in enumerate([name for name in os.listdir(config_path) if name.split("_")[-1].split(".")[0] in ['config','spec']]):
                    if idx == 2:
                        raise FileExistsError("Why your '_config.pkl' or '_spec.pkl' is not unique ?")
                    if item_name.split("_")[-1].split(".")[0] == 'config':
                        config_obj = import_config(os.path.join(config_path,item_name))
                    else:
                        spec = import_spec(os.path.join(config_path,item_name))
                
                # [ config_obj, spec ]
                self.hardware_connections = list([config_obj,spec])
            case _:
                """ To be determined """
                raise KeyError(f"Unknown machine type was given as '{machine_type}', Expected only 'QM' or 'Qblox'.")

        


        
if __name__ == "__main__":

    """ Create meas parameters survey """
    # Survey = Canvasser()
    # Survey.generate_ExpParas_servey('S1', ['q0','q1'])

    """ get assigned meas parameters """
    Survey = Canvasser()
    Survey.para_decoder(r"c:\ExpQueue\192_168_1_10\S0_ExpParasSurvey_cc90e236.toml")

