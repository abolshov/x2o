import argparse
import os
from x2o2Configurer import x2o2Configurer


# format: clock frequency(?) : config_file
clock_map = { 40: "/root/gem/clk_config/DPLLandAPLL2_Input_40p0786_Out0_40p0786_Out1_320p6288_OutOthers_160p3144_ZDM_EN_in_REF1.txt",
              320: "/root/gem/clk_config/DPLLandAPLL2_Input_40p0786_Out0_40p0786_Out1_320p6288_OutOthers_160p3144_ZDM_EN_in_REF0.txt" }

# format: board_type : fw_file
fpga_map = { "ge21": "/root/gem/fw/ge21_x2o-v5.0.3-hog7F4AD48-dirty_X2Ov2_v4_with_LDAQ/ge21_x2o-v5.0.3-hog7F4AD48-dirty.bit",
             "me0": "/root/gem/fw/me0_x2o-v5.0.3-hog7F4AD48-dirty_X2Ov2_v4_with_LDAQ/me0_x2o-v5.0.3-hog7F4AD48-dirty.bit" }

def main():
    parser = argparse.ArgumentParser(prog="configure_x2o2", description="Configures x2o v2 board")
    parser.add_argument("freq", type=int, help="Frequency of BP clock")
    parser.add_argument("board_type", type=str, help="Type of the board x2o is talking to")
    parser.add_argument("verbosity", type=int, help="Monitoring verbosity")

    args = parser.parse_args()
    freq = args.freq
    board_type = args.board_type
    v = args.verbosity
    # clk_cfg = clock_map[freq]
    # fw_file = fpga_map[board_type]

    if not os.path.exists(fw_file):
        print("WARNING! FIRMWARE FILE NOT FOUND, SHUTTING DOWN.")
        sys.exit(-1)

    print("Configuring x2o v2")
    x2o2_configurer = x2o2Configurer(freq, board_type, v)

    print("Initial board monitor check:")
    x2o2_configurer.monitor()

    print("Powering up the board:")
    x2o2_configurer.power_up()

    print("Power up board monitor check:")
    x2o2_configurer.monitor()

    print(f"Confugring clock: frequency {freq} MHz")
    x2o2_configurer.config_clock()

    print(f"Programming FPGA: {board_type}")
    x2o2_configurer.program_FPGA()

    print("Powering down the board:")
    x2o2_configurer.power_down()

    print("Final board monitor check:")
    x2o2_configurer.monitor()


if __name__ == "__main__":
    main()
