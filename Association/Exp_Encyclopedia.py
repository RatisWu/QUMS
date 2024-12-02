
import os
from Association.Soul import ExpParas, ExpSpirit
from qspec.channel_info import ChannelInfo
from config_component.configuration import Configuration
from ab.QM_config_dynamic import initializer
from exp.save_data import DataPackager
from qblox_drive_AS.support.UserFriend import *




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
        self.freq_ptsORstep = ExpParas("freq_ptsORstep","float",1,message="According to sampling function, use step or pts for all qubit",pre_fill=100)
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=100)
        self.freq_sampling_func = ExpParas("freq_sampling_func","func",1,message="sampling function options: 'linspace', 'arange'.",pre_fill='linspace')


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
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=100)
        self.freq_sampling_func = ExpParas("freq_sampling_func","func",1,message="sampling function options: 'linspace', 'arange'.",pre_fill='linspace')
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
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=200)
        self.power_range = ExpParas("power_range","list",2,message="rule: [start, end, pts/step], QM please set in step.",pre_fill=[0,0.6,30])
        self.freq_sampling_func = ExpParas("freq_sampling_func","func",1,message="sampling function options: 'linspace', 'arange'.",pre_fill='linspace')
        self.power_sampling_func = ExpParas("power_sampling_func","func",1,message="sampling function options: 'linspace', 'arange', 'logspace'. QM please use 'logspace'.",pre_fill='linspace')


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
        self.freq_ptsORstep = ExpParas("freq_ptsORstep","float",1,message="According to sampling function, use step or pts for all qubit",pre_fill=100)
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=100)
        self.freq_sampling_func = ExpParas("freq_sampling_func","func",1,message="sampling function options: 'linspace', 'arange',",pre_fill='linspace')


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
                print(f"QD @ {QD_path}")
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
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=300)
        self.flux_range = ExpParas("flux_range","list",2,message="rule: [start, end, pts/step], QM please set in step.")
        self.bias_targets = ExpParas("bias_targets","list",2,message="If you want bias on coupler, please fill it in like ['c0', ...]. Otherwise leave [].",pre_fill=[])
        self.freq_sampling_func = ExpParas("freq_sampling_func","func",1,message="sampling function options: 'linspace', 'arange'.",pre_fill='linspace')
        self.flux_sampling_func = ExpParas("flux_sampling_func","func",1,message="sampling function options: 'linspace', 'arange'.",pre_fill='linspace')


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
        self.shots = ExpParas("shots","int",1,pre_fill=10000)


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
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=500)
        self.flux_range = ExpParas("flux_range","list",2,message="rule: [start, end, pts/step].")
        self.freq_sampling_func = ExpParas("freq_sampling_func","func",1,message="sampling function options: 'linspace', 'arange'.",pre_fill='linspace')
        self.flux_sampling_func = ExpParas("flux_sampling_func","func",1,message="sampling function options: 'linspace', 'arange', 'logspace'.",pre_fill='linspace')


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
        self.ROXYoverlap = ExpParas("ROXYoverlap","int",1,message="booling value set 0 for False or 1 for True, RO-XY overlap or not ?",pre_fill=0)
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=300)
        self.power_range = ExpParas("power_range","list",2,message="rule: [start, end, pts/step] or [a fixed value].",pre_fill=[0,0.1,10])
        self.freq_sampling_func = ExpParas("freq_sampling_func","func",1,message="sampling function options: 'linspace', 'arange'.",pre_fill='linspace')
        self.power_sampling_func = ExpParas("power_sampling_func","func",1,message="sampling function options: 'linspace', 'arange', 'logspace'.",pre_fill='linspace')


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

