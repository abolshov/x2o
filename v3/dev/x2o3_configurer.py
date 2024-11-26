import re
import sys
import os
import subprocess
import time
from dumbo.i2c import *
from dumbo.bitstream import bscan 


'''
device : list [V, I, P, T] of tuples (min, max) for each parameter
'''
conditions_dict = {
    "12V0" : {},
    "3V3_STANDBY": {},
    "1V8_MACHXO2": {},
    "2V5_OSC_NE": {'V': (2.504, 2.506), 'I': (0, 30.0), 'P': (0.0, 75.18), 'T': (-1.0, 1000.0)},
    "1V8_MGTVCCAUX_VUP_N": {'V': (1.8138, 1.8144), 'I': (0, 30.0), 'P': (0.0, 55.0), 'T': (-1.0, 1000.0)},
    "2V5_OSC_NW": {'V': (2.5162, 2.5164), 'I': (0, 30.0), 'P': (0.0, 75.492), 'T': (-1.0, 1000.0)},
    "1V8_MGTVCCAUX_VUP_S": {'V': (1.817, 1.8194), 'I': (0, 30.0), 'P': (0.0, 55.0), 'T': (-1.0, 1000.0)},
    "2V5_OSC_SW": {'V': (2.512, 2.514), 'I': (0, 30.0), 'P': (0.0, 75.42), 'T': (-1.0, 1000.0)},
    "2V5_OSC_SE": {'V': (-1.0, 200.0), 'I': (0, 30.0), 'P': (0.0, 6000.0), 'T': (-1.0, 1000.0)},
    "3V3_LMK": {},
    "0V9_MGTAVCC_VUP_N": {'V': (0.89, 0.9), 'I': (0.150, 0.154), 'P': (0.133, 0.138), 'T': (-1.0, 1000.0)},
    "1V8_VCCAUX_VUP": {'V': (1.796, 1.799), 'I': (1.27, 1.28), 'P': (2.28092, 2.30272), 'T': (-1.0, 1000.0)},
    "1V2_MGTAVTT_VUP_N": {'V': (1.1942, 1.1944), 'I': (0.35, 0.37), 'P': (0.41797, 0.441928), 'T': (42.0, 51.0)},
    "3V5_INTERMEDIATE": {'V': (0.0, 5.0), 'I': (0.5, 0.6), 'P': (0.0, 30.0), 'T': (53.0, 63.0)},
    "0V9_MGTAVCC_VUP_S": {'V': (0.89, 0.91), 'I': (0.15, 0.16), 'P': (0.1335, 0.1456), 'T': (36.0, 46.0)},
    "1V2_MGTAVTT_VUP_S": {'V': (1.196, 1.198), 'I': (0.37, 0.38), 'P': (0.44252, 0.45524), 'T': (35.0, 46.0)},
    "0V85_VCCINT_VUP": {'V': (-1.0, 200.0), 'I': (0, 30.0), 'P': (0.0, 6000.0), 'T': (-1.0, 1000.0)},
    "VIRTEXUPLUS": {}
}


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
    if target.keys() != measured.keys():
        print("GOT CONFLICTING LIST OF DEVICES!")
        self.power_down()
        sys.exit(-1)

    for device, measured_params in measured.items():
        target_params = target[device]


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
