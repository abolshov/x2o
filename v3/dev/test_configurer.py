import argparse
import os
from x2o3_configurer import x2o3_onfigurer


def main():
    parser = argparse.ArgumentParser(prog="test_configurer", description="test for x2o3_configurer")
    parser.add_argument("freq", type=int, help="Frequency of BP clock")
    parser.add_argument("board_type", type=str, help="Type of the board x2o is talking to")
    parser.add_argument("verbosity", type=int, help="Monitoring verbosity")

    args = parser.parse_args()
    freq = args.freq
    board_type = args.board_type
    v = args.verbosity

    print("Configuring x2o v2")
    conf = x2o3_configurer(freq, board_type, v)

    print("Initial board monitor check:")
    conf.monitor()

    print("Powering up the board:")
    conf.power_up()

    print("Power up board monitor check:")
    conf.monitor()

    print(f"Confugring clock: frequency {freq} MHz")
    conf.config_clock()

    print(f"Programming FPGA: {board_type}")
    conf.program_FPGA()

    print("Powering down the board:")
    conf.power_down()

    print("Final board monitor check:")
    conf.monitor()


if __name__ == "__main__":
    main()