
import inspect, os, shutil
from datetime import datetime
from Association.Soul import ExpParas, ExpSpirit
from qspec.channel_info import ChannelInfo
from config_component.configuration import Configuration
from ab.QM_config_dynamic import initializer
from qblox_drive_AS.support import QDmanager, Data_manager
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

        


class BbCavitySearch(ExpSpirit):
    def __init__(self):
        super().__init__()
            
    def get_ExpLabel(self)->str:
        return "S1"

    def set_variables(self):
        self.freq_range = ExpParas("freq_range","list",3)
        self.avg_n = ExpParas("avg_n","int",1)
        self.freq_sampling_func = ExpParas("freq_sampling_func","func",1)

        # self.bias_range = ExpParas("bias_range","list",2)  # <- only for test
        # self.bias_sampling_func = ExpParas("bias_sampling_func","func",1) # <- only for test.

    def provide_ExpSurveyInfo(self):
        self.set_variables()


    def start_measurement(self):
        
        match self.machine_type.lower():
            case 'qblox':
                from qblox_drive_AS.support.ExpFrames import BroadBand_CavitySearching
                self.EXP = BroadBand_CavitySearching(QD_path=self.connections[0],data_folder=self.save_data_folder,JOBID=self.JOBID)
                target_q = list(self.freq_range.keys())[0]
                if self.freq_sampling_func == 'arange':
                    pts = int(abs(float(self.freq_range[target_q][1])-float(self.freq_range[target_q][0]))/float(self.freq_range[target_q][2]))
                else:
                    pts = int(self.freq_range[target_q][2])
                self.EXP.SetParameters([target_q],float(self.freq_range[target_q][0]),float(self.freq_range[target_q][1]),pts)
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
                    my_exp.resolution = self.freq_range[ro_q][2]*1e-6
                    print(f'arange ,step= {my_exp.resolution}')
                else:
                    my_exp.resolution = (abs(float(self.freq_range[ro_q][1])-float(self.freq_range[ro_q][0]))/float(self.freq_range[ro_q][2]))*1e-6
                self.raw_data_path:str = os.path.join(self.save_data_folder,f"ROFreqSweep_{self.JOBID}.nc")
                print(f"raw at= {self.raw_data_path}")
                self.dataset = my_exp.run( int(self.avg_n))
                self.dataset.to_netcdf(self.raw_data_path,engine='netcdf4')
    
    def start_analysis(self,*args):
        """ Wait calling from Conductor.Executor """
        match self.machine_type.lower():
            case 'qblox':
                new_QD_folder = shutil.copytree(os.path.split(self.connections[0])[0],os.path.join(os.path.split(os.path.split(self.connections[0])[0])[0],f"Updated_{ConfigUniqueName}"))
                self.EXP.RunAnalysis(new_QD_folder)

            case 'qm':
                import numpy as np
                import matplotlib.pyplot as plt
                idata = self.dataset["q0_ro"].sel(mixer='I').values
                qdata = self.dataset["q0_ro"].sel(mixer='Q').values
                zdata = idata+1j*qdata
                plt.plot(self.dataset.coords["frequency"].values,np.abs(zdata))
                plt.savefig(os.path.join(self.save_data_folder,f"ROFreqSweep_{self.JOBID}.png"))
                plt.close()
    


if __name__ == "__main__":
    
    s1 = BbCavitySearch()
    s1.provide_ExpSurveyInfo()
    shared_Paras = [name for name in [name for name, _ in inspect.getmembers(s1) if not name.startswith("__")] if  name.startswith("_") and name.endswith("_")]
    print(shared_Paras)
    unique_Paras = [name for name in list(vars(s1).keys()) if name not in shared_Paras and name.split("_")[-1].lower() != 'protocol']
    print(unique_Paras)