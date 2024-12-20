
import os
from Association.Soul import ExpParas, ExpSpirit
from qspec.channel_info import ChannelInfo
from config_component.configuration import Configuration
from ab.QM_config_dynamic import initializer
from exp.save_data import DataPackager
from qblox_drive_AS.support.UserFriend import *
from xarray import open_dataset, Dataset
from numpy import ndarray, diff




# S0 done
class SampleRegister():
    def __init__(self):
        self.provide_ExpSurveyInfo()
    
    def get_ExpLabel(self)->str:
        return "S0"

    def provide_ExpSurveyInfo(self):
        self.Machine_IP = ExpParas("Machine_IP","str",1)
        self.cool_down_date = ExpParas("cool_down_date","str",1)
        self.cool_down_dr = ExpParas("cool_down_dr","str",1)
        self.sample_name = ExpParas("sample_name","str",1)

        

# S1 done
class CavitySearch(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S1"

    def set_variables(self):
        self.init_macro = ExpParas("init_macro","dict",4,message="Make sure it's in the quotes (\"\"),initializer operation: initializer(time=400e-6,mode='wait')",pre_fill={"time":2e-6,"mode":'wait'})
        self.ro_elements = ExpParas("ro_elements","list",4,message="Fill in who to read like: ['q0_ro',...]",pre_fill=[])
        self.freq_range = ExpParas("freq_range","list",3,message="QM span given value from LO, Qblox sweep what freq you give. rule: [start, end]")
        self.freq_ptsORstep = ExpParas("freq_ptsORstep","float",1,message="According to sampling function, use step or pts for all qubit",pre_fill=100)
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=100)
        self.freq_sampling_func = ExpParas("freq_sampling_func","func",1,message="sampling function options: 'linspace', 'arange'.",pre_fill='linspace')


    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):
        # show parameters it recieved
        slightly_print("\n==============================")
        eyeson_print(f"Executtion: {self.get_ExpLabel()}, {self.__class__.__name__}")
        print("\n")
        self.show_assigned_paras()
        slightly_print("==============================\n")
        

        if not self.BetaMode:
            match self.machine_type.lower():
                case 'qblox':
                    from qblox_drive_AS.support.ExpFrames import Zoom_CavitySearching
                    self.target_qs = list(self.freq_range.keys())
                    self.EXP = Zoom_CavitySearching(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                    self.EXP.SetParameters( self.freq_range,self.freq_ptsORstep,self.avg_n,execution=True)
                    self.EXP.WorkFlow()
                    eyeson_print("Raw data located:")
                    slightly_print(self.EXP.RawDataPath)

                case 'qm':
                    self.init_macro = eval(self.init_macro)
                    from exp.rofreq_sweep import ROFreqSweep
                    config_obj:Configuration = self.connections[0]
                    spec:ChannelInfo = self.connections[1]
                    config = config_obj.get_config()
                    qmm, _ = spec.buildup_qmm()
                    self.EXP = ROFreqSweep(config, qmm)
                    self.EXP.ro_elements = self.ro_elements
                    self.EXP.initializer = initializer(self.init_macro["time"]*1e9,mode=self.init_macro["mode"])
                    """ freq unit in MHz """
                    self.EXP.freq_range = (float(self.freq_range[0])*1e-6, float(self.freq_range[1])*1e-6)
                    
                    if self.freq_sampling_func == 'arange':
                        self.EXP.resolution = self.freq_ptsORstep*1e-6
                        
                    else:
                        self.EXP.resolution = (abs(float(self.freq_range[1])-float(self.freq_range[0]))/float(self.freq_ptsORstep))*1e-6
                    self.raw_data_path:str = os.path.join(self.save_data_folder,f"ROFreqSweep_{self.JOBID}.nc")
                    
                    self.dataset = self.EXP.run( int(self.avg_n))
                    self.dataset.to_netcdf(self.raw_data_path,engine='netcdf4')
        
    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"][0]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)

            case 'qm':
                    import numpy as np
                    import matplotlib.pyplot as plt
                    raw_data_files = analysis_need["Data"]
                    for file in raw_data_files:
                        save_folder = os.path.split(file)[0]
                        dataset = open_dataset(file)
                        idata = dataset[self.target_qs[0]].sel(mixer='I').values
                        qdata = dataset[self.target_qs[0]].sel(mixer='Q').values
                        zdata = idata+1j*qdata
                        plt.plot(dataset.coords["frequency"].values,np.abs(zdata))
                        plt.savefig(os.path.join(save_folder,f"ROFreqSweep_{self.JOBID}.png"))
                        plt.close()

# S1b done
class BbCavitySearch(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S1b"

    def set_variables(self):
        self.freq_range = ExpParas("freq_range","list",3,message="Qblox only, LO sweeps what freq range you give. rule: [start, end]")
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=100)
        self.freq_sampling_func = ExpParas("freq_sampling_func","func",1,message="sampling function options: 'linspace', 'arange'.",pre_fill='linspace')
        self.freq_ptsORstep = ExpParas("freq_ptsORstep","float",1,message="According to sampling function, use step or pts for all qubit")
        # self.bias_range = ExpParas("bias_range","list",2)  # <- only for test
        # self.bias_sampling_func = ExpParas("bias_sampling_func","func",1) # <- only for test.

    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):
        # show parameters it recieved
        slightly_print("\n==============================")
        eyeson_print(f"Executtion: {self.get_ExpLabel()}, {self.__class__.__name__}")
        print("\n")
        self.show_assigned_paras()
        slightly_print("==============================\n")
        

        if not self.BetaMode:
            match self.machine_type.lower():
                case 'qblox':
                    from qblox_drive_AS.support.ExpFrames import BroadBand_CavitySearching
                    self.EXP = BroadBand_CavitySearching(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                    target_q = list(self.freq_range.keys())[0]
                    if self.freq_sampling_func == 'arange':
                        pts = int(abs(float(self.freq_range[target_q][1])-float(self.freq_range[target_q][0]))/float(self.freq_ptsORstep))
                    else:
                        pts = int(self.freq_ptsORstep)
                    self.EXP.SetParameters([target_q],float(self.freq_range[target_q][0]),float(self.freq_range[target_q][1]),pts)
                    self.EXP.WorkFlow()
                    eyeson_print("Raw data located:")
                    slightly_print(self.EXP.RawDataPath)
                case 'qm':
                    raise SystemError(f"QM didn't support LO-sweeping Cavity Searching !")
    
    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"][0]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)

# S2 done
class PowerCavity(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S2"

    def set_variables(self):
        self.init_macro = ExpParas("init_macro","dict",4,message="Make sure it's in the quotes (\"\"),initializer operation: initializer(time=400e-6,mode='wait')",pre_fill={"time":10e-6,"mode":'wait'})
        self.ro_elements = ExpParas("ro_elements","list",4,message="Fill in who to read like: ['q0_ro',...]",pre_fill=[])
        self.freq_range = ExpParas("freq_range","list",3,message="Values to span. rule: [start, end]")
        self.freq_ptsORstep = ExpParas("freq_ptsORstep","int",1,message="Depends on Freq sampling func set in step or pts.")
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=200)
        self.power_range = ExpParas("power_range","list",2,message="rule: [start, end, pts/step], QM please set in step.",pre_fill=[0,0.6,30])
        self.freq_sampling_func = ExpParas("freq_sampling_func","func",1,message="sampling function options: 'linspace', 'arange'.",pre_fill='linspace')
        self.power_sampling_func = ExpParas("power_sampling_func","func",1,message="sampling function options: 'linspace', 'arange', 'logspace'. QM please use 'logspace'.",pre_fill='linspace')


    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):
        # show parameters it recieved
        slightly_print("\n==============================")
        eyeson_print(f"Executtion: {self.get_ExpLabel()}, {self.__class__.__name__}")
        print("\n")
        self.show_assigned_paras()
        slightly_print("==============================\n")
        

        if not self.BetaMode:
            match self.machine_type.lower():
                case 'qblox':
                    self.target_qs = list(self.freq_range.keys())
                    from qblox_drive_AS.support.ExpFrames import PowerCavity
                    self.EXP = PowerCavity(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                    self.EXP.SetParameters(self.freq_range, self.power_range, self.power_sampling_func, self.freq_ptsORstep,self.avg_n,execution=True)
                    self.EXP.WorkFlow()
                    eyeson_print("Raw data located:")
                    slightly_print(self.EXP.RawDataPath)

                case 'qm':
                    self.init_macro = eval(self.init_macro)
                    from exp.rofreq_sweep_power_dep import ROFreqSweepPowerDep
                    config_obj:Configuration = self.connections[0]
                    spec:ChannelInfo = self.connections[1]
                    config = config_obj.get_config()
                    qmm, _ = spec.buildup_qmm()
                    self.EXP = ROFreqSweepPowerDep(config, qmm)
                    self.EXP.ro_elements = self.ro_elements
                    self.EXP.initializer = initializer(self.init_macro["time"]*1e9,mode=self.init_macro["mode"])
                    """ freq unit in MHz """
                    self.EXP.freq_range = (float(self.freq_range[0])*1e-6, float(self.freq_range[1])*1e-6)
                    print(f"freq range= {self.EXP.freq_range}")
                    if self.freq_sampling_func == 'arange':
                        self.EXP.freq_resolution = self.freq_ptsORstep*1e-6
                        print(f'arange ,step= {self.EXP.freq_resolution}')
                    else:
                        self.EXP.freq_resolution = abs(diff(self.freq_range))[0]/self.freq_ptsORstep
                    """ power """
                    if self.power_sampling_func in ['linspace','logspace']:
                        self.EXP.amp_scale = self.power_sampling_func[:3]
                    else:
                        self.EXP.amp_scale = 'log'
                    self.EXP.amp_resolution = self.power_range[-1]    
                    self.EXP.amp_mod_range = (self.power_range[0],self.power_range[1])
                    self.folder_label = os.path.split(self.save_data_folder)[-1]  

                    
                    self.dataset = self.EXP.run( int(self.avg_n))
                    save_path = os.path.join(self.save_data_folder,f"PowerCavity_{self.JOBID}.nc")
                    self.dataset.to_netcdf(save_path)
        
    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"][0]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)

            case 'qm':
                from exp.plotting import PainterPowerDepRes
                raw_data_files = analysis_need["Data"]
                for file in raw_data_files:
                    dataset = open_dataset(file)
                    painter = PainterPowerDepRes()
                    folder_path = os.path.split(file)[0]
                    dp = DataPackager(folder_path,'pic',time_label_type="no_label")
                    figs = painter.plot(dataset,"Power_Cavity")
                    dp.save_figs( figs )

# S2b done
class DressedCavityFit(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S2b"

    def set_variables(self):
        self.freq_range = ExpParas("freq_range","list",3,message="QM span given value from LO, Qblox sweep what freq you give. rule: [start, end]")
        self.RO_amp = ExpParas("RO_amp","float",3,message=" A single value.")
        self.freq_ptsORstep = ExpParas("freq_ptsORstep","float",1,message="According to sampling function, use step or pts for all qubit",pre_fill=100)
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=100)
        self.freq_sampling_func = ExpParas("freq_sampling_func","func",1,message="sampling function options: 'linspace', 'arange',",pre_fill='linspace')


    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):
        # show parameters it recieved
        slightly_print("\n==============================")
        eyeson_print(f"Executtion: {self.get_ExpLabel()}, {self.__class__.__name__}")
        print("\n")
        self.show_assigned_paras()
        slightly_print("==============================\n")
        

        if not self.BetaMode:
            self.target_qs = list(self.freq_range.keys())
            match self.machine_type.lower():
                case 'qblox':
                    from qblox_drive_AS.support.ExpFrames import Dressed_CavitySearching
                    self.EXP = Dressed_CavitySearching(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                    self.EXP.SetParameters( self.freq_range,self.RO_amp,self.freq_ptsORstep,self.avg_n,execution=True)
                    self.EXP.WorkFlow()
                    eyeson_print("Raw data located:")
                    slightly_print(self.EXP.RawDataPath)
                case 'qm':
                    raise SystemError(f"QM didn't support DressedCavityFit !")

    
    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"][0]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                print(f"QD @ {QD_path}")
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)

