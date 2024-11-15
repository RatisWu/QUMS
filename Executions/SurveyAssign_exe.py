from Association.FBI import Canvasser

#######################################
########    Experiment tags    ########
#######################################
"""
S0: Sample Registeration    
S1: Broad-Band Cavity Search 
"""

What_exp_tag:str = 'S1'
What_qubits_join:list = ['q0_ro']


Survey = Canvasser()
Survey.generate_ExpParas_servey(What_exp_tag,What_qubits_join)
