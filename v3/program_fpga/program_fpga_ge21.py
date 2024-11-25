#!/usr/bin/python3

from dumbo.i2c import *
from dumbo.bitstream import bscan 
import sys
import os
import subprocess
import time

#FIRMWARE_FILE = "/root/gem/fw/ge21_x2o-v5.0.3-hog7F4AD48-dirty_X2Ov2_v4_with_LDAQ/ge21_x2o-v5.0.3-hog7F4AD48-dirty.bit"
#FIRMWARE_FILE = "/root/gem/fw/ge21_x2o-v5.0.3-hog9DEAC8A-dirty__SPECIAL_FOR_CSC_ALCT_TEST_X2O_v2_AND_SLINK/ge21_x2o-v5.0.3-hog9DEAC8A-dirty.bit" # CSC ALCT and SLINK TEST FW
#FIRMWARE_FILE = "/root/gem/fw/ge21_x2o-v5.0.3-hog9DEAC8A-dirty__SPECIAL_FOR_CSC_ALCT_TEST_X2O_v2/ge21_x2o-v5.0.3-hog9DEAC8A-dirty.bit" # CSC ALCT and SLINK TEST FW
#FIRMWARE_FILE = "/root/gem/fw/ge21_x2o-v5.0.3-60B3805-dirty_X2O_v3_4OH_fixed/ge21_x2o-v5.0.3-60B3805-dirty.bit" # v3 X2O normal firmware with 4OH
FIRMWARE_FILE = "/root/gem/fw/ge21_x2o-v5.0.3-D7AB225-dirty_v3_full_4_SLR_8_OH/ge21_x2o-v5.0.3-D7AB225-dirty.bit" # v3 X2O full scale firmware with 4 SLRs and 8 OHs in each SLR

if not os.path.exists(FIRMWARE_FILE):
    print('File not found: %s' % FIRMWARE_FILE)
    sys.exit(-1)

load_cmd = "load_bitstream_top" if FIRMWARE_FILE.endswith("bit") else "load_bitstream_top_decoded" if FIRMWARE_FILE.endswith("dat") else None

if load_cmd is None:
    print("ERROR: unrecognized file format: %s" % FIRMWARE_FILE)
    sys.exit(-1)

#proc = subprocess.Popen("insmod /root/libs/control/drivers/dma_proxy_128_us.ko", shell=True, executable="/bin/bash")
#proc.wait()
proc = subprocess.Popen("x2o control %s %s" % (load_cmd, FIRMWARE_FILE), shell=True, executable="/bin/bash")
proc.wait()
time.sleep(3)
proc = subprocess.Popen("x2o control reset_c2c_top", shell=True, executable="/bin/bash")
proc.wait()

print("")
print("DONE!")

