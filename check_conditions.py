import re
import sys


dummy = {'V': (-1.0, 200.0), 'I': (-1.0, 30.0), 'P': (-1.0, 6000.0), 'T': (-1.0, 1000.0)}

'''
device : list [V, I, P, T] of tuples (min, max) for each parameter
'''
conditions_dict = {
    "12V0" : dummy,
    "3V3_STANDBY": dummy,
    "1V8_MACHXO2": dummy,
    "2V5_OSC_NE": {'V': (2.504, 2.506), 'I': (0, 30.0), 'P': (0.0, 75.18), 'T': (-1.0, 1000.0)},
    "1V8_MGTVCCAUX_VUP_N": {'V': (1.8138, 1.8144), 'I': (0, 30.0), 'P': (0.0, 55.0), 'T': (-1.0, 1000.0)},
    "2V5_OSC_NW": {'V': (2.5162, 2.5164), 'I': (0, 30.0), 'P': (0.0, 75.492), 'T': (-1.0, 1000.0)},
    "1V8_MGTVCCAUX_VUP_S": {'V': (1.817, 1.8194), 'I': (0, 30.0), 'P': (0.0, 55.0), 'T': (-1.0, 1000.0)},
    "2V5_OSC_SW": {'V': (2.512, 2.514), 'I': (0, 30.0), 'P': (0.0, 75.42), 'T': (-1.0, 1000.0)},
    "2V5_OSC_SE": dummy,
    "3V3_LMK": dummy,
    "0V9_MGTAVCC_VUP_N": {'V': (0.89, 0.9), 'I': (0.150, 0.154), 'P': (0.133, 0.138), 'T': (-1.0, 1000.0)},
    "1V8_VCCAUX_VUP": {'V': (1.796, 1.799), 'I': (1.27, 1.28), 'P': (2.28092, 2.30272), 'T': (-1.0, 1000.0)},
    "1V2_MGTAVTT_VUP_N": {'V': (1.1942, 1.1944), 'I': (0.35, 0.37), 'P': (0.41797, 0.441928), 'T': (42.0, 51.0)},
    "3V5_INTERMEDIATE": {'V': (0.0, 5.0), 'I': (0.5, 0.6), 'P': (0.0, 30.0), 'T': (53.0, 63.0)},
    "0V9_MGTAVCC_VUP_S": {'V': (0.89, 0.91), 'I': (0.15, 0.16), 'P': (0.1335, 0.1456), 'T': (36.0, 46.0)},
    "1V2_MGTAVTT_VUP_S": {'V': (1.196, 1.198), 'I': (0.37, 0.38), 'P': (0.44252, 0.45524), 'T': (35.0, 46.0)},
    "0V85_VCCINT_VUP": dummy,
    "VIRTEXUPLUS": dummy
}



def parse_monitor_table_v3(table):
    result = {}

    # Define regex to match rows with values in the *MONITOR* format
    row_pattern = re.compile(r"""
        ^(?P<name>[^\s]+)\s+               # Name of the device (non-whitespace characters)
        (?P<V>\d+\.\d+|-)\s+               # Voltage (or - for none)
        (?P<I>\d+\.\d+|-)\s+               # Current (or - for none)
        (?P<P>\d+\.\d+|-)\s+               # Power (or - for none)
        (?P<T>[\d\.\,\s-]*)$
    """, re.VERBOSE)

    for line in table.splitlines():
        match = row_pattern.match(line)
        if match:
            name = match.group("name")
            v = match.group("V")
            i = match.group("I")
            p = match.group("P")
            t = match.group("T")

            # Clean and convert values to lists
            def clean_value(value):
                symbols = [c[:-1] if c.endswith(',') else c for c in value.strip().split(' ') if c != '']
                res = []
                for sym in symbols:
                    if sym == '-':
                        continue
                    else:
                        res.append(float(sym))
                return res


            result[name] = {
                "V": [float(v)] if v != "-" else [],
                "I": [float(i)] if i != "-" else [],
                "P": [float(p)] if p != "-" else [],
                "T": clean_value(t)
            }

    return result


def check_conditions(table):
    monitoring_result = parse_monitor_table_v3(table)

    if set(conditions_dict.keys()) != set(monitoring_result.keys()):
        print("GOT CONFLICTING LIST OF DEVICES!")
        sys.exit(-1)

    for device, measured_params in monitoring_result.items():
        target_params = conditions_dict[device]

        # loop over V, I, P, T and measured values
        for quantity, measured_values in measured_params.items():
            min_spec, max_spec = target_params[quantity]
            # loop over each measured value and compare it with allowed
            for val in measured_values:
                if val < min_spec or val > max_spec:
                    print(f"ACHTUNG! DEVICE {device} HAS QUANTITY {quantity}={val}, NOT IN [{min_spec}, {max_spec}]")
                    print("SHUTTING BOARD DOWN")
                    sys.exit(-1)

    print("ALL CHECKS SUCCESSFULLY DONE!")


table_v3 = """
*MONITOR*
Name                     V         I         P         Tlocal                   Tremote                  
=========================================================================================================
0V85_VCCINT_VUP          0.85      0.52      6.30      24.62, 25.12, 25.47      30.53, 31.31, 31.09      
0V9_MGTAVCC_VUP_N        0.90      0.12      1.47      23.69, 23.25             25.75, 25.44             
0V9_MGTAVCC_VUP_S        0.90      0.12      1.47      23.44, 23.12             25.75, 25.44             
12V0                     12.04     -         -         -                        -                        
1V2_MGTAVTT_VUP_N        1.20      0.14      1.66      24.75, 24.06             27.56, 26.81             
1V2_MGTAVTT_VUP_S        1.20      0.13      1.60      23.88, 23.69             27.31, 27.19             
1V8_MACHXO2              1.78      -         -         -                        -                        
1V8_MGTVCCAUX_VUP_N      1.81      -         -         -                        -                        
1V8_MGTVCCAUX_VUP_S      1.81      -         -         -                        -                        
1V8_VCCAUX_VUP           1.79      1.02      3.52      -                        -                        
2V5_OSC_NE               2.48      -         -         -                        -                        
2V5_OSC_NW               2.48      -         -         -                        -                        
2V5_OSC_SE               2.48      -         -         -                        -                        
2V5_OSC_SW               2.48      -         -         -                        -                        
3V3_LMK                  3.22      -         -         -                        -                        
3V3_STANDBY              3.30      -         -         -                        -                        
3V5_INTERMEDIATE         3.39      0.00      0.00      25.38                    32.25                    
---------------------------------------------------------------------------------------------------------
VIRTEXUPLUS              -         -         16.03     23.06                    25.94                    
---------------------------------------------------------------------------------------------------------
BOARD POWER:             -         -         16.03     -                        -
"""

check_conditions(table_v3)