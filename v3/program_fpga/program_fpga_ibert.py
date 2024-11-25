#!/usr/bin/python3

from dumbo.i2c import *
from dumbo.bitstream import bscan 
import sys
import os
import subprocess
import time

FIRMWARE_FILE = "/root/gem/fw/example_ibert_25p625g_all.bit" # 12.5G Q126 Q127
#FIRMWARE_FILE = "/root/gem/fw/ibert_12p5g_q126_127/example_x2o_ibert_12p5g_slr1.bit" # 12.5G Q126 Q127

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

print("")
print("DONE!")

