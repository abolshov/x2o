#!/usr/bin/python3

from dumbo.i2c import *
import subprocess
import time

subprocess.Popen("cd /root/X2O-Zynq-software && source ./rev3.sh && ./devreg_us.sh bp_clk_sel_top 0", shell=True, executable="/bin/bash")
time.sleep(0.1)
subprocess.Popen("cd /root/X2O-Zynq-software && source ./rev3.sh && ./devreg_us.sh bp_clk_sel_bot 0", shell=True, executable="/bin/bash")
time.sleep(0.1)

i2cbus = bus(1)
octopus=octopus_rev2(i2cbus)
#octopus.lmk.load_config('/root/gem/clk_config/HexRegisterValues_322p265625.txt')
#octopus.lmk.load_config('/root/gem/clk_config/DPLLandAPLL2_Input_40p0786_Out0_40p0786_OutOthers_160p3144_ZDM.txt')
#octopus.lmk.load_config('/root/gem/clk_config/DPLLandAPLL2_Input_40p0786_Out0_40p0786_Out1_320p6288_OutOthers_160p3144_ZDM.txt')
#octopus.lmk.load_config('/root/gem/clk_config/DPLLandAPLL2_Input_40p0786_Out0_40p0786_Out1_320p6288_OutOthers_160p3144_ZDM_use_REF1.txt')
#octopus.lmk.load_config('/root/gem/clk_config/DPLLandAPLL2_Input_40p0786_Out0_40p0786_Out1_320p6288_OutOthers_160p3144_ZDM_1000ppm_freq_valid_range.txt')


#octopus.lmk.load_config('/root/gem/clk_config/DPLLandAPLL2_Input_40p0786_Out0_40p0786_Out1_320p6288_OutOthers_160p3144_ZDM_EN_in_REF0.txt')
#octopus.lmk.load_config('/root/gem/clk_config/DPLLandAPLL2_Input_40p0786_Out0_40p0786_Out1_320p6288_OutOthers_160p3144_ZDM_EN_in_REF1.txt')
octopus.lmk.load_config('/root/gem/clk_config/DPLLandAPLL2_Input_40p0786_Out0_40p0786_OutOthers_160p3144_ZDM_EN_in_REF1.txt')

time.sleep(1)

octopus.lmk.sync()

