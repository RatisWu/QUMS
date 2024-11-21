
import inspect, os, shutil
from datetime import datetime
from Association.Soul import ExpParas, ExpSpirit
from qspec.channel_info import ChannelInfo
from config_component.configuration import Configuration
from ab.QM_config_dynamic import initializer
from qblox_drive_AS.support import QDmanager, Data_manager
from exp.save_data import DataPackager
from qblox_drive_AS.support.UserFriend import *
from Association.ExclusiveNames import ConfigUniqueName


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

        

# S1
class CavitySearch(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S1"

    def set_variables(self):
        self.freq_range = ExpParas("freq_range","list",3,message="QM span given value from LO, Qblox sweep what freq you give. rule: [start, end]")
        self.freq_ptsORstep = ExpParas("freq_ptsORstep","float",1,message="According to sampling function, use step or pts for all qubit")
        self.avg_n = ExpParas("avg_n","int",1)
        self.freq_sampling_func = ExpParas("freq_sampling_func","func",1,message="sampling function options: 'linspace', 'arange' ")


    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):

        self.target_qs = list(self.freq_range.keys())
        match self.machine_type.lower():
            case 'qblox':
                from qblox_drive_AS.support.ExpFrames import Zoom_CavitySearching
                self.EXP = Zoom_CavitySearching(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                self.EXP.SetParameters( self.freq_range,self.freq_ptsORstep,self.avg_n,execution=True)
                self.EXP.WorkFlow()
                eyeson_print("Raw data located:")
                slightly_print(self.EXP.RawDataPath)

            case 'qm':
                from exp.rofreq_sweep import ROFreqSweep
                config_obj:Configuration = self.connections[0]
                spec:ChannelInfo = self.connections[1]
                config = config_obj.get_config()
                qmm, _ = spec.buildup_qmm()
                my_exp = ROFreqSweep(config, qmm)
                ro_q = my_exp.ro_elements[0]
                my_exp.initializer = initializer(2000,mode='wait')
                """ freq unit in MHz """
                my_exp.freq_range = (float(self.freq_range[ro_q][0])*1e-6, float(self.freq_range[ro_q][1])*1e-6)
                print(f"freq range= {my_exp.freq_range}")
                if self.freq_sampling_func == 'arange':
                    my_exp.resolution = self.freq_ptsORstep*1e-6
                    print(f'arange ,step= {my_exp.resolution}')
                else:
                    my_exp.resolution = (abs(float(self.freq_range[ro_q][1])-float(self.freq_range[ro_q][0]))/float(self.freq_ptsORstep))*1e-6
                self.raw_data_path:str = os.path.join(self.save_data_folder,f"ROFreqSweep_{self.JOBID}.nc")
                print(f"raw at= {self.raw_data_path}")
                self.dataset = my_exp.run( int(self.avg_n))
                self.dataset.to_netcdf(self.raw_data_path,engine='netcdf4')
    
    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)

            case 'qm':
                import numpy as np
                import matplotlib.pyplot as plt
                idata = self.dataset[self.target_qs[0]].sel(mixer='I').values
                qdata = self.dataset[self.target_qs[0]].sel(mixer='Q').values
                zdata = idata+1j*qdata
                plt.plot(self.dataset.coords["frequency"].values,np.abs(zdata))
                plt.savefig(os.path.join(self.save_data_folder,f"ROFreqSweep_{self.JOBID}.png"))
                plt.close()

# S1b
class BbCavitySearch(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S1b"

    def set_variables(self):
        self.freq_range = ExpParas("freq_range","list",3,message="Qblox only, LO sweeps what freq range you give. rule: [start, end]")
        self.avg_n = ExpParas("avg_n","int",1)
        self.freq_sampling_func = ExpParas("freq_sampling_func","func",1,message="sampling function options: 'linspace', 'arange' ")
        self.freq_ptsORstep = ExpParas("freq_ptsORstep","float",1,message="According to sampling function, use step or pts for all qubit")
        # self.bias_range = ExpParas("bias_range","list",2)  # <- only for test
        # self.bias_sampling_func = ExpParas("bias_sampling_func","func",1) # <- only for test.

    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):
        if self.machine_type.lower() == 'qm':
            raise SystemError(f"QM didn't support LO-sweeping Cavity Searching !")
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
    
    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)

