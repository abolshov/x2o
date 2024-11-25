#!/usr/bin/python3

import sys
import os
import subprocess
import time

proc = subprocess.Popen("x2o octopus power_down", shell=True, executable="/bin/bash")
proc.wait()

print("")
print("DONE!")

