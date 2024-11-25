import re


def parse_table(table):  
    """
    Parses a table and extracts rows containing words (letters, digits, underscores, and hyphens).

    Args:
        table (str): The input table as a string.

    Returns:
        dict: A dictionary where keys are row names and values are dictionaries with parameters (V, I, P, T).
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
                return float(value.replace(unit, "")) if value else None

            result[device] = {
                "V": clean_value(v, " V"),
                "I": clean_value(i, " A"),
                "P": clean_value(p, " W"),
                "T": [float(temp.replace(" C", "")) for temp in t.split(",")] if t else None
            }

    return result


table = """--------------------------------------------------------------------------------------------------------------
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

res = parse_table(table)
for key, val in res.items():
    print(f"{key}: {val}")