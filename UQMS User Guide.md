---
title: UQMS User Guide

---
# UQMS User Guide
**United Quantum Measuring System**\
**Notation:** \<This-is-a-variable> can be replaced.\
<mark style="color:red;">Warning !</mark>: Do **NOT** rename any file you will upload to server.\
<mark style="color:green;">Destination</mark>: `/home/<user-name>/MeasConfigs/`

---
Sec I. Measurement Flow
---
**-- First at Local**  
1. Generate the `ExpParasSurvey.toml` according to the exp you want.
    * Use `UQMS\Executions\SurveyAssign.py` 
    * Can be generated to an arbitary file path.
2. Fill in the Survey.toml and prepare the HardwareConfig you need.
    1. **QM**: `<arbitrary-name>_config.pkl` and `<arbitrary-name>_spec.pkl`
    2. **Qblox**: `QD_file`
3. Packaging your configs with a folder named `'ExpConfigs'`.
4. Upload `ExpConfigs` and `ExpParasSurvey.toml` to server <mark style="color:green;">Destination</mark>

**-- Second by Remote**  
1. SSH to the server and Start the env `conda activate UQMS`
2. Run the measurement with the bash file, see appendix for more.

**-- Final by FileZilla-Client**  
1. Check the raw data and picture in the ~/Data (Only download-able), see appendix for more.

---

# Sec II. Connection tools (Terminal)

### -- SSH Connections 
Connect: `ssh -p <port> <user-name>@<server-ip>`
Close: `exit`

### -- SSH via VPN
Connect: `ssh -p <port> <user-name>@<Lab-Website>`

### -- SCP all items in a folder to <mark style="color:green;">Destination</mark>
`scp -P <port> -r <folder-path>/* <user-name>@<server-ip>:"<Destination>"`

### -- SCP a file to <mark style="color:green;">Destination</mark>
 `scp -P <port> -r <file_path> <user-name>@<server-ip>:"<Destination>"`  
    
### -- SCP back all items in a folder from the Server
 `scp <user-name>@<server-ip>:/path/to/dir/ /local/dir/path`

--- 
# Appendix

### 1. Bash files for executing a measurement or registeration.
1 meas_exe.sh -> run the measurement with a console.\
2 meas_BGexe.sh -> rum the measurement at the BackGround (no console shown).\
3 chip_register.sh -> Register a new sample (Only need S0-Survey to execute with).
* use `./<filename>.sh` to launch it.
    
### 2. Reattach your background executions
If you use `meas_BGexe.sh`, then the log file with name `<JOB-name>` will be generated. Kill this python running with the command:
    `tmux send-keys -t <JOB-name> C-c`

### 3. FileZilla settings (via SFTP)
We use FileZilla Client to transfering the data. The following picture is the communications setup, please download the application first. You will need two different communications if you connect with VPN.
![截圖 2024-12-13 11.10.20](https://hackmd.io/_uploads/r1I1wmK4yx.png)

---

### 4. SSH KeyAuthentication
 1. Generate the public-private Key pair
 ![截圖 2024-12-13 11.04.46](https://hackmd.io/_uploads/r1rQH7tN1g.png)
 2. Upload your <mark style="color:red;">public key</mark> to server
 ![截圖 2024-12-13 11.05.26](https://hackmd.io/_uploads/SkhSrQFEke.png)
 
 
### 5. Run your own developed measurement script <mark style="color:red;">on server</mark>
There are some rules you should follow to do this execution:
* Your own designed measurement script should <mark style="color:red;">inherit</mark> the `ExpSpirit` which is defined at `UQMS/Association/Soul` and store in a python file.
* Generate the __ExpParasSurvey__ by `UQMS\Executions\SurveyAssign.py`.
* Put this script in your __MeasConfigs__ folder on server.
* <mark style="color:red;">This script must be the __only one__ python file in that folder.</mark>

Following figure shows the correct structure that you can run a measurement. 
![截圖 2024-12-13 16.44.15](https://hackmd.io/_uploads/HJVE4dKV1e.png)