#!/usr/bin/python3

from dumbo.i2c import *
from dumbo.bitstream import bscan 
import sys
import os
import subprocess
import time

FIRMWARE_FILE = "/root/gem/fw/ge21_x2o-v5.0.3-60B3805-dirty_X2O_rev3_PROD_TEST_10G_v2_no_ibert/ge21_x2o-v5.0.3-60B3805-dirty.bit"

#jtag = bscan(0x43c10000)
#i2cbus = bus(1)
#octopus=octopus_rev2(i2cbus)

if not os.path.exists(FIRMWARE_FILE):
    print('File not found')
    sys.exit(-1)

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

