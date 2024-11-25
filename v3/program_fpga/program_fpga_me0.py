#!/usr/bin/python3

from dumbo.i2c import *
from dumbo.bitstream import bscan 
import sys
import os
import subprocess
import time

# X2O v2
#FIRMWARE_FILE = "/root/gem/fw/me0_x2o-v5.0.3-hog7F4AD48-dirty_X2Ov2_v4_with_LDAQ/me0_x2o-v5.0.3-hog7F4AD48-dirty.bit"
#FIRMWARE_FILE = "/root/gem/0xbefe/scripts/resources/x2o_csc.bit"

#X2O v3
#FIRMWARE_FILE = "/root/gem/fw/me0_x2o-v5.0.3-60B3805-dirty_one_stack_try1/me0_x2o-v5.0.3-60B3805-dirty.bit"
#FIRMWARE_FILE = "/root/gem/fw/me0_x2o-v5.0.3-60B3805-dirty_X2O_v3_full_1SLR_QPLL1/me0_x2o-v5.0.3-60B3805-dirty.bit"
#FIRMWARE_FILE = "/root/gem/fw/me0_x2o-v5.0.3-60B3805-dirty_v3_1OH_QPLL1_DAQ100/me0_x2o-v5.0.3-60B3805-dirty.bit"
FIRMWARE_FILE = "/root/gem/fw/me0_x2o-v5.0.3-D7AB225-dirty_v3_full_4SLR_4_2_OH/me0_x2o-v5.0.3-D7AB225-dirty.bit"

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

