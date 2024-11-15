---
title: United Quantum Measurement System  User Guide

---

# United Quantum Measurement System  User Guide
++**Notation:** \<This-is-a-variable> can be replaced.++
## Measurement Flow
**-- First at Local**  
1. Generate the `ExpParasSurvey.toml` according to the exp you want.
    * Use `UQMS\\Executions\\SurveyAssign.py` 
    * Generate to `C:\\Users\\<username>\\`
2. Fill in the Survey.toml and prepare the HardwareConfig you need.
    1. **QM**: `<arbitrary-name>_config.pkl` and `<arbitrary-name>_spec.pkl`
    2. **Qblox**: `QD_file`
3. Packaging your configs with a folder named `'ExpConfigs'`.
4. SCP `ExpConfigs` and `ExpParasSurvey.toml` to server ==Destination==

**-- Second by Remote**  
1.  SSH to the server and `cd MeasExecutor`
2.   Start the env `conda activate UQMS`
3. Run the measurement with `python MEAS_exe.py`

**-- Final by FileZilla**  
1. Connect to FileZill server check the raw data and picture.

---------------------------------------------------------
## Connection tools
### -- SSH Connections 
`ssh -p <port> <user-name>@<server-ip>`

### -- SCP all items in a folder to ==Destination==
`scp -P <port> -r <folder-path>/* <user-name>@<server-ip>: "<Destination>"`

*   ==<Destination>==: `C:\\Users\\<user-name>\\MeasConfigs\\`
----------------------------------------------------------
## <mark style="color:red;">* Warning !</mark>  
1. Do ++**NOT**++ rename any file you will scp to server.