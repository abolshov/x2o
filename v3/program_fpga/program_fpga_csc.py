#!/usr/bin/python3

from dumbo.i2c import *
from dumbo.bitstream import bscan 
import sys
import os
import subprocess
import time

#FIRMWARE_FILE = "/root/csc/fw/x2o/csc_x2o-v5.0.3-hog7F4AD48-dirty_X2Ov2_test_tcds_polarity3/csc_x2o-v5.0.3-hog7F4AD48-dirty.bit"
#FIRMWARE_FILE = "/root/csc/fw/x2o/csc_x2o-v5.0.3-hog7F4AD48-dirty_X2Ov2_v3_ODMB_cage24_DMB_cage25_TTC_cage23_GBT_cage22/csc_x2o-v5.0.3-hog7F4AD48-dirty.bit"
#FIRMWARE_FILE = "/root/csc/fw/x2o/csc_x2o-v5.0.3-hog83E86F4-dirty_X2Ov2_v4_ODMB_cages_4_5_DMB_LDAQ_cage_23/csc_x2o-v5.0.3-hog83E86F4-dirty.bit" # 2 ODMBs on top cages
# LAST USED ==> #FIRMWARE_FILE = "/root/csc/fw/x2o/csc_x2o-v5.0.3-hog39C227A-dirty_X2Ov2_v6_ODMB_cages_4_5_DMB_LDAQ_cage_23_NEW/csc_x2o-v5.0.3-hog39C227A-dirty.bit" # with ALCT PROMless
#FIRMWARE_FILE = "/root/gem/0xbefe/scripts/resources/x2o_csc.bit"
#FIRMWARE_FILE = "/root/csc/fw/x2o/csc_x2o-v5.0.3-hog39C227A-dirty_X2Ov2_v6_ODMB_cages_4_5_DMB_LDAQ_cage_23_NEW/csc_x2o-v5.0.3-hog39C227A-dirty.bit" # with ALCT PROMless

# FULL fw X2O v2
#FIRMWARE_FILE = "/root/csc/fw/x2o/csc_x2o-v5.0.3-60B3805-dirty_FULL_SCALE_v2_DAQ_200_some_timing_fails/csc_x2o-v5.0.3-60B3805-dirty.bit"
#FIRMWARE_FILE = "/root/csc/fw/x2o/csc_x2o-v5.0.3-60B3805-dirty_FULL_SCALE_v2_DAQ_100/csc_x2o-v5.0.3-60B3805-dirty.bit"
#FIRMWARE_FILE = "/root/csc/fw/x2o/csc_x2o-v5.0.3-60B3805-dirty_FULL_SCALE_v2_DAQ_100_fixed_clk_period/csc_x2o-v5.0.3-60B3805-dirty.bit"
#FIRMWARE_FILE = "/root/csc/fw/x2o/csc_x2o-v5.0.3-60B3805-dirty_FULL_SCALE_v3_DAQ_100_SR_fix/csc_x2o-v5.0.3-60B3805-dirty.bit"
#FIRMWARE_FILE = "/root/csc/fw/x2o/csc_x2o-v5.0.3-60B3805-dirty_FULL_SCALE_v4_LDAQ_EOE_fix/csc_x2o-v5.0.3-60B3805-dirty.bit"

# FULL fw X2O v3
#FIRMWARE_FILE = "/root/gem/fw/csc_x2o-v5.0.3-60B3805-dirty_X2O_v3_full/csc_x2o-v5.0.3-60B3805-dirty.bit"
FIRMWARE_FILE = "/root/gem/fw/csc_x2o-v5.0.3-60B3805-dirty_X2O_v3_full/csc_x2o-v5.0.3-60B3805-dirty.dat"


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

