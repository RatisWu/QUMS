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
S4 : Flux dependent Qubit spectrum  #! qblox test okay
S4b: Power dependent Continuous 2-tone (Qblox only) #! qblox test okay
S5 : Power Rabi Oscillation  #! qblox test okay
S6 : Time Rabi Oscillation  #! qblox test okay
S7 : Single Shot   #! qblox test okay
S8 : Ramsey T2   #! qblox test okay
S9 : Spin Echo T2   #! qblox test okay
S9b: CPMG (Qblox only)   #! qblox test okay
S10: T1   #! qblox test okay

-------- AuxiliaryMeas -------
A1 : Zgate T1   #! qblox test okay
A2 : Time Monitor  #! qblox test okay

-------- Calibrations --------
C1 : XYF calibration   #! qblox test okay
C2 : ROF calibration   #! qblox test okay
C3 : ROL calibration   #! qblox test okay
C4 : Pi-amp calibration  #! qblox test okay
C5 : half Pi-amp calibration  #! qblox test okay
C6 : Drag coef Calibration  #! qblox test okay

-------- 2Q operation --------
T1M: i-SWAP (QM only)
T2M: CZ-chevron (QM only) 

--------      RB      --------  
R1M: 1Q Randomized Benchmarking (QM only)
R1b: Gate phase error estimation (Qblox)  #! qblox test okay
R2M: 2Q Randomized Benchmarking (QM only)


"""

#######################################
####    Generation Eequirements    ####
#######################################

What_exp_tag:str = 's1'
What_qubits_join:list = ['q0','q1']
creat_survey_in_this_folder:str = ""

# If you want run your customized meas script, fill the absolute path in
# Make sure that the Meas obj in your script inherit the Association.Soul.ExpSpirits and also SCP it to 'MeasConfigs folder at server.
# ONLY accept ONE .py file in that folder. Otherwise, it will enforce to queue out.
developing_meas_path:str = ""


Survey = Canvasser()
Survey.generate_ExpParas_servey(What_exp_tag,What_qubits_join,creat_survey_in_this_folder,developing_meas_path)
