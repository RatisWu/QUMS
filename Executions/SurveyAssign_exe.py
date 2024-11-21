from Association.FBI import Canvasser

#######################################
########    Experiment tags    ########
#######################################
"""  
# If the tag ends with a letter, it means "system-unique" measurement. "b" for 'qblox', "M" for 'qm'
-------- Routine Meas --------
S0 : Sample Registeration  #! test OK
S1 : Cavity Search with IF span  #! qblox test OK 
S1b: Broad-Band Cavity Search (LO span, Qblox only) #! qblox test OK
S2 : Power dependent Cavity #! qblox test OK
S2b: Dressed Cavity Search (Qblox only) #! qblox test OK
S3 : Flux dependent Cavity/Coupler   #! qblox test OK
S3b: Ground IQ positioning (Qblox only) #! qblox test OK
S4 : Flux dependent Qubit spectrum
S4b: Power dependent Continuous 2-tone (Qblox only)
S5 : Power Rabi Oscillation
S6 : Time Rabi Oscillation
S7 : Single Shot
S8 : Ramsey T2
S9 : Spin Echo T2
S10: T1

-------- AuxiliaryMeas -------
A1 : Zgate T1
A2 : Time Monitor

-------- Calibrations --------
C1 : XYF calibration
C2 : ROF calibration
C3 : ROL calibration
C4 : Pi-amp calibration
C5 : half Pi-amp calibration

-------- 2Q operation --------
T1M: i-SWAP (QM only)
T2M: CZ-chevron (QM only) 

--------      RB      --------  
R1M: 1Q Randomized Benchmarking (QM only)
R2M: 2Q Randomized Benchmarking (QM only)

"""

#######################################
####    Generation Eequirements    ####
#######################################

What_exp_tag:str = 'S4'
What_qubits_join:list = ['q0',"q1"]
creat_survey_in_this_folder:str = ""


Survey = Canvasser()
Survey.generate_ExpParas_servey(What_exp_tag,What_qubits_join,creat_survey_in_this_folder)
