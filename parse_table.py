import re


def parse_monitor_table_v2(table):  
    """
    Parses a table and extracts rows containing words (letters, digits, underscores, and hyphens),
    mapping each key to a list of values.

    Args:
        table (str): The input table as a string.

    Returns:
        dict: A dictionary where keys are row names and values are dictionaries mapping parameters (V, I, P, T) to lists of values.
    """
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
                return [float(value.replace(unit, ""))] if value else []

            result[device] = {
                "V": clean_value(v, " V"),
                "I": clean_value(i, " A"),
                "P": clean_value(p, " W"),
                "T": [float(temp.replace(" C", "")) for temp in t.split(",")] if t else []
            }

    return result


table_v2 = """--------------------------------------------------------------------------------------------------------------
Device              	V		I		P		T
12V0                	0.845 V		          		          
3V3_STANDBY         	3.299 V		          		          
1V8_MACHXO2         	0.000 V		          		          
2V5_OSC_NE          	0.000 V		          		          
1V8_MGTVCCAUX_VUP_N 	0.000 V		          		          
2V5_OSC_NW          	0.000 V		          		          
1V8_MGTVCCAUX_VUP_S 	0.000 V		          		          
2V5_OSC_SW          	0.000 V		          		          
2V5_OSC_SE          	0.000 V		          		          
3V3_LMK             	0.000 V		          		          
0V9_MGTAVCC_VUP_N   	0.000 V		-0.00 A		-0.00 W
1V8_VCCAUX_VUP      	0.000 V		-0.00 A		-0.00 W
1V2_MGTAVTT_VUP_N   	0.000 V		+0.00 A		+0.00 W		23.2 C,22.0 C,22.9 C,21.9 C
3V5_INTERMEDIATE    	0.000 V		-0.00 A		-0.00 W		23.6 C,22.5 C
0V9_MGTAVCC_VUP_S   	0.000 V		-0.00 A		-0.00 W		22.8 C,21.5 C,22.8 C,21.4 C,23.0 C,21.4 C,22.8 C,21.7 C
1V2_MGTAVTT_VUP_S   	0.000 V		-0.00 A		-0.00 W		22.8 C,21.8 C,22.8 C,21.5 C
0V85_VCCINT_VUP     	0.000 V		-0.01 A		+0.00 W		0.0 C,0.0 C,0.0 C,0.0 C,0.0 C,0.0 C
--------------------------------------------------------------------------------------------------------------
VIRTEXUPLUS         	         	          	-0.00 W		22.8 C,25.4 C
--------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------

"""


def parse_monitor_table_v3(table):
    """
    Parses a table in the *MONITOR* format.

    Args:
        table (str): The input table as a string.

    Returns:
        dict: A dictionary where keys are row names and values are dictionaries with parameters (V, I, P, Tlocal, Tremote).
    """
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

# Example table input
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

table_v3 = """
*MONITOR*
Name                     V         I         P         Tlocal                   Tremote                  
=========================================================================================================
0V85_VCCINT_VUP          0.85      0.52      6.30      -                        -
0V9_MGTAVCC_VUP_N        0.90      0.12      1.47      -                        -               
0V9_MGTAVCC_VUP_S        0.90      0.12      1.47      23.44, 23.12, 24.06      25.75           
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

# Parse and print the result
res = parse_monitor_table_v2(table_v2)
# print(res)


# res = parse_table(table)
for key, val in res.items():
    print(f"{key}: {val}")