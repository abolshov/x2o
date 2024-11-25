from dumbo.i2c import *
from dumbo.bitstream import bscan
import subprocess

def x2o_c2c_reset():
    subprocess.Popen("cd /root/X2O-Zynq-software && source ./rev3.sh && ./gtp_reset.sh && ./c2c_reset_vu13p_top.sh", shell=True, executable="/bin/bash")

def x2o_power_down():
    i2cbus = bus(1)
    octopus=octopus_rev2(i2cbus)
    octopus.power_down(verbose=True)
    subprocess.Popen("cd /root/X2O-Zynq-software && source ./rev3.sh && ./payload_off.sh", shell=True, executable="/bin/bash")

def x2o_power_up():
    subprocess.Popen("cd /root/X2O-Zynq-software && source ./rev3.sh && ./payload_on.sh", shell=True, executable="/bin/bash")
    i2cbus = bus(1)
    octopus=octopus_rev2(i2cbus)
    octopus.configure()
    octopus.power_up(verbose=True)

def x2o_config_clk():
    proc = subprocess.Popen("cd /root/X2O-Zynq-software && source ./rev3.sh && ./devreg_us.sh bp_clk_sel_top 0", shell=True, executable="/bin/bash")
    proc.wait()
    time.sleep(0.1)
    proc = subprocess.Popen("cd /root/X2O-Zynq-software && source ./rev3.sh && ./devreg_us.sh bp_clk_sel_bot 0", shell=True, executable="/bin/bash")
    proc.wait()
    time.sleep(0.1)

    i2cbus = bus(1)
    octopus=octopus_rev2(i2cbus)
    proc = octopus.lmk.load_config('/root/gem/clk_config/DPLLandAPLL2_Input_40p0786_Out0_40p0786_Out1_320p6288_OutOthers_160p3144_ZDM_EN_in_REF1.txt')
    proc.wait()
    time.sleep(1)
    octopus.lmk.sync()

def x2o_program_fpga(firmware_file = None):
    if firmware_file is None:
        firmware_file = "/root/gem/0xbefe/scripts/resources/x2o_ge21.bit"
    
    proc = subprocess.Popen("cd /root/X2O-Zynq-software && source ./rev3.sh && cd /root/X2O-Zynq-software/jtag/jtag_fw_programmer && ./jtag_fw_programmer /dev/xilinx_xvc_driver_0 %s" % firmware_file, shell=True, executable="/bin/bash")
    proc.wait()

    #jtag = bscan(0x43c10000)
    #i2cbus = bus(1)
    #octopus=octopus_rev2(i2cbus)
    #
    #if not os.path.exists(FIRMWARE_FILE):
    #    print('File not found')
    #    return -1
    #
    #octopus.jtag_chain(1)
    #jtag.program_xilinx(FIRMWARE_FILE)
    #return 0
