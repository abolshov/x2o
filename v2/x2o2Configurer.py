from dumbo.i2c import *
from dumbo.bitstream import bscan
import subprocess
import time 


class x2o2Configurer:
    # format: clock frequency(?) : config_file
    clock_map = { 40: "/root/gem/clk_config/DPLLandAPLL2_Input_40p0786_Out0_40p0786_Out1_320p6288_OutOthers_160p3144_ZDM_EN_in_REF1.txt",
                  320: "/root/gem/clk_config/DPLLandAPLL2_Input_40p0786_Out0_40p0786_Out1_320p6288_OutOthers_160p3144_ZDM_EN_in_REF0.txt" }

    # format: board_type : fw_file
    fpga_map = { "ge21": "/root/gem/fw/ge21_x2o-v5.0.3-hog7F4AD48-dirty_X2Ov2_v4_with_LDAQ/ge21_x2o-v5.0.3-hog7F4AD48-dirty.bit",
                 "me0": "/root/gem/fw/me0_x2o-v5.0.3-hog7F4AD48-dirty_X2Ov2_v4_with_LDAQ/me0_x2o-v5.0.3-hog7F4AD48-dirty.bit" }

    def __init__(self, clk_freq, board_type, verbosity):
        self.ic2bus = bus(1)
        self.octopus = octopus_rev2(self.ic2bus)

        # path to clock config file
        self.clk_cfg = clock_map[clk_freq]
        # file with firmware to be loaded to x2o 
        self.fw_file = fpga_map[board_type]
        # verbosity level of monitoring routine
        self.verbosity = verbosity

    def power_up(self):
        subprocess.Popen("cd /root/X2O-Zynq-software && source ./rev3.sh && ./payload_on.sh", shell=True, executable="/bin/bash")
        self.octopus.configure()
        self.octopus.power_up(verbose=True)
        time.sleep(1) 

    def power_down(self):
        self.octopus.power_down(verbose=True)
        subprocess.Popen("cd /root/X2O-Zynq-software && source ./rev3.sh && ./payload_off.sh", shell=True, executable="/bin/bash")
        time.sleep(1)  
        
    def monitor(self):
        return self.octopus.monitor(self.verbosity) 

    def config_clock(self):
        subprocess.Popen("cd /root/X2O-Zynq-software && source ./rev3.sh && ./devreg_us.sh bp_clk_sel_top 0", shell=True, executable="/bin/bash")
        time.sleep(0.1)
        subprocess.Popen("cd /root/X2O-Zynq-software && source ./rev3.sh && ./devreg_us.sh bp_clk_sel_bot 0", shell=True, executable="/bin/bash")
        time.sleep(0.1)

        print(f"\tClock config file: {self.clk_cfg}")
        self.octopus.lmk.load_config(f"{self.clk_cfg}")
        time.sleep(1)

        self.octopus.lmk.sync()

    def program_FPGA(self):
        print(f"Programming FPGA with {self.fw_file}")

        proc = subprocess.Popen("cd /root/X2O-Zynq-software && source ./rev3.sh && insmod jtag/xvc/driver/xilinx_xvc_driver.ko", shell=True, executable="/bin/bash")
        proc.wait()
        proc = subprocess.Popen("cd /root/X2O-Zynq-software/jtag/jtag_fw_programmer && ./jtag_fw_programmer /dev/xilinx_xvc_driver_0 %s" % self.fw_file, shell=True, executable="/bin/bash") 
        proc.wait()

        time.sleep(3)
        proc = subprocess.Popen("cd /root/X2O-Zynq-software && source ./rev3.sh && ./gtp_reset.sh && ./c2c_reset_vu13p_top.sh", shell=True, executable="/bin/bash")
        proc.wait()

        print("FPGA has been programmed")