# S2
class PowerCavity(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S2"

    def set_variables(self):
        self.freq_range = ExpParas("freq_range","list",3,message="Values to span. rule: [start, end]")
        self.freq_ptsORstep = ExpParas("freq_ptsORstep","int",1,message="Depends on Freq sampling func set in step or pts.")
        self.avg_n = ExpParas("avg_n","int",1)
        self.power_range = ExpParas("power_range","list",2,message="rule: [start, end, pts/step], QM please set in step.")
        self.freq_sampling_func = ExpParas("freq_sampling_func","func",1,message="sampling function options: 'linspace', 'arange'.")
        self.power_sampling_func = ExpParas("power_sampling_func","func",1,message="sampling function options: 'linspace', 'arange', 'logspace'. QM please use 'logspace'.")


    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):

        self.target_qs = list(self.freq_range.keys())
        match self.machine_type.lower():
            case 'qblox':
                from qblox_drive_AS.support.ExpFrames import PowerCavity
                self.EXP = PowerCavity(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                self.EXP.SetParameters(self.freq_range, self.power_range, self.power_sampling_func, self.freq_ptsORstep,self.avg_n,execution=True)
                self.EXP.WorkFlow()
                eyeson_print("Raw data located:")
                slightly_print(self.EXP.RawDataPath)

            case 'qm':
                from exp.rofreq_sweep_power_dep import ROFreqSweepPowerDep
                config_obj:Configuration = self.connections[0]
                spec:ChannelInfo = self.connections[1]
                config = config_obj.get_config()
                qmm, _ = spec.buildup_qmm()
                my_exp = ROFreqSweepPowerDep(config, qmm)
                my_exp.ro_elements = list(self.freq_range.keys())
                ro_q = my_exp.ro_elements[0]
                my_exp.initializer = initializer(2000,mode='wait')
                """ freq unit in MHz """
                my_exp.freq_range = (float(self.freq_range[ro_q][0])*1e-6, float(self.freq_range[ro_q][1])*1e-6)
                print(f"freq range= {my_exp.freq_range}")
                if self.freq_sampling_func == 'arange':
                    my_exp.freq_resolution = self.freq_ptsORstep*1e-6
                    print(f'arange ,step= {my_exp.freq_resolution}')
                else:
                    my_exp.freq_resolution = (abs(float(self.freq_range[ro_q][1])-float(self.freq_range[ro_q][0]))/float(self.freq_ptsORstep))*1e-6
                """ power """
                if self.power_sampling_func in ['linspace','logspace']:
                    my_exp.amp_scale = self.power_sampling_func[:3]
                else:
                    my_exp.amp_scale = 'log'
                my_exp.amp_mod_range = (self.power_range[0],self.power_range[1])
                self.folder_label = "power_dep_resonator"
                self.dataset = my_exp.run( int(self.avg_n))
                self.dp = DataPackager( self.save_data_folder, self.folder_label )
                self.dp.save_nc(self.dataset,self.folder_label)
    
    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)

            case 'qm':
                from exp.plotting import PainterPowerDepRes
                painter = PainterPowerDepRes()
                figs = painter.plot(self.dataset,self.folder_label)
                self.dp.save_figs( figs )

# S2b
class DressedCavityFit(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S2b"

    def set_variables(self):
        self.freq_range = ExpParas("freq_range","list",3,message="QM span given value from LO, Qblox sweep what freq you give. rule: [start, end]")
        self.RO_amp = ExpParas("RO_amp","float",3,message=" A single value.")
        self.freq_ptsORstep = ExpParas("freq_ptsORstep","float",1,message="According to sampling function, use step or pts for all qubit")
        self.avg_n = ExpParas("avg_n","int",1)
        self.freq_sampling_func = ExpParas("freq_sampling_func","func",1,message="sampling function options: 'linspace', 'arange' ")


    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):

        self.target_qs = list(self.freq_range.keys())
        match self.machine_type.lower():
            case 'qblox':
                from qblox_drive_AS.support.ExpFrames import Dressed_CavitySearching
                self.EXP = Dressed_CavitySearching(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                self.EXP.SetParameters( self.freq_range,self.RO_amp,self.freq_ptsORstep,self.avg_n,execution=True)
                self.EXP.WorkFlow()
                eyeson_print("Raw data located:")
                slightly_print(self.EXP.RawDataPath)

    
    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)