# S5
class PowerRabi(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S5"

    def set_variables(self):
        self.pi_amp = ExpParas("pi_amp","list",3,message="amp values span. rule: [start, end] like: [-0.6, 0.6].")
        self.pi_duration = ExpParas("pi_duration","float",3,message="how long is your pi-pulse ?")
        # self.OSmode = ExpParas("OSmode","int",1,message="booling value set 0 for False or 1 for True, Use one-shot or not ?")
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=200)
        self.amp_sampling_func = ExpParas("amp_sampling_func","func",1,message="sampling function options: 'linspace', 'arange'.",pre_fill='linspace')
        self.pi_amp_ptsORstep = ExpParas("pi_amp_ptsORstep","int",1,message="Depends on sampling func set in step or pts.",pre_fill=100)


    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):

        self.target_qs = list(self.pi_amp.keys())
        match self.machine_type.lower():
            case 'qblox':
                from qblox_drive_AS.support.ExpFrames import PowerRabiOsci
                self.EXP = PowerRabiOsci(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                self.EXP.SetParameters(self.pi_amp, self.pi_duration, self.amp_sampling_func, self.pi_amp_ptsORstep,self.avg_n,execution=True)
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

# S6
class TimeRabi(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S6"

    def set_variables(self):
        self.pi_amp = ExpParas("pi_amp","float",3,message="amp for your pi-pulse.")
        self.pi_duration = ExpParas("pi_duration","list",3,message="amp values span. rule: [start, end] like: [0, 200e-9].")
        # self.OSmode = ExpParas("OSmode","int",1,message="booling value set 0 for False or 1 for True, Use one-shot or not ?")
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=200)
        self.duration_sampling_func = ExpParas("duration_sampling_func","func",1,message="sampling function options: 'linspace', 'arange'.",pre_fill='linspace')
        self.pi_dura_ptsORstep = ExpParas("pi_dura_ptsORstep","int",1,message="Depends on sampling func set in step or pts.",pre_fill=100)


    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):

        self.target_qs = list(self.pi_amp.keys())
        match self.machine_type.lower():
            case 'qblox':
                from qblox_drive_AS.support.ExpFrames import TimeRabiOsci
                self.EXP = TimeRabiOsci(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                self.EXP.SetParameters( self.pi_duration, self.pi_amp,self.duration_sampling_func, self.pi_dura_ptsORstep,self.avg_n,execution=True)
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

# S7
class SingleShot(ExpSpirit):
    def __init__(self):
        super().__init__()
        
            
    def get_ExpLabel(self)->str:
        return "S7"

    def set_variables(self):
        self.histo_counts = ExpParas("histo_counts","int",1,message="repeat times of histogram",pre_fill=1)
        self.shots = ExpParas("shots","int",1,pre_fill=10000)


    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):

        match self.machine_type.lower():
            case 'qblox':
                from qblox_drive_AS.support.ExpFrames import SingleShot
                self.EXP = SingleShot(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                self.EXP.SetParameters( self.target_qs,self.histo_counts,self.shots,execution=True)
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

# S8
class RamseyT2(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S8"

    def set_variables(self):
        self.time_range = ExpParas("time_range","list",3,message="evolution time span. rule: [start, end] like: [0, 20e-6].")
        # self.OSmode = ExpParas("OSmode","int",1,message="booling value set 0 for False or 1 for True, Use one-shot or not ?")
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=300)
        self.time_sampling_func = ExpParas("time_sampling_func","func",1,message="sampling function options: 'linspace', 'arange', 'logspace'.",pre_fill="linspace")
        self.time_ptsORstep = ExpParas("time_ptsORstep","int",1,message="Depends on sampling func set in step or pts.",pre_fill=100)
        self.histo_counts = ExpParas("histo_counts","int",1,message="repeat times of histogram, <101 use FPGA otherwies use while loop.",pre_fill=1)

    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):

        self.target_qs = list(self.time_range.keys())
        match self.machine_type.lower():
            case 'qblox':
                from qblox_drive_AS.support.ExpFrames import Ramsey
                self.EXP = Ramsey(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                self.EXP.SetParameters( self.time_range, self.time_sampling_func,self.time_ptsORstep, self.histo_counts,self.avg_n,execution=True)
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

# S9
class SpinEchoT2(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S9"

    def set_variables(self):
        self.time_range = ExpParas("time_range","list",3,message="evolution time span. rule: [start, end] like: [0, 20e-6].")
        # self.OSmode = ExpParas("OSmode","int",1,message="booling value set 0 for False or 1 for True, Use one-shot or not ?")
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=300)
        self.time_sampling_func = ExpParas("time_sampling_func","func",1,message="sampling function options: 'linspace', 'arange', 'logspace'.",pre_fill="linspace")
        self.time_ptsORstep = ExpParas("time_ptsORstep","int",1,message="Depends on sampling func set in step or pts.",pre_fill=100)
        self.histo_counts = ExpParas("histo_counts","int",1,message="repeat times of histogram, <101 use FPGA otherwies use while loop.",pre_fill=1)

    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):

        self.target_qs = list(self.time_range.keys())
        match self.machine_type.lower():
            case 'qblox':
                from qblox_drive_AS.support.ExpFrames import SpinEcho
                self.EXP = SpinEcho(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                self.EXP.SetParameters( self.time_range, self.time_sampling_func,self.time_ptsORstep, self.histo_counts,self.avg_n,execution=True)
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

# S9b
class CPMG(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S9b"

    def set_variables(self):
        self.time_range = ExpParas("time_range","list",3,message="evolution time span. rule: [start, end] like: [0, 20e-6].")
        self.pi_num = ExpParas("pi_num","int",2,message="how many pi-pulses between your Ramsey ?")
        # self.OSmode = ExpParas("OSmode","int",1,message="booling value set 0 for False or 1 for True, Use one-shot or not ?")
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=300)
        self.time_sampling_func = ExpParas("time_sampling_func","func",1,message="sampling function options: 'linspace', 'arange', 'logspace'.",pre_fill='linspace')
        self.time_ptsORstep = ExpParas("time_ptsORstep","int",1,message="Depends on sampling func set in step or pts.",pre_fill=100)
        self.histo_counts = ExpParas("histo_counts","int",1,message="repeat times of histogram, <101 use FPGA otherwies use while loop.",pre_fill=1)

    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):

        self.target_qs = list(self.time_range.keys())
        match self.machine_type.lower():
            case 'qblox':
                from qblox_drive_AS.support.ExpFrames import CPMG
                pi_num = {}
                for q in self.target_qs:
                    pi_num[q] = self.pi_num

                self.EXP = CPMG(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                self.EXP.SetParameters( self.time_range, pi_num, self.time_sampling_func,self.time_ptsORstep, self.histo_counts,self.avg_n,execution=True)
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

# S10
class EnergyRelaxation(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S10"

    def set_variables(self):
        self.time_range = ExpParas("time_range","list",3,message="evolution time span. rule: [start, end] like: [0, 20e-6].")
        # self.OSmode = ExpParas("OSmode","int",1,message="booling value set 0 for False or 1 for True, Use one-shot or not ?")
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=300)
        self.time_sampling_func = ExpParas("time_sampling_func","func",1,message="sampling function options: 'linspace', 'arange', 'logspace'.",pre_fill='linspace')
        self.time_ptsORstep = ExpParas("time_ptsORstep","int",1,message="Depends on sampling func set in step or pts.",pre_fill=100)
        self.histo_counts = ExpParas("histo_counts","int",1,message="repeat times of histogram, <101 use FPGA otherwies use while loop.",pre_fill=1)

    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):

        self.target_qs = list(self.time_range.keys())
        match self.machine_type.lower():
            case 'qblox':
                from qblox_drive_AS.support.ExpFrames import EnergyRelaxation
                self.EXP = EnergyRelaxation(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                self.EXP.SetParameters( self.time_range, self.time_sampling_func,self.time_ptsORstep, self.histo_counts,self.avg_n,execution=True)
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

# C1
class XYFcalibrator(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "C1"

    def set_variables(self):
        self.time_range = ExpParas("time_range","list",3,message="If the fitting is not good, you can shorten it.",pre_fill="[0, 1e-6]")
        # self.OSmode = ExpParas("OSmode","int",1,message="booling value set 0 for False or 1 for True, Use one-shot or not ?")
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=500)

    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):

        self.target_qs = list(self.time_range.keys())
        match self.machine_type.lower():
            case 'qblox':
                from qblox_drive_AS.support.ExpFrames import XYFcali
                self.EXP = XYFcali(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                self.EXP.SetParameters( self.target_qs, self.time_range[self.target_qs[0]][-1],avg_n=self.avg_n,execution=True)
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

# C2 
class ROFcalibrator(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "C2"

    def set_variables(self):
        self.freq_range = ExpParas("freq_range","list",3,message="freq to span, like [-6e6, +8e6].")
        self.freq_ptsORstep = ExpParas("freq_ptsORstep","int",1,message="qblox set pts",pre_fill=100)
        # self.OSmode = ExpParas("OSmode","int",1,message="booling value set 0 for False or 1 for True, Use one-shot or not ?")
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=300)

    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):

        self.target_qs = list(self.freq_range.keys())
        match self.machine_type.lower():
            case 'qblox':
                from qblox_drive_AS.support.ExpFrames import ROFcali
                self.EXP = ROFcali(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                self.EXP.SetParameters( self.freq_range, self.freq_ptsORstep,self.avg_n,execution=True)
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

# C3
class ROLcalibrator(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "C3"

    def set_variables(self):
        self.amp_coef_range = ExpParas("amp_coef_range","list",3,message="ro-amp coef, rule: [start, end].")
        self.coef_ptsORstep = ExpParas("coef_ptsORstep","int",1,message="qblox set pts",pre_fill=100)
        # self.OSmode = ExpParas("OSmode","int",1,message="booling value set 0 for False or 1 for True, Use one-shot or not ?")
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=300)

    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):

        self.target_qs = list(self.amp_coef_range.keys())
        match self.machine_type.lower():
            case 'qblox':
                from qblox_drive_AS.support.ExpFrames import ROLcali
                self.EXP = ROLcali(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                self.EXP.SetParameters( self.amp_coef_range, 'linspace', self.coef_ptsORstep,self.avg_n,execution=True)
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

# C4
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

        self.target_qs = list(self.piamp_coef_range.keys())
        match self.machine_type.lower():
            case 'qblox':
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
                data_file = queue_out_items["Data"]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)

