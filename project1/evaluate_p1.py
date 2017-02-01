#!/usr/bin/python3

__author__ = "Colin Burgin"
__copyright__ = "Copyright 2017"
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Colin Burgin"
__email__ = "cburgin707@gmail.com"
__status__ = "Incomplete"

# Evaluator for project Digital Design 2 Project 1
# Using python 3

import sys, os, argparse, subprocess, shutil

class evaluate_p1:
    '''Evaluator for DD2 P1'''
    def __init__(self, args):
        self.project_name = "nicetimer"
        self.args = args
        self.infile = ''
        self.parse_args()
        self.build_test_env()
        self.build_from_qar()
        self.program_sof()

    def parse_args(self):
        # Parse the command line arguments provided at runtime
        parser= argparse.ArgumentParser(description="Evaluate DD2 P1 sumbissions")
        parser.add_argument('-q', '--QAR', dest='quartus_archive', metavar='Q',
                            nargs='?', default=None,
                            help='Quartus Archive file name')
        parser.add_argument('-d', '--device', dest='device_id', metavar='D',
                            nargs='?', default="02D120DD",
                            help='FPGA Device ID')
        # Parse the input arguments
        args = parser.parse_args()
        self.device_id = args.device_id
        if args.quartus_archive is not None:
            self.infile = args.quartus_archive
        else:
            print("Please supply a .qar to test")

    def build_test_env(self):
    # Build test env for project
        print("\n***Building Test Directory***\n")
        # Create a new directory for testing this project and replace if necessary
        if os.path.exists("__PUT__"):
            shutil.rmtree("__PUT__")
        os.makedirs("__PUT__", exist_ok=True)
        # Write the file to new directory
        shutil.copyfile(self.infile, "__PUT__/"+self.infile)

    def build_from_qar(self):
    # Unarchive the project file supplied
        os.chdir("__PUT__/")
        # First, unarchive the project
        print("\n***Restoring Project from Archive***\n")
        subprocess.call(["quartus_sh","--restore", self.project_name])
        # Second, run the Quartus mapper
        print("\n***Running the Quartus Mapper***\n")
        subprocess.call(["quartus_map", self.project_name])
        # Third, run the Quartus fitter
        print("\n***Running the Quartus Fitter***\n")
        subprocess.call(["quartus_fit", self.project_name])
        # Fourth, run the Quartus assembler
        print("\n***Running the Quartus Assembler***\n")
        subprocess.call(["quartus_asm", self.project_name])

    def program_sof(self):
    # Program the SOF onto the board, wait for user input
        # Program with the SOF
        print("\n***Programming the Board with SOF***\n")
        curr_device = subprocess.check_output(["jtagconfig", "--enum"]).decode("utf-8")
        # Find device to be programs index in the device chain
        device_opts = curr_device.strip().split("\n")
        device_cable = str(device_opts[0]).split(" ").strip()[1:]
        for i in device_opts:
            if i.find(self.device_id) is not -1:
                device_index = device_opts.index(i)
                break

        # Program the SOF
        file_to_test = "P;" + self.project_name + ".sof@" + str(device_index)
        commands = ["-C", device_cable, "-m", "jtag", "-o", file_to_test]
        subprocess.call(["quartus_pgm", "-c", device_cable, "-m", "jtag", "-o", file_to_test])
        # Get user comments on functionality
        functionality_comments = input("Functionality: ")

def main(argv):
    eval = evaluate_p1(argv)

if __name__ == "__main__":
    main(sys.argv[1:])
