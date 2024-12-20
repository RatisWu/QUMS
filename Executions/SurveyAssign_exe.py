from Association.FBI import Canvasser

#######################################
########    Experiment tags    ########
#######################################
"""  
# If the tag ends with a letter, it means "system-unique" measurement. "b" for 'qblox', "M" for 'qm'
-------- Routine Meas --------
S0 : Sample Registeration                                |--done    
S1 : Cavity Search with IF span                          |--done
S1b: Broad-Band Cavity Search (LO span, Qblox only)      |--done
S2 : Power dependent Cavity                              |--done
S2b: Dressed Cavity Search (Qblox only)                  |--done
S3 : Flux dependent Cavity/Coupler                       |--done
S3b: Ground IQ positioning (Qblox only)                  |--done
S4 : Power dependent Continuous 2-tone                   |--done
S5 : Flux dependent Qubit spectrum                       |--done
S6 : Power Rabi Oscillation                              |--done
S7 : Time Rabi Oscillation                               |--done
S8 : Single Shot   #! qblox test okay                    |--100%, 90%
S9 : Ramsey T2   #! qblox test okay                      |--100%, 90 %
S9b: CPMG (Qblox only)                                   |--done
S10: Spin Echo T2   #! qblox test okay                   |--100%, 90 %
S11: T1   #! qblox test okay                             |--100%, 90 %
                                                         
-------- AuxiliaryMeas -------                          ---
A1 : Zgate T1   #! qblox test okay                       |--100%, 80 %
A2 : Time Monitor  #! qblox test okay                    |--100%, 90 %

-------- Calibrations --------                          ---
C1 : XYF calibration   #! qblox test okay                |--100%, 70 %
C2 : ROF calibration   #! qblox test okay                |--100%, 70 %
C3 : ROL calibration   #! qblox test okay                |--100%, 70 %
C4 : Pi-amp calibration  #! qblox test okay              |--100%, 0%
C5 : half Pi-amp calibration  #! qblox test okay         |--100%, 0%
C6 : Drag coef Calibration  #! qblox test okay           |--100%, 0%

-------- 2Q operation --------                          ---
T1M: i-SWAP (QM only)                                    |
T2M: CZ-chevron (QM only)                                |

--------      RB      --------                          ---
R1M: 1Q Randomized Benchmarking (QM only)                |
R1b: Gate phase error estimation (Qblox)                 |--done
R2M: 2Q Randomized Benchmarking (QM only)                |


"""

#######################################
####    Generation Eequirements    ####
#######################################

What_exp_tag:str = 'S11'
What_qubits_join:list = ['q0', 'q1']   # Qblox fill it, QM keep it empty! And if it's S0 also keep it empty for both system.
creat_survey_in_this_folder:str = "/home/asqcmeas/MeasConfigs"

# If you want run your customized meas script, fill the absolute path in
# Make sure that the Meas obj in your script inherit the Association.Soul.ExpSpirits and also SCP it to 'MeasConfigs folder at server.
# ONLY accept ONE .py file in that folder. Otherwise, it will enforce to queue out.
developing_meas_path:str = ""


Survey = Canvasser()
Survey.generate_ExpParas_servey(What_exp_tag,What_qubits_join,creat_survey_in_this_folder,developing_meas_path)