# C5
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

        self.target_qs = list(self.half_pi_coef_range.keys())
        match self.machine_type.lower():
            case 'qblox':
                from qblox_drive_AS.support.ExpFrames import hPiAcali
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
                data_file = queue_out_items["Data"]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.RunAnalysis(new_QD_path=QD_path,new_file_path=data_file)

#TODO C6
class DragCoefCali():
    pass

# A1
class ZgateRelaxation(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "A1"

    def set_variables(self):
        self.time_range = ExpParas("time_range","list",3,message="evolution time span. rule: [start, end] like: [0, 20e-6].")
        self.bias_range = ExpParas("bias_range","list",2,message="rule: [start, end, pts/step], QM please set in step.")
        # self.OSmode = ExpParas("OSmode","int",1,message="booling value set 0 for False or 1 for True, Use one-shot or not ?")
        self.avg_n = ExpParas("avg_n","int",1,pre_fill=300)
        self.prepare_Excited = ExpParas("prepare_Excited","int",1,message="booling value set 0 for False or 1 for True, Prepare the excited state first ?",pre_fill=1)
        self.time_sampling_func = ExpParas("time_sampling_func","func",1,message="sampling function options: 'linspace', 'arange', 'logspace'.",pre_fill='linspace')
        self.time_ptsORstep = ExpParas("time_ptsORstep","int",1,message="Depends on sampling func set in step or pts.",pre_fill=100)
        self.no_limit_repeat = ExpParas("no_limit_repeat","int",1,message="booling value set 0 for False or 1 for True, Don't stop it ?",pre_fill=0)
    

    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):

        self.target_qs = list(self.time_range.keys())
        match self.machine_type.lower():
            case 'qblox':
                from qblox_drive_AS.support.ExpFrames import ZgateEnergyRelaxation
                self.EXP = ZgateEnergyRelaxation(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                self.EXP.SetParameters( self.time_range, self.time_sampling_func,self.bias_range,self.prepare_Excited,'linspace',self.time_ptsORstep,self.no_limit_repeat,self.avg_n,execution=True)
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

# A2
class TimeMonitor(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "A2"

    def set_variables(self):
        self.T1_time_range = ExpParas("T1_time_range","list",3,message="T1 evolution time span. rule: [start, end] like: [0, 60e-6]. If you don't wanna do T1 leave it [].")
        self.T2_time_range = ExpParas("T2_time_range","list",3,message="T2 evolution time span. rule: [start, end] like: [0, 50e-6]. If you don't wanna do T2 leave it [].")
        self.time_sampling_func = ExpParas("time_sampling_func","func",1,message="sampling function options: 'linspace', 'arange', 'logspace'.",pre_fill='linspace')
        self.time_ptsORstep = ExpParas("time_ptsORstep","int",1,message="Depends on sampling func set in step or pts.",pre_fill=100)
        # self.OSmode = ExpParas("OSmode","int",1,message="booling value set 0 for False or 1 for True, Use one-shot or not ?")
        self.echo_pi_num = ExpParas("echo_pi_num","int",2,message="How many pi-pulse between Ramsey ? 0 for Ramsey T2, 1 for SpinEcho T2, more for CPMG.",pre_fill=0)
        self.small_detune = ExpParas("small_detune","float",1,message="Only while doing Ramsey, how many driving detuning ? otherwise set None",pre_fill=0)
        self.OS_shots = ExpParas("OS_shots","int",1,message="Shot number for OneSoht exp. If you don't wanna do OneShot leave it 0.",pre_fill=10000)

        self.avg_n = ExpParas("avg_n","int",1,pre_fill=500)

    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):
        match self.machine_type.lower():
            case 'qblox':
                from qblox_drive_AS.support.ExpFrames import QubitMonitor

                self.EXP = QubitMonitor(QD_path=self.connections[0],save_dir=self.save_data_folder)
                # T1 settings
                self.EXP.T1_time_range = {}
                for q in self.T1_time_range:
                    if len(self.T1_time_range[q]) != 0:
                        self.EXP.T1_time_range[q] = self.T1_time_range[q]
                # T2 settings
                self.EXP.T2_time_range = {}
                for q in self.T2_time_range:
                    if len(self.T2_time_range[q]) != 0:
                        self.EXP.T2_time_range[q] = self.T2_time_range[q]
                self.EXP.a_little_detune_Hz = self.small_detune  # for all qubit in T2_time_range. Set None if you do SpinEcho or CPMG
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



    def start_analysis(self,analysis_need:dict=None,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                queue_out_items = analysis_need
                config_folder = queue_out_items["Configs"]   # Association.TrafficBureau.Queuer.QueueOut()
                data_file = queue_out_items["Data"]
                QD_path = [os.path.join(config_folder,name) for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder,name)) and os.path.split(name)[-1].split(".")[-1]=='pkl'][0]
                self.EXP.TimeMonitor_analysis(New_QD_path=QD_path,New_data_file=data_file)

#TODO R1b
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
        match self.machine_type.lower():
            case 'qblox':
                from qblox_drive_AS.support.ExpFrames import XGateErrorTest
                self.EXP = XGateErrorTest(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                self.EXP.SetParameters( self.target_qs, self.OneShot_shots, self.MaxGate_num, execution=True, use_untrained_wf=self.use_uncali_waveform)
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