# S3 done 
class FluxCavity(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S3"

    def set_variables(self):
        self.init_macro = ExpParas("init_macro","dict",4,message="Make sure it's in the quotes (\"\"),initializer operation: initializer(time=400e-6,mode='wait')",pre_fill={"time":10e-6,"mode":'wait'})
        self.ro_elements = ExpParas("ro_elements","list",4,message="Fill in who to read like: ['q0_ro',...]",pre_fill=[])
        self.freq_range = ExpParas("freq_range","list",3,message="Values to span. rule: [start, end]")
        self.freq_ptsORstep = ExpParas("freq_ptsORstep","int",1,message="Depends on Freq sampling func set in step or pts.")
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=300)
        self.flux_range = ExpParas("flux_range","list",2,message="rule: [start, end, pts/step], QM please set in step.")
        self.bias_targets = ExpParas("bias_targets","list",2,message="If you want bias on coupler, please fill it in like ['c0', ...]. Otherwise leave []. QM call it z_elements",pre_fill=[])
        self.freq_sampling_func = ExpParas("freq_sampling_func","func",1,message="sampling function options: 'linspace', 'arange'.",pre_fill='linspace')
        self.flux_sampling_func = ExpParas("flux_sampling_func","func",1,message="sampling function options: 'linspace', 'arange'.",pre_fill='linspace')


    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):
        # show parameters it recieved
        slightly_print("\n==============================")
        eyeson_print(f"Executtion: {self.get_ExpLabel()}, {self.__class__.__name__}")
        print("\n")
        self.show_assigned_paras()
        slightly_print("==============================\n")
        

        if not self.BetaMode:
            match self.machine_type.lower():
                case 'qblox':
                    from qblox_drive_AS.support.ExpFrames import FluxCavity,FluxCoupler
                    self.target_qs = list(self.freq_range.keys())
                    if len(list(self.bias_targets)) == 0: 
                        slightly_print("Flux Cavity start.")
                        self.EXP = FluxCavity(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                        self.EXP.SetParameters(self.freq_range, self.flux_range, self.flux_sampling_func, self.freq_ptsORstep,self.avg_n,execution=True)
                    else:
                        slightly_print(f"Bias targets: {self.bias_targets}")
                        self.EXP = FluxCoupler(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                        self.EXP.SetParameters(self.freq_range, self.bias_targets, self.flux_range, self.flux_sampling_func, self.freq_ptsORstep,self.avg_n,execution=True)
                    
                    self.EXP.WorkFlow()
                    eyeson_print("Raw data located:")
                    slightly_print(self.EXP.RawDataPath)
                case 'qm':
                    self.init_macro = eval(self.init_macro)
                    from exp.rofreq_sweep_flux_dep import freq_sweep_flux_dep
                    config_obj:Configuration = self.connections[0]
                    spec:ChannelInfo = self.connections[1]
                    config = config_obj.get_config()
                    qmm, _ = spec.buildup_qmm()
                    init_macro = initializer(self.init_macro["time"]*1e9,mode=self.init_macro["mode"])
                    z_amp_ratio_range = (self.flux_range[0],self.flux_range[1])
                    freq_range = (self.freq_range[0]*1e-6,self.freq_range[1]*1e-6)
                    if self.freq_sampling_func == 'linspace':
                        freq_resolution = abs(diff(self.EXP.freq_range))[0]/self.freq_ptsORstep
                    else:
                        freq_resolution = self.freq_ptsORstep * 1e-6

                    if self.flux_sampling_func == 'arange':
                        z_amp_ratio_resolution = self.flux_range[-1]
                    else:
                        z_amp_ratio_resolution = abs(diff(z_amp_ratio_range))[0]/self.flux_range[-1]
                    
                    self.dataset = freq_sweep_flux_dep(self.ro_elements,self.bias_targets,config, qmm, self.avg_n, 1, freq_range, z_amp_ratio_range,z_amp_ratio_resolution,freq_resolution,init_macro)
                    save_path = os.path.join(self.save_data_folder,f"FluxCavity_{self.JOBID}.nc")
                    self.dataset.to_netcdf(save_path)

            
    
    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"][0]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)
            
            case 'qm':
                from exp.plotting import PainterFindFluxPeriod
                raw_data_files = analysis_need["Data"]
                for file in raw_data_files:
                    dataset = open_dataset(file)
                    painter = PainterFindFluxPeriod()
                    folder_path = os.path.split(file)[0]
                    dp = DataPackager(folder_path,'pic',time_label_type="no_label")
                    figs = painter.plot(dataset,"Flux_Cavity")
                    dp.save_figs( figs )

# S3b done
class GroundPositioning(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S3b"

    def set_variables(self):
        self.RO_amp_factor = ExpParas("RO_amp_factor","float",3,message="new RO-amp = old RO-amp * factor")
        self.shots = ExpParas("shots","int",1,pre_fill=10000)


    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):
        # show parameters it recieved
        slightly_print("\n==============================")
        eyeson_print(f"Executtion: {self.get_ExpLabel()}, {self.__class__.__name__}")
        print("\n")
        self.show_assigned_paras()
        slightly_print("==============================\n")
        

        if not self.BetaMode:
            self.target_qs = list(self.RO_amp_factor.keys())
            match self.machine_type.lower():
                case 'qblox':
                    from qblox_drive_AS.support.ExpFrames import IQ_references
                    self.EXP = IQ_references(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                    self.EXP.SetParameters( self.RO_amp_factor,self.shots,execution=True)
                    self.EXP.WorkFlow()
                    eyeson_print("Raw data located:")
                    slightly_print(self.EXP.RawDataPath)
                case 'qm':
                    raise SystemError(f"QM didn't support Ground-state Positioning !")

    
    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"][0]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)

# S5, done
class FluxQubitSpectrum(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S5"

    def set_variables(self):
        self.init_macro = ExpParas("init_macro","dict",4,message="Make sure it's in the quotes (\"\"),initializer operation: initializer(time=400e-6,mode='wait')",pre_fill={"time":10e-6,"mode":'wait'})
        self.ro_elements = ExpParas("ro_elements","list",4,message="Fill in who to read like: ['q0_ro',...]",pre_fill=[])
        self.xy_elements = ExpParas("xy_elements","list",4,message="Fill in who to drive like: ['q0_xy',...]",pre_fill=[])
        self.driving_time = ExpParas("driving_time","float",4,message="XY driving time.",pre_fill=20e-6)
        self.xy_amp_mod = ExpParas("xy_amp_mod","float",4,message="Driving pulse amp modification.",pre_fill=0.1)
        self.sweep_type = ExpParas("sweep_type","str",4,message="z_pulse or overlap ?",pre_fill='z_pulse')
        self.parametric_drive = ExpParas("parametric_drive","bool",4,message="0 for False 1 for True",pre_fill=0)
        self.Pdrive_element = ExpParas("Pdrive_element","str",4,message="Apply parametric drive on who ? like: 'q0_z'. Keep it empty if you don't apply.",pre_fill="")

        self.freq_range = ExpParas("freq_range","list",3,message="Values to span. rule: [start, end] like: [-300e6, +200e6].")
        self.freq_ptsORstep = ExpParas("freq_ptsORstep","int",1,message="Depends on Freq sampling func set in step or pts.")
        self.bias_targets = ExpParas("bias_targets","list",2,message="Must be fill, what element will be biased, like ['q0','q1','c0', ...].") 
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=500)
        self.flux_range = ExpParas("flux_range","list",2,message="rule: [start, end, pts/step]. QM call it 'z_amp_ratio_range'")
        self.freq_sampling_func = ExpParas("freq_sampling_func","func",1,message="sampling function options: 'linspace', 'arange'.",pre_fill='linspace')
        self.flux_sampling_func = ExpParas("flux_sampling_func","func",1,message="sampling function options: 'linspace', 'arange'.",pre_fill='linspace')


    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):
        # show parameters it recieved
        slightly_print("\n==============================")
        eyeson_print(f"Executtion: {self.get_ExpLabel()}, {self.__class__.__name__}")
        print("\n")
        self.show_assigned_paras()
        slightly_print("==============================\n")
        

        if not self.BetaMode:
            match self.machine_type.lower():
                case 'qblox':
                    self.target_qs = list(self.freq_range.keys())
                    from qblox_drive_AS.support.ExpFrames import FluxQubit
                    self.EXP = FluxQubit(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                    self.EXP.SetParameters(self.freq_range, self.bias_targets, self.flux_range, self.flux_sampling_func, self.freq_ptsORstep,self.avg_n,execution=True)
                    self.EXP.WorkFlow()
                    eyeson_print("Raw data located:")
                    slightly_print(self.EXP.RawDataPath)
                case 'qm':
                    self.init_macro = eval(self.init_macro)
                    from exp.xyfreq_sweep_flux_dep import XYFreqFlux
                    config_obj:Configuration = self.connections[0]
                    spec:ChannelInfo = self.connections[1]
                    config = config_obj.get_config()
                    qmm, _ = spec.buildup_qmm()
                    self.EXP = XYFreqFlux(config, qmm)
                    self.EXP.ro_elements = self.ro_elements
                    self.EXP.xy_elements = self.xy_elements
                    self.EXP.z_elements = self.bias_targets
                    self.EXP.xy_driving_time = self.driving_time * 1e6
                    self.EXP.xy_amp_mod = self.xy_amp_mod
                    self.EXP.sweep_type = self.sweep_type
                    self.EXP.parametric_drive = self.parametric_drive
                    self.EXP.drive_element = self.Pdrive_element
                    self.EXP.z_amp_ratio_range = (self.flux_range[0],self.flux_range[1])
                    self.EXP.freq_range = (self.freq_range[0]*1e-6,self.freq_range[1]*1e-6)
                    if self.freq_sampling_func == 'linspace':
                        self.EXP.freq_resolution = abs(diff(self.EXP.freq_range))[0]/self.freq_ptsORstep
                    else:
                        self.EXP.freq_resolution = self.freq_ptsORstep * 1e-6

                    if self.flux_sampling_func == 'arange':
                        self.EXP.z_amp_ratio_resolution = self.flux_range[-1]
                    else:
                        self.EXP.z_amp_ratio_resolution = abs(diff(self.EXP.z_amp_ratio_range))[0]/self.flux_range[-1]
                    
                    self.EXP.initializer = initializer(self.init_macro["time"]*1e9,mode=self.init_macro["mode"])
                    self.dataset = self.EXP.run( self.avg_n )
                    save_path = os.path.join(self.save_data_folder,f"FluxQubitSpec_{self.JOBID}.nc")
                    self.dataset.to_netcdf(save_path)
                
    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
    
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"][0]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)
            case 'qm':
                from exp.plotting import PainterFluxDepQubit
                raw_data_files = analysis_need["Data"]
                for file in raw_data_files:
                    dataset = open_dataset(file)
                    for attr in dataset.attrs:
                        if not isinstance(dataset.attrs[attr], ndarray):
                            dataset.attrs[attr] = [dataset.attrs[attr]]
                    painter = PainterFluxDepQubit()
                    folder_path = os.path.split(file)[0]
                    dp = DataPackager(folder_path,'pic',time_label_type="no_label")
                    figs = painter.plot(dataset,"Flux_Qubit_Spectrum")
                    dp.save_figs( figs )

# S4, done
class Power2tone(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S4"

    def set_variables(self):
        self.init_macro = ExpParas("init_macro","dict",4,message="Make sure it's in the quotes (\"\"),initializer operation: initializer(time=400e-6,mode='wait')",pre_fill={"time":10e-6,"mode":'wait'})
        self.ro_elements = ExpParas("ro_elements","list",4,message="Fill in who to read like: ['q0_ro',...]",pre_fill=[])
        self.xy_elements = ExpParas("xy_elements","list",4,message="Fill in who to drive like: ['q0_xy',...]",pre_fill=[])
        self.driving_time = ExpParas("driving_time","float",4,message="XY driving time.",pre_fill=20e-6)

        self.freq_range = ExpParas("freq_range","list",3,message="Values to sweep. rule: [start, end] like: [4.2e9, 4.7e9]. For Qblox: [0] calculate a advise value by computer.")
        self.freq_ptsORstep = ExpParas("freq_ptsORstep","int",1,message="Depends on Freq sampling func set in step or pts.")
        self.ROXYoverlap = ExpParas("ROXYoverlap","int",1,message="booling value set 0 for False (z_pulse) or 1 for True (overlap), RO-XY overlap or not ?",pre_fill=0)
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=300)
        self.power_range = ExpParas("power_range","list",2,message="rule: [start, end, pts/step] or [a fixed value], QM please fill in a fixed value.",pre_fill=[0,0.1,10])
        self.freq_sampling_func = ExpParas("freq_sampling_func","func",1,message="sampling function options: 'linspace', 'arange'.",pre_fill='linspace')
        self.power_sampling_func = ExpParas("power_sampling_func","func",1,message="sampling function options: 'linspace', 'arange', 'logspace'.",pre_fill='linspace')


    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):
        # show parameters it recieved
        slightly_print("\n==============================")
        eyeson_print(f"Executtion: {self.get_ExpLabel()}, {self.__class__.__name__}")
        print("\n")
        self.show_assigned_paras()
        slightly_print("==============================\n")
        

        if not self.BetaMode:         
            match self.machine_type.lower():
                case 'qblox':
                    from qblox_drive_AS.support.ExpFrames import PowerConti2tone
                    self.target_qs = list(self.freq_range.keys())
                    self.EXP = PowerConti2tone(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                    self.EXP.SetParameters(self.freq_range, self.power_range, self.power_sampling_func, self.freq_ptsORstep,self.avg_n,self.ROXYoverlap,execution=True)
                    self.EXP.WorkFlow()
                    eyeson_print("Raw data located:")
                    slightly_print(self.EXP.RawDataPath)
                case 'qm':
                    self.init_macro = eval(self.init_macro)
                    from exp.xyfreq_sweep import XYFreq
                    config_obj:Configuration = self.connections[0]
                    spec:ChannelInfo = self.connections[1]
                    config = config_obj.get_config()
                    qmm, _ = spec.buildup_qmm()
                    self.EXP = XYFreq(config, qmm)
                    self.EXP.ro_elements = self.ro_elements
                    self.EXP.xy_elements = self.xy_elements
                    self.EXP.xy_driving_time = self.driving_time * 1e6
                    self.EXP.xy_amp_mod = self.power_range[0]
                    self.EXP.sweep_type = "overlap" if self.ROXYoverlap else "z_pulse"
                    self.EXP.freq_range = (self.freq_range[0]*1e-6,self.freq_range[1]*1e-6)
                    if self.freq_sampling_func == 'linspace':
                        self.EXP.freq_resolution = abs(diff(self.EXP.freq_range))[0]/self.freq_ptsORstep
                    else:
                        self.EXP.freq_resolution = self.freq_ptsORstep * 1e-6
                    
                    self.EXP.initializer = initializer(self.init_macro["time"]*1e9,mode=self.init_macro["mode"])
                    self.dataset = self.EXP.run( self.avg_n )
                    save_path = os.path.join(self.save_data_folder,f"TwoTone_{self.JOBID}.nc")
                    self.dataset.to_netcdf(save_path)

            
    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"][0]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)
            case 'qm':
                from exp.plotting import PainterQubitSpec
                raw_data_files = analysis_need["Data"]
                for file in raw_data_files:
                    
                    dataset = open_dataset(file)
                    for attr in dataset.attrs:
                        if not isinstance(dataset.attrs[attr], ndarray):
                            dataset.attrs[attr] = [dataset.attrs[attr]]
                    
                    painter = PainterQubitSpec()
                    folder_path = os.path.split(file)[0]
                    dp = DataPackager(folder_path,'pic',time_label_type="no_label")
                    figs = painter.plot(dataset,"Qubit_Spectrum")
                    dp.save_figs( figs )

# S6, done
class PowerRabi(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S6"

    def set_variables(self):
        self.init_macro = ExpParas("init_macro","dict",4,message="Make sure it's in the quotes (\"\"),initializer operation: initializer(time=400e-6,mode='wait')",pre_fill={"time":100e-6,"mode":'wait'})
        self.ro_elements = ExpParas("ro_elements","list",4,message="Fill in who to read like: ['q0_ro',...]",pre_fill=[])
        self.xy_elements = ExpParas("xy_elements","list",4,message="Fill in who to drive like: ['q0_xy',...]",pre_fill=[])
        self.freq_range = ExpParas("freq_range","list",3,message="Values to span. rule: [start, end, resolution] like: [-3e6, 3e6, 1e6]",pre_fill=[])

        self.pi_amp = ExpParas("pi_amp","list",3,message="amp values span. rule: [start, end] like: [-0.6, 0.6].")
        self.pi_duration = ExpParas("pi_duration","float",3,message="Only for Qblox, how long is your pi-pulse ?",pre_fill=40e-9)
        # self.OSmode = ExpParas("OSmode","int",1,message="booling value set 0 for False or 1 for True, Use one-shot or not ?")
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=200)
        self.amp_sampling_func = ExpParas("amp_sampling_func","func",1,message="sampling function options: 'linspace', 'arange'.",pre_fill='linspace')
        self.pi_amp_ptsORstep = ExpParas("pi_amp_ptsORstep","int",1,message="Depends on sampling func set in step or pts.",pre_fill=100)


    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):
        # show parameters it recieved
        slightly_print("\n==============================")
        eyeson_print(f"Executtion: {self.get_ExpLabel()}, {self.__class__.__name__}")
        print("\n")
        self.show_assigned_paras()
        slightly_print("==============================\n")
        

        if not self.BetaMode:
            match self.machine_type.lower():
                case 'qblox':
                    from qblox_drive_AS.support.ExpFrames import PowerRabiOsci
                    self.target_qs = list(self.pi_amp.keys())
                    self.EXP = PowerRabiOsci(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                    self.EXP.SetParameters(self.pi_amp, self.pi_duration, self.amp_sampling_func, self.pi_amp_ptsORstep,self.avg_n,execution=True)
                    self.EXP.WorkFlow()
                    eyeson_print("Raw data located:")
                    slightly_print(self.EXP.RawDataPath)
                case 'qm':
                    self.init_macro = eval(self.init_macro)
                    from exp.rabi import RabiTime
                    config_obj:Configuration = self.connections[0]
                    spec:ChannelInfo = self.connections[1]
                    config = config_obj.get_config()
                    qmm, _ = spec.buildup_qmm()
                    self.EXP = RabiTime(config, qmm)
                    self.EXP.initializer = initializer(self.init_macro["time"]*1e9,mode=self.init_macro["mode"])
                    self.EXP.process = "power"
                    self.EXP.ro_elements = self.ro_elements
                    self.EXP.xy_elements = self.xy_elements
                    self.EXP.amp_range = (self.pi_amp[0], self.pi_amp[1]) 
                    self.EXP.freq_range = (self.freq_range[0]*1e-6, self.freq_range[1]*1e-6)
                    self.EXP.freq_resolution = self.freq_range[-1]*1e-6
                    if self.amp_sampling_func == 'arange':
                        self.EXP.amp_resolution = self.pi_amp_ptsORstep
                    else:
                        self.EXP.amp_resolution = abs(diff(self.EXP.freq_range))[0]/self.pi_amp_ptsORstep
                    self.dataset = self.EXP.run( self.avg_n )
                    save_path = os.path.join(self.save_data_folder,f"detunedPowerRabi_{self.JOBID}.nc")
                    self.dataset.to_netcdf(save_path)

            
    
    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"][0]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)
            case 'qm':
                from exp.plotting import PainterRabi
                raw_data_files = analysis_need["Data"]
                for file in raw_data_files:
                    
                    dataset = open_dataset(file)
                    for attr in dataset.attrs:
                        if not isinstance(dataset.attrs[attr], ndarray):
                            dataset.attrs[attr] = [dataset.attrs[attr]]
                    
                    painter = PainterRabi('power')
                    folder_path, file_name = os.path.split(file)
                    dp = DataPackager(folder_path,'pic',time_label_type="no_label")
                    figs = painter.plot(dataset,file_name.split("_")[0])
                    dp.save_figs( figs )

# S7, done
class TimeRabi(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S7"

    def set_variables(self):
        self.init_macro = ExpParas("init_macro","dict",4,message="Make sure it's in the quotes (\"\"),initializer operation: initializer(time=400e-6,mode='wait')",pre_fill={"time":100e-6,"mode":'wait'})
        self.ro_elements = ExpParas("ro_elements","list",4,message="Fill in who to read like: ['q0_ro',...]",pre_fill=[])
        self.xy_elements = ExpParas("xy_elements","list",4,message="Fill in who to drive like: ['q0_xy',...]",pre_fill=[])
        self.freq_range = ExpParas("freq_range","list",3,message="Values to span. rule: [start, end, resolution] like: [-3e6, 3e6, 1e6]",pre_fill=[])

        self.pi_amp = ExpParas("pi_amp","float",3,message="Only for Qblox, amp for your pi-pulse.",pre_fill=0.2)
        self.pi_duration = ExpParas("pi_duration","list",3,message="pi-len values span. rule: [start, end] like: [0, 200e-9]. ** QM starts from 16e-9 **")
        # self.OSmode = ExpParas("OSmode","int",1,message="booling value set 0 for False or 1 for True, Use one-shot or not ?")
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=200)
        self.duration_sampling_func = ExpParas("duration_sampling_func","func",1,message="sampling function options: 'linspace', 'arange'.",pre_fill='linspace')
        self.pi_dura_ptsORstep = ExpParas("pi_dura_ptsORstep","int",1,message="Depends on sampling func set in step or pts.",pre_fill=100)


    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):
        # show parameters it recieved
        slightly_print("\n==============================")
        eyeson_print(f"Executtion: {self.get_ExpLabel()}, {self.__class__.__name__}")
        print("\n")
        self.show_assigned_paras()
        slightly_print("==============================\n")
        

        if not self.BetaMode:
            match self.machine_type.lower():
                case 'qblox':
                    from qblox_drive_AS.support.ExpFrames import TimeRabiOsci
                    self.target_qs = list(self.pi_amp.keys())
                    self.EXP = TimeRabiOsci(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                    self.EXP.SetParameters( self.pi_duration, self.pi_amp,self.duration_sampling_func, self.pi_dura_ptsORstep,self.avg_n,execution=True)
                    self.EXP.WorkFlow()
                    eyeson_print("Raw data located:")
                    slightly_print(self.EXP.RawDataPath)
                case 'qm':
                    self.init_macro = eval(self.init_macro)
                    from exp.rabi import RabiTime
                    config_obj:Configuration = self.connections[0]
                    spec:ChannelInfo = self.connections[1]
                    config = config_obj.get_config()
                    qmm, _ = spec.buildup_qmm()
                    self.EXP = RabiTime(config, qmm)
                    self.EXP.initializer = initializer(self.init_macro["time"]*1e9,mode=self.init_macro["mode"])
                    self.EXP.process = "time"
                    self.EXP.ro_elements = self.ro_elements
                    self.EXP.xy_elements = self.xy_elements
                    self.EXP.time_range = (self.pi_duration[0]*1e9, self.pi_duration[1]*1e9) 
                    self.EXP.freq_range = (self.freq_range[0]*1e-6, self.freq_range[1]*1e-6)
                    self.EXP.freq_resolution = self.freq_range[-1]*1e-6
                    if self.duration_sampling_func == 'arange':
                        self.EXP.time_resolution = self.pi_dura_ptsORstep*1e9
                    else:
                        self.EXP.time_resolution = abs(diff(self.EXP.freq_range))[0]/self.pi_dura_ptsORstep
                    self.dataset = self.EXP.run( self.avg_n )
                    save_path = os.path.join(self.save_data_folder,f"detunedTimeRabi_{self.JOBID}.nc")
                    self.dataset.to_netcdf(save_path)

            
    
    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"][0]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)
            case 'qm':
                from exp.plotting import PainterRabi
                raw_data_files = analysis_need["Data"]
                for file in raw_data_files:
                    
                    dataset = open_dataset(file)
                    for attr in dataset.attrs:
                        if not isinstance(dataset.attrs[attr], ndarray):
                            dataset.attrs[attr] = [dataset.attrs[attr]]
                    
                    painter = PainterRabi('time')
                    folder_path, file_name = os.path.split(file)
                    dp = DataPackager(folder_path,'pic',time_label_type="no_label")
                    figs = painter.plot(dataset,file_name.split("_")[0])
                    dp.save_figs( figs )

# S8, need qm test on sample
class SingleShot(ExpSpirit):
    def __init__(self):
        super().__init__()
        
            
    def get_ExpLabel(self)->str:
        return "S8"

    def set_variables(self):
        self.init_macro = ExpParas("init_macro","dict",4,message="Make sure it's in the quotes (\"\"),initializer operation: initializer(time=400e-6,mode='wait')",pre_fill={"time":400e-6,"mode":'wait'})
        self.ro_elements = ExpParas("ro_elements","list",4,message="Fill in who to read like: ['q0_ro',...]",pre_fill=[])
        self.xy_elements = ExpParas("xy_elements","list",4,message="Fill in who to drive like: ['q0_xy',...]",pre_fill=[])
        self.histo_counts = ExpParas("histo_counts","int",1,message="Only for Qblox, repeat times of histogram",pre_fill=1)
        self.shots = ExpParas("shots","int",1,pre_fill=10000)


    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):
        # show parameters it recieved
        slightly_print("\n==============================")
        eyeson_print(f"Executtion: {self.get_ExpLabel()}, {self.__class__.__name__}")
        print("\n")
        self.show_assigned_paras()
        slightly_print("==============================\n")
        

        if not self.BetaMode:
            match self.machine_type.lower():
                case 'qblox':
                    from qblox_drive_AS.support.ExpFrames import SingleShot
                    self.EXP = SingleShot(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                    self.EXP.SetParameters( self.target_qs,self.histo_counts,self.shots,execution=True)
                    self.EXP.WorkFlow()
                    eyeson_print("Raw data located:")
                    slightly_print(self.EXP.RawDataPath)
                case 'qm':
                    self.init_macro = eval(self.init_macro)
                    from exp.readout_fidelity import readout_fidelity
                    config_obj:Configuration = self.connections[0]
                    spec:ChannelInfo = self.connections[1]
                    config = config_obj.get_config()
                    qmm, _ = spec.buildup_qmm()
                    init_macro = initializer(self.init_macro["time"]*1e9,mode=self.init_macro["mode"])
                    self.dataset = readout_fidelity( self.xy_elements, self.ro_elements, self.shots, config, qmm, init_macro) 
                    save_path = os.path.join(self.save_data_folder,f"ROfidelity_{self.JOBID}.nc")
                    self.dataset.to_netcdf(save_path)

    
    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"][0]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)
            case 'qm':
                from exp.plotting import plot_and_save_readout_fidelity
                raw_data_files = analysis_need["Data"]
                for file in raw_data_files:
                    
                    dataset = open_dataset(file)
                    for attr in dataset.attrs:
                        if not isinstance(dataset.attrs[attr], ndarray):
                            dataset.attrs[attr] = [dataset.attrs[attr]]
                    
                    folder_path, file_name = os.path.split(file)
                    dp = DataPackager(folder_path,'pic',time_label_type="no_label")
                    figs = plot_and_save_readout_fidelity(dataset,file_name.split("_")[0])
                    dp.save_figs( figs )

# S9, need qm test on sample
class RamseyT2(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S9"

    def set_variables(self):
        self.init_macro = ExpParas("init_macro","dict",4,message="Make sure it's in the quotes (\"\"),initializer operation: initializer(time=400e-6,mode='wait')",pre_fill={"time":300e-6,"mode":'wait'})
        self.ro_elements = ExpParas("ro_elements","list",4,message="Fill in who to read like: ['q0_ro',...]",pre_fill=[])
        self.xy_elements = ExpParas("xy_elements","list",4,message="Fill in who to drive like: ['q0_xy',...]",pre_fill=[])
        self.virtual_detune = ExpParas("virtual_detune","int",4,message="virtual detuning like: 0.5e6",pre_fill=0e6)
        
        self.max_evo_time = ExpParas("max_evo_time","int",3,message="evolution time maximum like: 20e-6.")
        # self.OSmode = ExpParas("OSmode","int",1,message="booling value set 0 for False or 1 for True, Use one-shot or not ?")
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=300)
        self.time_sampling_func = ExpParas("time_sampling_func","func",1,message="sampling function options: 'linspace', 'arange', 'logspace'.",pre_fill="linspace")
        self.time_ptsORstep = ExpParas("time_ptsORstep","int",1,message="Depends on sampling func set in step or pts.",pre_fill=100)
        self.histo_counts = ExpParas("histo_counts","int",1,message="repeat times of histogram. QM always use FPGA. Qblox use FPGA runnning while it's less than 101, otherwise use while-loop.",pre_fill=1)

    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):
        # show parameters it recieved
        slightly_print("\n==============================")
        eyeson_print(f"Executtion: {self.get_ExpLabel()}, {self.__class__.__name__}")
        print("\n")
        self.show_assigned_paras()
        slightly_print("==============================\n")
        
        if not self.BetaMode:
            match self.machine_type.lower():
                case 'qblox':
                    self.target_qs = list(self.max_evo_time.keys())
                    self.time_range = {}
                    for q in self.target_qs:
                        self.time_range[q] = [0, self.max_evo_time[q]]
                    from qblox_drive_AS.support.ExpFrames import Ramsey
                    self.EXP = Ramsey(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                    self.EXP.SetParameters( self.time_range, self.time_sampling_func,self.time_ptsORstep, self.histo_counts,self.avg_n,execution=True)
                    self.EXP.WorkFlow()
                    eyeson_print("Raw data located:")
                    slightly_print(self.EXP.RawDataPath)
                case 'qm':
                    self.init_macro = eval(self.init_macro)
                    from exp.ramsey import Ramsey
                    config_obj:Configuration = self.connections[0]
                    spec:ChannelInfo = self.connections[1]
                    config = config_obj.get_config()
                    qmm, _ = spec.buildup_qmm()
                    self.EXP = Ramsey(config, qmm)
                    self.EXP.shot_num = self.avg_n
                    self.EXP.initializer = initializer(self.init_macro["time"]*1e9,mode=self.init_macro["mode"])
                    self.EXP.ro_elements = self.ro_elements
                    self.EXP.xy_elements = self.xy_elements
                    self.EXP.virtual_detune = self.virtual_detune*1e-6
                    self.EXP.max_time = self.max_evo_time*1e6
                    if self.time_sampling_func == "arange":
                        self.EXP.time_resolution = self.time_ptsORstep*1e6
                    elif self.time_sampling_func == "linspace":
                        self.EXP.time_resolution = self.EXP.max_time/self.time_ptsORstep
                    else:
                        raise ValueError(f"Sorry, The given sampling function = {self.time_sampling_func} is temporarily unsupported !")
                    
                    if self.histo_counts == 1:
                        self.dataset = self.EXP.run()
                        save_path = os.path.join(self.save_data_folder,f"RamseyT2_{self.JOBID}.nc")
                        
                    else:
                        from exp.repetition_measurement import RepetitionMeasurement
                        re_exp = RepetitionMeasurement()
                        re_exp.exp_list = [self.EXP]
                        re_exp.exp_name = ["T2"]
                        self.dataset:Dataset = re_exp.run(self.histo_counts)[re_exp.exp_name[0]]
                        save_path = os.path.join(self.save_data_folder,f"RamseyT2Rep_{self.JOBID}.nc")
                    
                    self.dataset.to_netcdf(save_path)
                
        
    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"][0]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)
            case 'qm':
                from exp.plotting import PainterT2Ramsey, PainterT2Repeat
                raw_data_files = analysis_need["Data"]
                for file in raw_data_files:
                    
                    dataset = open_dataset(file)
                    for attr in dataset.attrs:
                        if not isinstance(dataset.attrs[attr], ndarray):
                            dataset.attrs[attr] = [dataset.attrs[attr]]
                    
                    folder_path, file_name = os.path.split(file)
                    if 'rep' not in file_name.lower():
                        painter = PainterT2Ramsey()
                    else:
                        painter = PainterT2Repeat()

                    dp = DataPackager(folder_path,'pic',time_label_type="no_label")
                    figs = painter.plot(dataset,file_name.split("_")[0])
                    dp.save_figs( figs )

# S10, need qm test on sample
class SpinEchoT2(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S10"

    def set_variables(self):
        self.init_macro = ExpParas("init_macro","dict",4,message="Make sure it's in the quotes (\"\"),initializer operation: initializer(time=400e-6,mode='wait')",pre_fill={"time":300e-6,"mode":'wait'})
        self.ro_elements = ExpParas("ro_elements","list",4,message="Fill in who to read like: ['q0_ro',...]",pre_fill=[])
        self.xy_elements = ExpParas("xy_elements","list",4,message="Fill in who to drive like: ['q0_xy',...]",pre_fill=[])
        self.max_evo_time = ExpParas("max_evo_time","int",3,message="evolution time maximum like: 20e-6.")
        # self.OSmode = ExpParas("OSmode","int",1,message="booling value set 0 for False or 1 for True, Use one-shot or not ?")
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=300)
        self.time_sampling_func = ExpParas("time_sampling_func","func",1,message="sampling function options: 'linspace', 'arange', 'logspace'.",pre_fill="linspace")
        self.time_ptsORstep = ExpParas("time_ptsORstep","int",1,message="Depends on sampling func set in step or pts.",pre_fill=100)
        self.histo_counts = ExpParas("histo_counts","int",1,message="repeat times of histogram. QM always use FPGA. Qblox use FPGA runnning while it's less than 101, otherwise use while-loop.",pre_fill=1)

    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):
        # show parameters it recieved
        slightly_print("\n==============================")
        eyeson_print(f"Executtion: {self.get_ExpLabel()}, {self.__class__.__name__}")
        print("\n")
        self.show_assigned_paras()
        slightly_print("==============================\n")
        

        if not self.BetaMode:
            match self.machine_type.lower():
                case 'qblox':
                    self.target_qs = list(self.max_evo_time.keys())
                    self.time_range = {}
                    for q in self.target_qs:
                        self.time_range[q] = [0, self.max_evo_time[q]]

                    from qblox_drive_AS.support.ExpFrames import SpinEcho
                    self.EXP = SpinEcho(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                    self.EXP.SetParameters( self.time_range, self.time_sampling_func,self.time_ptsORstep, self.histo_counts,self.avg_n,execution=True)
                    self.EXP.WorkFlow()
                    eyeson_print("Raw data located:")
                    slightly_print(self.EXP.RawDataPath)
                case 'qm':
                    self.init_macro = eval(self.init_macro)
                    from exp.single_spin_echo import SpinEcho
                    config_obj:Configuration = self.connections[0]
                    spec:ChannelInfo = self.connections[1]
                    config = config_obj.get_config()
                    qmm, _ = spec.buildup_qmm()
                    self.EXP = SpinEcho(config, qmm)
                    self.EXP.shot_num = self.avg_n
                    self.EXP.initializer = initializer(self.init_macro["time"]*1e9,mode=self.init_macro["mode"])
                    self.EXP.ro_elements = self.ro_elements
                    self.EXP.xy_elements = self.xy_elements
                    
                    self.EXP.time_range = (40, self.max_evo_time*1e6)
                    if self.time_sampling_func == "arange":
                        self.EXP.time_resolution = self.time_ptsORstep*1e6
                    elif self.time_sampling_func == "linspace":
                        self.EXP.time_resolution = abs(diff(self.EXP.time_range))[0]/self.time_ptsORstep
                    else:
                        raise ValueError(f"Sorry, The given sampling function = {self.time_sampling_func} is temporarily unsupported !")
                    
                    if self.histo_counts == 1:
                        self.dataset = self.EXP.run()
                        save_path = os.path.join(self.save_data_folder,f"SpinEcho_{self.JOBID}.nc")
                        
                    else:
                        from exp.repetition_measurement import RepetitionMeasurement
                        re_exp = RepetitionMeasurement()
                        re_exp.exp_list = [self.EXP]
                        re_exp.exp_name = ["spin_echo"]
                        self.dataset:Dataset = re_exp.run(self.histo_counts)[re_exp.exp_name[0]]
                        save_path = os.path.join(self.save_data_folder,f"SpinEchoRep_{self.JOBID}.nc")
                    
                    self.dataset.to_netcdf(save_path)

            
    
    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"][0]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)

            case 'qm':
                from exp.plotting import PainterT2SpinEcho, PainterT2Repeat
                raw_data_files = analysis_need["Data"]
                for file in raw_data_files:
                    
                    dataset = open_dataset(file)
                    for attr in dataset.attrs:
                        if not isinstance(dataset.attrs[attr], ndarray):
                            dataset.attrs[attr] = [dataset.attrs[attr]]
                    
                    folder_path, file_name = os.path.split(file)
                    if 'rep' not in file_name.lower():
                        painter = PainterT2SpinEcho()
                    else:
                        painter = PainterT2Repeat()

                    dp = DataPackager(folder_path,'pic',time_label_type="no_label")
                    figs = painter.plot(dataset,file_name.split("_")[0])
                    dp.save_figs( figs )


# S9b, done
class CPMG(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S9b"

    def set_variables(self):
        self.max_evo_time = ExpParas("max_evo_time","int",3,message="evolution time maximum like: 20e-6.")
        self.pi_num = ExpParas("pi_num","int",2,message="how many pi-pulses between your Ramsey ?")
        # self.OSmode = ExpParas("OSmode","int",1,message="booling value set 0 for False or 1 for True, Use one-shot or not ?")
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=300)
        self.time_sampling_func = ExpParas("time_sampling_func","func",1,message="sampling function options: 'linspace', 'arange', 'logspace'.",pre_fill='linspace')
        self.time_ptsORstep = ExpParas("time_ptsORstep","int",1,message="Depends on sampling func set in step or pts.",pre_fill=100)
        self.histo_counts = ExpParas("histo_counts","int",1,message="repeat times of histogram, <101 use FPGA otherwies use while loop.",pre_fill=1)

    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):
        # show parameters it recieved
        slightly_print("\n==============================")
        eyeson_print(f"Executtion: {self.get_ExpLabel()}, {self.__class__.__name__}")
        print("\n")
        self.show_assigned_paras()
        slightly_print("==============================\n")
        

        if not self.BetaMode:          
            match self.machine_type.lower():
                case 'qblox':
                    from qblox_drive_AS.support.ExpFrames import CPMG
                    pi_num = {}
                    self.time_range = {}
                    self.target_qs = list(self.max_evo_time.keys())
                    for q in self.target_qs:
                        pi_num[q] = self.pi_num
                        self.time_range[q] = [0, self.max_evo_time[q]]

                    self.EXP = CPMG(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                    self.EXP.SetParameters( self.time_range, pi_num, self.time_sampling_func,self.time_ptsORstep, self.histo_counts,self.avg_n,execution=True)
                    self.EXP.WorkFlow()
                    eyeson_print("Raw data located:")
                    slightly_print(self.EXP.RawDataPath)
                case 'qm':
                    raise SystemError(f"QM didn't support CPMG !")


    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"][0]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)

# S11, need qm test on sample
class EnergyRelaxation(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S11"

    def set_variables(self):
        self.init_macro = ExpParas("init_macro","dict",4,message="Make sure it's in the quotes (\"\"),initializer operation: initializer(time=400e-6,mode='wait')",pre_fill={"time":300e-6,"mode":'wait'})
        self.ro_elements = ExpParas("ro_elements","list",4,message="Fill in who to read like: ['q0_ro',...]",pre_fill=[])
        self.xy_elements = ExpParas("xy_elements","list",4,message="Fill in who to drive like: ['q0_xy',...]",pre_fill=[])
        self.max_evo_time = ExpParas("max_evo_time","int",3,message="evolution time maximum like: 20e-6.")
        
        # self.OSmode = ExpParas("OSmode","int",1,message="booling value set 0 for False or 1 for True, Use one-shot or not ?")
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=300)
        self.time_sampling_func = ExpParas("time_sampling_func","func",1,message="sampling function options: 'linspace', 'arange', 'logspace'.",pre_fill='linspace')
        self.time_ptsORstep = ExpParas("time_ptsORstep","int",1,message="Depends on sampling func set in step or pts.",pre_fill=100)
        self.histo_counts = ExpParas("histo_counts","int",1,message="repeat times of histogram, <101 use FPGA otherwies use while loop.",pre_fill=1)

    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):
        # show parameters it recieved
        slightly_print("\n==============================")
        eyeson_print(f"Executtion: {self.get_ExpLabel()}, {self.__class__.__name__}")
        print("\n")
        self.show_assigned_paras()
        slightly_print("==============================\n")
        

        if not self.BetaMode:
            match self.machine_type.lower():
                case 'qblox':
                    self.target_qs = list(self.max_evo_time.keys())
                    self.time_range = {}
                    for q in self.target_qs:
                        self.time_range[q] = [0, self.max_evo_time[q]]
                    
                    from qblox_drive_AS.support.ExpFrames import EnergyRelaxation
                    self.EXP = EnergyRelaxation(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                    self.EXP.SetParameters( self.time_range, self.time_sampling_func,self.time_ptsORstep, self.histo_counts,self.avg_n,execution=True)
                    self.EXP.WorkFlow()
                    eyeson_print("Raw data located:")
                    slightly_print(self.EXP.RawDataPath)
                case 'qm':
                    self.init_macro = eval(self.init_macro)
                    from exp.relaxation_time import exp_relaxation_time
                    config_obj:Configuration = self.connections[0]
                    spec:ChannelInfo = self.connections[1]
                    config = config_obj.get_config()
                    qmm, _ = spec.buildup_qmm()
                    self.EXP = exp_relaxation_time(config, qmm)
                    self.EXP.shot_num = self.avg_n
                    self.EXP.initializer = initializer(self.init_macro["time"]*1e9,mode=self.init_macro["mode"])
                    self.EXP.ro_elements = self.ro_elements
                    self.EXP.xy_elements = self.xy_elements
                    
                    self.EXP.max_time = self.max_evo_time*1e6
                    if self.time_sampling_func == "arange":
                        self.EXP.time_resolution = self.time_ptsORstep*1e6
                    elif self.time_sampling_func == "linspace":
                        self.EXP.time_resolution = self.EXP.max_time/self.time_ptsORstep
                    else:
                        raise ValueError(f"Sorry, The given sampling function = {self.time_sampling_func} is temporarily unsupported !")
                    
                    if self.histo_counts == 1:
                        self.dataset = self.EXP.run()
                        save_path = os.path.join(self.save_data_folder,f"T1relaxation_{self.JOBID}.nc")
                        
                    else:
                        from exp.repetition_measurement import RepetitionMeasurement
                        re_exp = RepetitionMeasurement()
                        re_exp.exp_list = [self.EXP]
                        re_exp.exp_name = ["T1_relaxation"]
                        self.dataset:Dataset = re_exp.run(self.histo_counts)[re_exp.exp_name[0]]
                        save_path = os.path.join(self.save_data_folder,f"T1relaxationRep_{self.JOBID}.nc")
                    
                    self.dataset.to_netcdf(save_path)

            
    
    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"][0]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)
            case 'qm':
                from exp.plotting import PainterT1Single, PainterT1Repeat
                raw_data_files = analysis_need["Data"]
                for file in raw_data_files:
                    
                    dataset = open_dataset(file)
                    for attr in dataset.attrs:
                        if not isinstance(dataset.attrs[attr], ndarray):
                            dataset.attrs[attr] = [dataset.attrs[attr]]
                    
                    folder_path, file_name = os.path.split(file)
                    if 'rep' not in file_name.lower():
                        painter = PainterT1Single()
                    else:
                        painter = PainterT1Repeat()

                    dp = DataPackager(folder_path,'pic',time_label_type="no_label")
                    figs = painter.plot(dataset,file_name.split("_")[0])
                    dp.save_figs( figs )


# C1, need qm test on sample, plot is also a concern
class XYFcalibrator(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "C1"

    def set_variables(self):
        self.init_macro = ExpParas("init_macro","dict",4,message="Make sure it's in the quotes (\"\"),initializer operation: initializer(time=400e-6,mode='wait')",pre_fill={"time":300e-6,"mode":'wait'})
        self.ro_elements = ExpParas("ro_elements","list",4,message="Fill in who to read like: ['q0_ro',...]",pre_fill=[])
        self.xy_elements = ExpParas("xy_elements","list",4,message="Fill in who to drive like: ['q0_xy',...]",pre_fill=[])
        self.virtual_detune = ExpParas("virtual_detune","int",4,message="virtual detuning like: 0.5e6",pre_fill=5e6)
        self.point_per_period = ExpParas("point_per_period","int",4,message="How many data point is in a period ?",pre_fill=20)
        self.max_period = ExpParas("max_period","int",4,message="How many period ?",pre_fill=6)
        
        self.max_evo_time = ExpParas("max_evo_time","int",3,message="QM ignore it, evolution time maximum like: 20e-6.")
        # self.OSmode = ExpParas("OSmode","int",1,message="booling value set 0 for False or 1 for True, Use one-shot or not ?")
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=500)

    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):
        # show parameters it recieved
        slightly_print("\n==============================")
        eyeson_print(f"Executtion: {self.get_ExpLabel()}, {self.__class__.__name__}")
        print("\n")
        self.show_assigned_paras()
        slightly_print("==============================\n")
        

        if not self.BetaMode:
            match self.machine_type.lower():
                case 'qblox':
                    self.target_qs = list(self.max_evo_time.keys())
                    from qblox_drive_AS.support.ExpFrames import XYFcali
                    self.EXP = XYFcali(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                    self.EXP.SetParameters( self.target_qs, self.max_evo_time[self.target_qs[0]],avg_n=self.avg_n,execution=True)
                    self.EXP.WorkFlow()
                    eyeson_print("Raw data located:")
                    slightly_print(self.EXP.RawDataPath)
                case 'qm':
                    self.init_macro = eval(self.init_macro)
                    from exp.ramsey_freq_calibration import RamseyFreqCalibration
                    config_obj:Configuration = self.connections[0]
                    spec:ChannelInfo = self.connections[1]
                    config = config_obj.get_config()
                    qmm, _ = spec.buildup_qmm()
                    self.EXP = RamseyFreqCalibration(config, qmm)
                    self.EXP.shot_num = self.avg_n
                    self.EXP.initializer = initializer(self.init_macro["time"]*1e9,mode=self.init_macro["mode"])
                    self.EXP.ro_elements = self.ro_elements
                    self.EXP.xy_elements = self.xy_elements
                    self.EXP.virtial_detune_freq = self.virtual_detune*1e-6
                    
                    self.dataset = self.EXP.run()
                    save_path = os.path.join(self.save_data_folder,f"RamseyT2_{self.JOBID}.nc")
                    self.dataset.to_netcdf(save_path)
            
    
    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"][0]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)
            case 'qm':
                from exp.ramsey_freq_calibration import plot_ana_result
                import matplotlib.pyplot as plt
                raw_data_files = analysis_need["Data"]
                for file in raw_data_files:
                    
                    dataset = open_dataset(file)
                    for attr in dataset.attrs:
                        if not isinstance(dataset.attrs[attr], ndarray):
                            dataset.attrs[attr] = [dataset.attrs[attr]]
                    evo_time = dataset.coords["time"].values
                    folder_path, file_name = os.path.split(file)
                    dp = DataPackager(folder_path,'pic',time_label_type="no_label")
                    figs = []
                    for ro_element in dataset.data_vars:
                        fig, ax = plt.subplots()
                        plot_data = dataset[ro_element].values[0]
                        plot_ana_result(evo_time,plot_data,self.EXP.virtial_detune_freq,ax)
                        save_name = f"{ro_element}_XYFcali"
                        figs.append((save_name,fig))
                        plt.close()
                    
                    dp.save_figs( figs )



# C2, need qm test on sample, plot is also a concern 
class ROFcalibrator(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "C2"

    def set_variables(self):
        self.init_macro = ExpParas("init_macro","dict",4,message="Make sure it's in the quotes (\"\"),initializer operation: initializer(time=400e-6,mode='wait')",pre_fill={"time":300e-6,"mode":'wait'})
        self.ro_elements = ExpParas("ro_elements","list",4,message="Fill in who to read like: ['q0_ro',...]",pre_fill=[])
        self.xy_elements = ExpParas("xy_elements","list",4,message="Fill in who to drive like: ['q0_xy',...]",pre_fill=[])
        self.OSmode = ExpParas("OSmode","int",4,message="booling value set 0 for False or 1 for True, Use average or one-shot ?",pre_fill=1)
        self.freq_range = ExpParas("freq_range","list",3,message="freq to span, like [-6e6, +8e6].")
        self.freq_ptsORstep = ExpParas("freq_ptsORstep","int",1,message="qblox set pts",pre_fill=100)
         
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=300)

    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):
        # show parameters it recieved
        slightly_print("\n==============================")
        eyeson_print(f"Executtion: {self.get_ExpLabel()}, {self.__class__.__name__}")
        print("\n")
        self.show_assigned_paras()
        slightly_print("==============================\n")
        
        if not self.BetaMode:
            match self.machine_type.lower():
                case 'qblox':
                    self.target_qs = list(self.freq_range.keys())
                    from qblox_drive_AS.support.ExpFrames import ROFcali
                    self.EXP = ROFcali(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                    self.EXP.SetParameters( self.freq_range, self.freq_ptsORstep,self.avg_n,execution=True)
                    self.EXP.WorkFlow()
                    eyeson_print("Raw data located:")
                    slightly_print(self.EXP.RawDataPath)
                case 'qm':
                    self.init_macro = eval(self.init_macro)
                    from exp.readout_optimization import ROFreq
                    config_obj:Configuration = self.connections[0]
                    spec:ChannelInfo = self.connections[1]
                    config = config_obj.get_config()
                    qmm, _ = spec.buildup_qmm()
                    self.EXP = ROFreq(config, qmm)
                    self.EXP.shot_num = self.avg_n
                    self.EXP.initializer = initializer(self.init_macro["time"]*1e9,mode=self.init_macro["mode"])
                    self.EXP.ro_elements = self.ro_elements
                    self.EXP.xy_elements = self.xy_elements
                    self.EXP.freq_range = (self.freq_range[0]*1e-6,self.freq_range[1]*1e-6)
                    self.EXP.freq_resolution = self.freq_ptsORstep*1e-6
                    if self.OSmode:
                        self.EXP.preprocess = "shot"
                    else:
                        self.EXP.preprocess = "ave"
                    self.dataset = self.EXP.run()
                    save_path = os.path.join(self.save_data_folder,f"ROFcali_{self.JOBID}.nc")
                    self.dataset.to_netcdf(save_path)


    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"][0]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)
            case 'qm':
                from exp.plotting import plot_and_save_readout_freq
                raw_data_files = analysis_need["Data"]
                for file in raw_data_files:
                    
                    dataset = open_dataset(file)
                    for attr in dataset.attrs:
                        if not isinstance(dataset.attrs[attr], ndarray):
                            dataset.attrs[attr] = [dataset.attrs[attr]]
                    
                    folder_path, file_name = os.path.split(file)
                    dp = DataPackager(folder_path,'pic',time_label_type="no_label")
                    
                    figs = plot_and_save_readout_freq(dataset,self.EXP)

                    dp.save_figs( figs )

# C3, need qm test on sample, plot is also a concern 
class ROLcalibrator(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "C3"

    def set_variables(self):
        self.init_macro = ExpParas("init_macro","dict",4,message="Make sure it's in the quotes (\"\"),initializer operation: initializer(time=400e-6,mode='wait')",pre_fill={"time":300e-6,"mode":'wait'})
        self.ro_elements = ExpParas("ro_elements","list",4,message="Fill in who to read like: ['q0_ro',...]",pre_fill=[])
        self.xy_elements = ExpParas("xy_elements","list",4,message="Fill in who to drive like: ['q0_xy',...]",pre_fill=[])
        self.amp_coef_range = ExpParas("amp_coef_range","list",3,message="ro-amp coef, rule: [start, end].")
        self.coef_ptsORstep = ExpParas("coef_ptsORstep","int",1,message="qblox set pts",pre_fill=100)
        # self.OSmode = ExpParas("OSmode","int",1,message="booling value set 0 for False or 1 for True, Use one-shot or not ?")
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=300)

    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):
        # show parameters it recieved
        slightly_print("\n==============================")
        eyeson_print(f"Executtion: {self.get_ExpLabel()}, {self.__class__.__name__}")
        print("\n")
        self.show_assigned_paras()
        slightly_print("==============================\n")
        

        if not self.BetaMode:
            match self.machine_type.lower():
                case 'qblox':
                    self.target_qs = list(self.amp_coef_range.keys())
                    from qblox_drive_AS.support.ExpFrames import ROLcali
                    self.EXP = ROLcali(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                    self.EXP.SetParameters( self.amp_coef_range, 'linspace', self.coef_ptsORstep,self.avg_n,execution=True)
                    self.EXP.WorkFlow()
                    eyeson_print("Raw data located:")
                    slightly_print(self.EXP.RawDataPath)
                case 'qm':
                    self.init_macro = eval(self.init_macro)
                    from exp.readout_optimization import power_dep_signal
                    config_obj:Configuration = self.connections[0]
                    spec:ChannelInfo = self.connections[1]
                    config = config_obj.get_config()
                    qmm, _ = spec.buildup_qmm()
                    init_macro = initializer(self.init_macro["time"]*1e9,mode=self.init_macro["mode"])
                    self.dataset = power_dep_signal(self.amp_coef_range,self.coef_ptsORstep,self.xy_elements,self.ro_elements,self.avg_n,config,qmm,init_macro)
                    save_path = os.path.join(self.save_data_folder,f"ROLcali_{self.JOBID}.nc")
                    self.dataset.to_netcdf(save_path)


    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"][0]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)
            case 'qm':    
                from exp.plotting import plot_and_save_readout_amp
                raw_data_files = analysis_need["Data"]
                for file in raw_data_files:
                    
                    dataset = open_dataset(file)
                    for attr in dataset.attrs:
                        if not isinstance(dataset.attrs[attr], ndarray):
                            dataset.attrs[attr] = [dataset.attrs[attr]]
                    
                    folder_path, file_name = os.path.split(file)
                    dp = DataPackager(folder_path,'pic',time_label_type="no_label")
                    
                    figs = plot_and_save_readout_amp(dataset)

                    dp.save_figs( figs )

# C4, QM version too old, skip 
class PIampCalibrator(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "C4"

    def set_variables(self):
        self.piamp_coef_range = ExpParas("piamp_coef_range","list",3,message="pi-amp coef, rule: [start, end].")
        self.coef_ptsORstep = ExpParas("coef_ptsORstep","int",1,message="qblox set pts",pre_fill=100)
        self.pi_pair_num = ExpParas("pi_pair_num","list",1,message="How many pi-pulse pair ? qblox please assign two value like [3,5], qm only one required like [3]")
        # self.OSmode = ExpParas("OSmode","int",1,message="booling value set 0 for False or 1 for True, Use one-shot or not ?")
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=300)

    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):
        # show parameters it recieved
        slightly_print("\n==============================")
        eyeson_print(f"Executtion: {self.get_ExpLabel()}, {self.__class__.__name__}")
        print("\n")
        self.show_assigned_paras()
        slightly_print("==============================\n")
        
        if not self.BetaMode:
        
            match self.machine_type.lower():
                case 'qblox':
                    self.target_qs = list(self.piamp_coef_range.keys())
                    from qblox_drive_AS.support.ExpFrames import PiAcali
                    self.EXP = PiAcali(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                    self.EXP.SetParameters( self.piamp_coef_range, 'linspace', self.coef_ptsORstep,self.pi_pair_num,self.avg_n,execution=True)
                    self.EXP.WorkFlow()
                    eyeson_print("Raw data located:")
                    slightly_print(self.EXP.RawDataPath)

                
    
    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"][0]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)

# C5, QM same as C4
class halfPIampCalibrator(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "C5"

    def set_variables(self):
        self.half_pi_coef_range = ExpParas("half_pi_coef_range","list",3,message=" half pi-amp coef, span around 0.5, rule: [start, end].")
        self.coef_ptsORstep = ExpParas("coef_ptsORstep","int",1,message="qblox set pts",pre_fill=100)
        self.half_pi_quadruple_num = ExpParas("half_pi_quadruple_num","list",1,message="How many half pi-pulse quadruples ? qblox please assign two value like [3,5], qm only one required like [3]")
        # self.OSmode = ExpParas("OSmode","int",1,message="booling value set 0 for False or 1 for True, Use one-shot or not ?")
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=300)

    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):
        # show parameters it recieved
        slightly_print("\n==============================")
        eyeson_print(f"Executtion: {self.get_ExpLabel()}, {self.__class__.__name__}")
        print("\n")
        self.show_assigned_paras()
        slightly_print("==============================\n")
        
        if not self.BetaMode:
            match self.machine_type.lower():
                case 'qblox':
                    from qblox_drive_AS.support.ExpFrames import hPiAcali
                    self.target_qs = list(self.half_pi_coef_range.keys())
                    self.EXP = hPiAcali(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                    self.EXP.SetParameters( self.half_pi_coef_range, 'linspace', self.coef_ptsORstep,self.half_pi_quadruple_num,self.avg_n,execution=True)
                    self.EXP.WorkFlow()
                    eyeson_print("Raw data located:")
                    slightly_print(self.EXP.RawDataPath)

            
    
    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"][0]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)

# C6, didn't see it in QM 
class DragCoefCali(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "C6"

    def set_variables(self):
        self.drag_coef_range = ExpParas("drag_coef_range","list",3,message=" DRAG coef, rule: [start, end].",pre_fill=[-2,2])
        self.coef_ptsORstep = ExpParas("coef_ptsORstep","int",1,message="qblox set pts",pre_fill=50)
        # self.OSmode = ExpParas("OSmode","int",1,message="booling value set 0 for False or 1 for True, Use one-shot or not ?")
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=300)

    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):
        # show parameters it recieved
        slightly_print("\n==============================")
        eyeson_print(f"Executtion: {self.get_ExpLabel()}, {self.__class__.__name__}")
        print("\n")
        self.show_assigned_paras()
        slightly_print("==============================\n")
        

        if not self.BetaMode:
            match self.machine_type.lower():
                case 'qblox':
                    from qblox_drive_AS.support.ExpFrames import DragCali
                    self.target_qs = list(self.drag_coef_range.keys())
                    self.EXP = DragCali(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                    self.EXP.SetParameters( self.drag_coef_range, 'linspace', self.coef_ptsORstep,self.avg_n,execution=True)
                    self.EXP.WorkFlow()
                    eyeson_print("Raw data located:")
                    slightly_print(self.EXP.RawDataPath)

            
    
    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"][0]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)


# A1, qm core meas-object need to be re-built, and then test on samples
class ZgateRelaxation(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "A1"

    def set_variables(self):
        self.init_macro = ExpParas("init_macro","dict",4,message="Make sure it's in the quotes (\"\"),initializer operation: initializer(time=400e-6,mode='wait')",pre_fill={"time":300e-6,"mode":'wait'})
        self.ro_elements = ExpParas("ro_elements","list",4,message="Fill in who to read like: ['q0_ro',...]",pre_fill=[])
        self.xy_elements = ExpParas("xy_elements","list",4,message="Fill in who to drive like: ['q0_xy',...]",pre_fill=[])
        self.z_elements = ExpParas("z_elements","list",4,message="Fill in who to bias like: ['q0_z',...]",pre_fill=[])
        self.max_evo_time = ExpParas("max_evo_time","int",3,message="evolution time maximum like: 20e-6.")
        
        self.bias_range = ExpParas("bias_range","list",2,message="rule: [start, end, pts/step], QM please set in step.")
        # self.OSmode = ExpParas("OSmode","int",1,message="booling value set 0 for False or 1 for True, Use one-shot or not ?")
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=300)
        self.prepare_Excited = ExpParas("prepare_Excited","int",1,message="QM please ignore it, booling value set 0 for False or 1 for True, Prepare the excited state first ?",pre_fill=1)
        self.time_sampling_func = ExpParas("time_sampling_func","func",1,message="sampling function options: 'linspace', 'arange'.",pre_fill='linspace')
        self.time_ptsORstep = ExpParas("time_ptsORstep","int",1,message="Depends on sampling func set in step or pts.",pre_fill=100)
        self.histo_counts = ExpParas("histo_counts","int",1,message="How many times you want to repeat ? If you don't want it stop, set a very large number like 5e9 please.",pre_fill=1)
    

    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):
        # show parameters it recieved
        slightly_print("\n==============================")
        eyeson_print(f"Executtion: {self.get_ExpLabel()}, {self.__class__.__name__}")
        print("\n")
        self.show_assigned_paras()
        slightly_print("==============================\n")
        
        if not self.BetaMode:
            match self.machine_type.lower():
                case 'qblox':
                    from qblox_drive_AS.support.ExpFrames import ZgateEnergyRelaxation
                    self.target_qs = list(self.max_evo_time.keys())
                    self.time_range = {}
                    for q in self.target_qs:
                        self.time_range[q] = [0, self.max_evo_time[q]]
                    self.EXP = ZgateEnergyRelaxation(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                    self.EXP.SetParameters( self.time_range, self.time_sampling_func,self.bias_range,self.prepare_Excited,'linspace',self.time_ptsORstep,True,self.avg_n,execution=True)
                    self.EXP.WorkFlow(int(self.histo_counts))
                    eyeson_print("Raw data located:")
                    slightly_print(self.EXP.RawDataPath)
                case 'qm':
                    from exp.z_pulse_relaxation_time import z_pulse_relaxation_time
                    self.init_macro = eval(self.init_macro)
                    config_obj:Configuration = self.connections[0]
                    spec:ChannelInfo = self.connections[1]
                    config = config_obj.get_config()
                    qmm, _ = spec.buildup_qmm()
                    self.EXP = z_pulse_relaxation_time(config, qmm)
                    self.EXP.ro_elements = self.ro_elements
                    self.EXP.xy_elements = self.xy_elements
                    self.EXP.z_elements = self.z_elements
                    self.EXP.max_time = self.max_evo_time*1e6
                    self.EXP.flux_range= [self.bias_range[0], self.bias_range[1]] # list
                    self.EXP.flux_resolution = self.bias_range[-1]
                    if self.time_sampling_func == 'arange':
                        self.EXP.time_resolution = self.time_ptsORstep*1e6
                    else:
                        self.EXP.time_resolution = self.EXP.max_time/self.time_ptsORstep

                    self.EXP.initializer = initializer(self.init_macro["time"]*1e9,mode=self.init_macro["mode"])
                    self.dataset = self.EXP.run( self.avg_n )
                    save_path = os.path.join(self.save_data_folder,f"T1Spectrum_{self.JOBID}.nc")
                    self.dataset.to_netcdf(save_path)

        
    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"][0]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)
            case 'qm':
                from exp.plotting import plot_and_save_T1_spectrum
                raw_data_files = analysis_need["Data"]
                for file in raw_data_files:
                    
                    dataset = open_dataset(file)
                    for attr in dataset.attrs:
                        if not isinstance(dataset.attrs[attr], ndarray):
                            dataset.attrs[attr] = [dataset.attrs[attr]]
                    
                    time = dataset.coords["time"].values
                    flux = dataset.coords["z_voltage"].values

                    folder_path, file_name = os.path.split(file)
                    dp = DataPackager(folder_path,'pic',time_label_type="no_label")
                    figs = plot_and_save_T1_spectrum(dataset,time,flux)
                    dp.save_figs( figs )


# A2, need qm test on sample
class TimeMonitor(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "A2"

    def set_variables(self):
        self.init_macro = ExpParas("init_macro","dict",4,message="Make sure it's in the quotes (\"\"),initializer operation: initializer(time=400e-6,mode='wait')",pre_fill={"time":300e-6,"mode":'wait'})
        self.ro_elements = ExpParas("ro_elements","list",4,message="Fill in who to read like: ['q0_ro',...]",pre_fill=[])
        self.xy_elements = ExpParas("xy_elements","list",4,message="Fill in who to drive like: ['q0_xy',...]",pre_fill=[])

        self.T1_max_evo_time = ExpParas("T1_max_evo_time","int",3,message="T1 evolution time maximun like 60e-6. If you don't wanna do T1 leave it 0.")
        self.T2_max_evo_time = ExpParas("T2_max_evo_time","int",3,message="T2 evolution time maximum like: 50e-6. If you don't wanna do T2 leave it 0.")
        self.time_sampling_func = ExpParas("time_sampling_func","func",1,message="sampling function options: 'linspace', 'arange', 'logspace', **QM only use 'arange'**.",pre_fill='linspace')
        self.time_ptsORstep = ExpParas("time_ptsORstep","int",1,message="Depends on sampling func set in step or pts. **QM always sets the resolution**",pre_fill=100)
        # self.OSmode = ExpParas("OSmode","int",1,message="booling value set 0 for False or 1 for True, Use one-shot or not ?")
        self.echo_pi_num = ExpParas("echo_pi_num","int",2,message="How many pi-pulse between Ramsey ? 0 for Ramsey T2, 1 for SpinEcho T2, more for CPMG (Qblox only).",pre_fill=0)
        self.virtual_detune = ExpParas("virtual_detune","float",1,message="Only while doing Ramsey, how many driving detuning ? otherwise set None",pre_fill=0)
        self.OS_shots = ExpParas("OS_shots","int",1,message="Shot number for OneSoht exp. If you don't wanna do OneShot leave it 0.",pre_fill=10000)
        self.histo_counts = ExpParas("histo_counts","int",1,message="repeat times. Qblox always uses while-loop",pre_fill=1)
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=500)

    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):
        # show parameters it recieved
        slightly_print("\n==============================")
        eyeson_print(f"Executtion: {self.get_ExpLabel()}, {self.__class__.__name__}")
        print("\n")
        self.show_assigned_paras()
        slightly_print("==============================\n")
    
        if not self.BetaMode:
            match self.machine_type.lower():
                case 'qblox':
                    from qblox_drive_AS.support.ExpFrames import QubitMonitor

                    self.EXP = QubitMonitor(QD_path=self.connections[0],save_dir=self.save_data_folder)
                    # T1 settings
                    self.EXP.T1_time_range = {}
                    for q in self.T1_max_evo_time:
                        if self.T1_max_evo_time[q] != 0:
                            self.EXP.T1_time_range[q] = [0, self.T1_max_evo_time[q]]
                    # T2 settings
                    self.EXP.T2_time_range = {}
                    for q in self.T2_max_evo_time:
                        if self.T2_max_evo_time[q] != 0:
                            self.EXP.T2_time_range[q] = [0, self.T2_max_evo_time[q]]
                    self.EXP.a_little_detune_Hz = self.virtual_detune  # for all qubit in T2_time_range. Set None if you do SpinEcho or CPMG
                    self.EXP.echo_pi_num = self.echo_pi_num
                    # SingleShot settings, skip if 0 shot
                    self.EXP.OS_shots = self.OS_shots     
                    self.EXP.OS_target_qs = list(set(list(self.EXP.T1_time_range.keys())+list(self.EXP.T2_time_range.keys())))
                    # T1, T2 shared settings
                    self.EXP.time_sampling_func =  self.time_sampling_func
                    self.EXP.time_ptsORstep = self.time_ptsORstep
                    self.EXP.AVG = self.avg_n

                    print("T1: ",self.EXP.T1_time_range)
                    print("T2: ",self.EXP.T2_time_range)
                    print("OS: ",self.EXP.OS_target_qs)


                    self.EXP.StartMonitoring() # while loop
                case 'qm':
                    self.init_macro = eval(self.init_macro)
                    from exp.repetition_measurement import RepetitionMeasurement
                    self.EXP = RepetitionMeasurement()
                    self.EXP.exp_list = []
                    self.EXP.exp_name = []
                    config_obj:Configuration = self.connections[0]
                    spec:ChannelInfo = self.connections[1]
                    config = config_obj.get_config()
                    qmm, _ = spec.buildup_qmm()
                    if int(self.T1_max_evo_time) != 0:
                        from exp.relaxation_time import exp_relaxation_time

                        EXP = exp_relaxation_time(config, qmm)
                        EXP.max_time = self.T1_max_evo_time*1e6
                        self.EXP.exp_list.append(EXP)
                        self.EXP.exp_name.append("T1Relaxation")

                    if int(self.T2_max_evo_time) != 0:
                        if self.echo_pi_num == 0 :
                            from exp.ramsey import Ramsey
                            EXP = Ramsey(config, qmm)
                            EXP.max_time = self.T2_max_evo_time*1e6
                            EXP.virtual_detune = self.virtual_detune*1e-6
                            self.EXP.exp_name.append("RamseyT2")
                        else:
                            from exp.single_spin_echo import SpinEcho
                            EXP = SpinEcho(config, qmm)
                            EXP.time_range = (40, self.T2_max_evo_time*1e6)
                            self.EXP.exp_name.append("SpinEcho")
                        self.EXP.exp_list.append(EXP)
                    
                    if int(self.OS_shots) != 0:
                        print("QM didn't support SingleShot meas in the time-monitor !")
                        # self.EXP.exp_name.append("OneShot")


                    for EXP in self.EXP.exp_list:
                    
                        EXP.shot_num = self.avg_n
                        EXP.initializer = initializer(self.init_macro["time"]*1e9,mode=self.init_macro["mode"])
                        EXP.ro_elements = self.ro_elements
                        EXP.xy_elements = self.xy_elements
                        if self.time_sampling_func == "arange":
                            EXP.time_resolution = self.time_ptsORstep*1e6
                        else:
                            raise ValueError(f"Sorry, The given sampling function = {self.time_sampling_func} is temporarily unsupported !")
    
                    self.dataset = self.EXP.run(self.histo_counts,self.save_data_folder)
                    
                    for name in self.EXP.exp_name:
                        save_path = os.path.join(self.save_data_folder,f"{name}Rep_{self.JOBID}.nc") # if file name changed, analysis also need to be modified.
                        dataset:Dataset = self.dataset[name]
                        dataset.to_netcdf(save_path)

    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"][0]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.basename(name).split(".")[-1]=='pkl'][0]
                self.EXP.TimeMonitor_analysis(New_QD_path=QD_path,New_data_file=data_file)
            case 'qm':
                from exp.plotting import PainterT1Single, PainterT1Repeat, PainterT2Ramsey, PainterT2Repeat, PainterT2SpinEcho

                raw_data_files = analysis_need["Data"]
                dp = DataPackager(os.path.split(raw_data_files[0])[0],'pic',time_label_type="no_label")
                
                rep_files = [file for file in raw_data_files if "rep" in os.path.basename(file).lower()]
                
                # If "Rep" is in a file name that means this monitor is done and closed by itself. Otherwise, there will not a file named includes "Rep". 
                rep_ana, ana_targets = [False,raw_data_files] if len(rep_files) == 0 else [True, rep_files]

                for file in ana_targets:
                    file:str
                    skip_ana:bool = False
                    dataset = open_dataset(file)
                    for attr in dataset.attrs:
                        if not isinstance(dataset.attrs[attr], ndarray):
                            dataset.attrs[attr] = [dataset.attrs[attr]]
                    
                    
                    if rep_ana:
                        exp_name:str = os.path.basename(file.lower()).split("rep")[0]
                        match exp_name:
                            case "t1relaxation":
                                painter = PainterT1Repeat()
                            case "ramseyt2" | "spinecho":
                                painter = PainterT2Repeat()
                            case _:
                                skip_ana = True
                                print(f"Skip a recieved unexpected exp name = {exp_name}")
                        
                    else:
                        exp_name:str = os.path.basename(file.lower()).split("_")[0] # check into exp.repetition_measurement.RepetitionMeasurement
                        match exp_name:
                            case "t1relaxation":
                                painter = PainterT1Single()
                            case "ramseyt2":
                                painter = PainterT2Ramsey()
                            case "spinecho":
                                painter = PainterT2SpinEcho()
                            case _:
                                skip_ana = True
                                print(f"Skip a recieved unexpected exp name = {exp_name}")

                    if not skip_ana:
                        figs = painter.plot(dataset,os.path.basename(file.lower()).split("_")[0])
                        dp.save_figs( figs )
                

# R1b
class GatePhaErrorEstim(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "R1b"

    def set_variables(self):
        self.MaxGate_num = ExpParas("MaxGate_num","int",2,message="The maximum gate number to apply.",pre_fill=350)
        self.OneShot_shots = ExpParas("OneShot_shots","int",1,message="SingleShot total shots.",pre_fill=10000)
        self.use_uncali_waveform = ExpParas("use_uncali_waveform","int",1,message="booling value set 0 for False or 1 for True, if True won't use calibrated Drag coef.",pre_fill=0)
        # self.OSmode = ExpParas("OSmode","int",1,message="booling value set 0 for False or 1 for True, Use one-shot or not ?")
        # self.avg_n = ExpParas("avg_n","int",1,pre_fill=300)

    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):
        # show parameters it recieved
        slightly_print("\n==============================")
        eyeson_print(f"Executtion: {self.get_ExpLabel()}, {self.__class__.__name__}")
        print("\n")
        self.show_assigned_paras()
        slightly_print("==============================\n")
        
        if not self.BetaMode:
            match self.machine_type.lower():
                case 'qblox':
                    from qblox_drive_AS.support.ExpFrames import XGateErrorTest
                    self.EXP = XGateErrorTest(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                    self.EXP.SetParameters( self.target_qs, self.OneShot_shots, self.MaxGate_num, execution=True, use_untrained_wf=self.use_uncali_waveform)
                    self.EXP.WorkFlow()
                    eyeson_print("Raw data located:")
                    slightly_print(self.EXP.RawDataPath)
                case 'qm':
                    raise SystemError(f"QM didn't support X-Gate phase-error test !")

            
    
    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"][0]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)