# S3
class FluxCavity(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S3"

    def set_variables(self):
        self.freq_range = ExpParas("freq_range","list",3,message="Values to span. rule: [start, end]")
        self.freq_ptsORstep = ExpParas("freq_ptsORstep","int",1,message="Depends on Freq sampling func set in step or pts.")
        self.avg_n = ExpParas("avg_n","int",1)
        self.flux_range = ExpParas("flux_range","list",2,message="rule: [start, end, pts/step], QM please set in step.")
        self.bias_targets = ExpParas("bias_targets","list",2,message="If you want bias on coupler, please fill it in like ['c0', ...]. Otherwise leave [].")
        self.freq_sampling_func = ExpParas("freq_sampling_func","func",1,message="sampling function options: 'linspace', 'arange'.")
        self.flux_sampling_func = ExpParas("flux_sampling_func","func",1,message="sampling function options: 'linspace', 'arange'.")


    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):

        self.target_qs = list(self.freq_range.keys())
        match self.machine_type.lower():
            case 'qblox':
                from qblox_drive_AS.support.ExpFrames import FluxCavity,FluxCoupler
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

            
    
    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)

# S3b
class GroundPositioning(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S3b"

    def set_variables(self):
        self.RO_amp_factor = ExpParas("RO_amp_factor","float",3,message="new RO-amp = old RO-amp * factor")
        self.shots = ExpParas("shots","int",1)


    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):

        self.target_qs = list(self.RO_amp_factor.keys())
        match self.machine_type.lower():
            case 'qblox':
                from qblox_drive_AS.support.ExpFrames import IQ_references
                self.EXP = IQ_references(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                self.EXP.SetParameters( self.RO_amp_factor,self.shots,execution=True)
                self.EXP.WorkFlow()
                eyeson_print("Raw data located:")
                slightly_print(self.EXP.RawDataPath)

    
    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)

# S4
class FluxQubitSpectrum(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S4"

    def set_variables(self):
        self.freq_range = ExpParas("freq_range","list",3,message="Values to span. rule: [start, end] like: [-300e6, +200e6].")
        self.freq_ptsORstep = ExpParas("freq_ptsORstep","int",1,message="Depends on Freq sampling func set in step or pts.")
        self.bias_targets = ExpParas("bias_targets","list",2,message="Must be fill, what element will be biased, like ['q0','q1','c0', ...].") 
        self.avg_n = ExpParas("avg_n","int",1)
        self.flux_range = ExpParas("flux_range","list",2,message="rule: [start, end, pts/step].")
        self.freq_sampling_func = ExpParas("freq_sampling_func","func",1,message="sampling function options: 'linspace', 'arange'.")
        self.flux_sampling_func = ExpParas("flux_sampling_func","func",1,message="sampling function options: 'linspace', 'arange', 'logspace'.")


    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):

        self.target_qs = list(self.freq_range.keys())
        match self.machine_type.lower():
            case 'qblox':
                from qblox_drive_AS.support.ExpFrames import FluxQubit
                self.EXP = FluxQubit(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                self.EXP.SetParameters(self.freq_range, self.bias_targets, self.flux_range, self.flux_sampling_func, self.freq_ptsORstep,self.avg_n,execution=True)
                self.EXP.WorkFlow()
                eyeson_print("Raw data located:")
                slightly_print(self.EXP.RawDataPath)

            
    
    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
    
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)

# S4b
class Power2tone(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S4b"

    def set_variables(self):
        self.freq_range = ExpParas("freq_range","list",3,message="Values to sweep. rule: [start, end] like: [4.2e9, 4.7e9], or [0] calculate a advise value by system.")
        self.freq_ptsORstep = ExpParas("freq_ptsORstep","int",1,message="Depends on Freq sampling func set in step or pts.")
        self.ROXYoverlap = ExpParas("ROXYoverlap","int",1,message="booling value set 0 for False or 1 for True, RO-XY overlap or not ?")
        self.avg_n = ExpParas("avg_n","int",1)
        self.power_range = ExpParas("power_range","list",2,message="rule: [start, end, pts/step] or [a fixed value].")
        self.freq_sampling_func = ExpParas("freq_sampling_func","func",1,message="sampling function options: 'linspace', 'arange'.")
        self.power_sampling_func = ExpParas("power_sampling_func","func",1,message="sampling function options: 'linspace', 'arange', 'logspace'.")


    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):

        self.target_qs = list(self.freq_range.keys())
        match self.machine_type.lower():
            case 'qblox':
                from qblox_drive_AS.support.ExpFrames import PowerConti2tone
                self.EXP = PowerConti2tone(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                self.EXP.SetParameters(self.freq_range, self.power_range, self.power_sampling_func, self.freq_ptsORstep,self.avg_n,self.ROXYoverlap,execution=True)
                self.EXP.WorkFlow()
                eyeson_print("Raw data located:")
                slightly_print(self.EXP.RawDataPath)

            
    
    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)






































