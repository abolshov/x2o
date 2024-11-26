import re
import sys
import os
import subprocess
import time
from dumbo.i2c import *
from dumbo.bitstream import bscan 


def parse_table(table):  
    result = {}

    # Split the table into lines
    lines = table.splitlines()

    # Define regex to match rows with words in the first column
    row_pattern = re.compile(r"""
        ^(?P<device>[\w\-]+)\s+        # Device name (words)
        (?P<V>[+-]?[\d.]+\sV)?\s*     # Voltage (optional)
        (?P<I>[+-]?[\d.]+\sA)?\s*     # Current (optional)
        (?P<P>[+-]?[\d.]+\sW)?\s*     # Power (optional)
        (?P<T>(\d+\.\d+\sC(?:,\s*\d+\.\d+\sC)*))?$  # Temperature(s) (optional)
    """, re.VERBOSE)

    for line in lines:
        if line.strip() == "":
            continue

        match = row_pattern.match(line)
        if match:
            device = match.group("device")
            v = match.group("V")
            i = match.group("I")
            p = match.group("P")
            t = match.group("T")

            # Remove units from values and convert to float where applicable
            def clean_value(value, unit):
                return float(value.replace(unit, "")) if value else None

            result[device] = {
                "V": clean_value(v, " V"),
                "I": clean_value(i, " A"),
                "P": clean_value(p, " W"),
                "T": [float(temp.replace(" C", "")) for temp in t.split(",")] if t else None
            }

    return result


def compare_conditions(target, measured):
    pass


firmware_file_map = {"csc":"/root/gem/fw/csc_x2o-v5.0.3-60B3805-dirty_X2O_v3_full/csc_x2o-v5.0.3-60B3805-dirty.dat"
                     "ge11":"/root/gem/fw/ge11_x2o-v5.0.3-60B3805-dirty_X2O_v3_SLR0_full/ge11_x2o-v5.0.3-60B3805-dirty.bit"
                     "ge21":"/root/gem/fw/ge21_x2o-v5.0.3-D7AB225-dirty_v3_full_4_SLR_8_OH/ge21_x2o-v5.0.3-D7AB225-dirty.bit"
                     "me0":"/root/gem/fw/ge21_x2o-v5.0.3-D7AB225-dirty_v3_full_4_SLR_8_OH/ge21_x2o-v5.0.3-D7AB225-dirty.bit"}

clk_cfg_map = {40: '/root/gem/clk_config/DPLLandAPLL2_Input_40p0786_Out0_40p0786_OutOthers_160p3144_ZDM_EN_in_REF1.txt',
               320: '/root/gem/clk_config/DPLLandAPLL2_Input_40p0786_Out0_40p0786_Out1_320p6288_OutOthers_160p3144_ZDM_EN_in_REF0.txt'}


class x2o3_configurer():
    def __init__(self, clk_freq, board_type, verbosity):
        # path to clock config file
        self.clk_cfg = clk_cfg_map[clk_freq]
        # file with firmware to be loaded to x2o 
        self.fw_file = fpga_map[board_type]
        # verbosity level of monitoring routine
        self.verbosity = verbosity

        if not os.path.exists(self.fw_file):
            print(f"FIRMWARE FILE {self.fw_file} NOT FOUND")
            sys.exit(-1)

        self.i2cbus = bus(1)
        self.octopus = octopus_rev2(i2cbus)


    def power_up(self):
        proc = subprocess.Popen("x2o control payload_on", shell=True, executable="/bin/bash")
        proc.wait()
        time.sleep(1)
        proc = subprocess.Popen("x2o octopus configure", shell=True, executable="/bin/bash")
        proc.wait()
        time.sleep(0.1)
        proc = subprocess.Popen("x2o octopus power_up", shell=True, executable="/bin/bash")
        proc.wait()

        print("")
        print("POWER UP DONE!")


    def power_down(self):
        proc = subprocess.Popen("x2o octopus power_down", shell=True, executable="/bin/bash")
        proc.wait()

        print("")
        print("POWER DOWN DONE!")  
        
        
    def monitor(self):
        proc = subprocess.Popen("x2o octopus monitor",
                                shell=True, 
                                executable="/bin/bash"
                                stdout=subprocess.PIPE,  # Captures the standard output
                                stderr=subprocess.PIPE)
        proc.wait()

        stdout, stderr = proc.communicate()

        # Decode the output (since it's in bytes) into a string
        output = stdout.decode('utf-8').strip()  # Adjust 'utf-8' if your encoding is different
        error = stderr.decode('utf-8').strip()

        print(output)
        print(error)

        monitoring_result = parse_table(output)

        print("")
        print("MONITORING DONE!")


    def config_clock(self):
        subprocess.Popen("cd /root/X2O-Zynq-software && source ./rev3.sh && ./devreg_us.sh bp_clk_sel_top 0", shell=True, executable="/bin/bash")
        time.sleep(0.1)
        subprocess.Popen("cd /root/X2O-Zynq-software && source ./rev3.sh && ./devreg_us.sh bp_clk_sel_bot 0", shell=True, executable="/bin/bash")
        time.sleep(0.1)

        self.octopus.lmk.load_config(self.clk_cfg)
        time.sleep(1)
        self.octopus.lmk.sync()

        print("")
        print("CLOCK CONFIGURATION DONE!") 


    def program_FPGA(self):
        load_cmd = "load_bitstream_top" if self.fw_file.endswith("bit") else "load_bitstream_top_decoded" if self.fw_file.endswith("dat") else None

        if load_cmd is None:
            print(f"ERROR: UNRECOGNIZED FIRMWARE FILE FORMAT: .{self.fw_file.split('.')[-1]}")
            sys.exit(-1)

        proc = subprocess.Popen(f"x2o control {load_cmd} {self.fw_file}", shell=True, executable="/bin/bash")
        proc.wait()
        time.sleep(3)
        proc = subprocess.Popen("x2o control reset_c2c_top", shell=True, executable="/bin/bash")
        proc.wait()

        print("")
        print("PROGRAMMING FPGA DONE!")
