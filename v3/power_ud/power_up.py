#!/usr/bin/python3

import sys
import os
import subprocess
import time

proc = subprocess.Popen("x2o control payload_on", shell=True, executable="/bin/bash")
proc.wait()
time.sleep(1)
proc = subprocess.Popen("x2o octopus configure", shell=True, executable="/bin/bash")
proc.wait()
time.sleep(0.1)
proc = subprocess.Popen("x2o octopus power_up", shell=True, executable="/bin/bash")
proc.wait()

print("")
print("DONE!")

