#!/usr/bin/env python3

## @package Analyzer
# Main package for Arkitest Analyzer
#
#   AAA   RRRRRR  KK  KK IIIII TTTTTTT EEEEEEE  SSSSS  TTTTTTT
#  AAAAA  RR   RR KK KK   III    TTT   EE      SS        TTT
# AA   AA RRRRRR  KKKK    III    TTT   EEEEE    SSSSS    TTT
# AAAAAAA RR  RR  KK KK   III    TTT   EE           SS   TTT
# AA   AA RR   RR KK  KK IIIII   TTT   EEEEEEE  SSSSS    TTT
#
# @author Matteo Iervasi, Mirko Morati, Andrea Toaiari

import AnalyzerSis
import AnalyzerAsm
import argparse
import os
import sys

# Check and manage arguments
parser = argparse.ArgumentParser(description="Analyzer for projects of the Computer Architecture course at "
                                             "University of Verona")
cmd_args = parser.add_argument_group("required arguments")
cmd_args.add_argument("-f", "--file",
                      type=str,
                      help="Specify the path of the archive that contains the projects",
                      required=True)
cmd_args.add_argument("-i", "--inp",
                      type=str,
                      help="Specify the path of the simulation input",
                      required=True)
cmd_args.add_argument("-o", "--out",
                      type=str,
                      help="Specify the path of the simulation output",
                      required=True)
args = parser.parse_args()

if not os.path.exists(args.file) or not os.path.isfile(args.file):
    print("An error occurred. Please specify the path of the archive that contains the projects.")
    sys.exit(-1)
if not os.path.exists(args.inp) or not os.path.isfile(args.inp):
    print("An error occurred. Please specify the path of the simulation input.")
    sys.exit(-1)
if not os.path.exists(args.out) or not os.path.isfile(args.out):
    print("An error occurred. Please specify the path of the simulation output.")
    sys.exit(-1)

simulation_input = str(os.path.abspath(args.inp))
correct_outputs = str(os.path.abspath(args.out))
tar_directory = str(os.path.abspath(args.file))

if "sis" in tar_directory:
    sis_tar_directory = AnalyzerSis.extract_archive(tar_directory)
    if sis_tar_directory != "":
        if AnalyzerSis.simulate(sis_tar_directory, simulation_input, sis_tar_directory + "/out_exam.txt") == 0:
            correctness = AnalyzerSis.compare(sis_tar_directory + "/out_exam.txt", correct_outputs)
            if correctness > 0:
                print(correctness)
            else:
                print("Error during correctness calculation")
                sys.exit(-1)
        else:
            print("Something went wrong during the simulation")
            sys.exit(-1)
    else:
        print("Error during archive extraction")
        sys.exit(-1)

elif "asm" in tar_directory:  # TODO: da fare gestione assembly
    asm_tar_directory = AnalyzerSis.extract_archive(tar_directory)

else:
    print("Error! Project not identified!")
