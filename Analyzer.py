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
from enum import Enum


class Error(Enum):
    MISSING_PROJECT_ARCHIVE = 2
    MISSING_CORRECT_INPUT = 3
    MISSING_CORRECT_OUTPUT = 4
    CORRECTNESS_CALCULATION_ERROR = 5
    SIMULATION_ERROR = 6
    MALFORMED_ARCHIVE = 7
    UNIDENTIFIED_PROJECT_TYPE = 8
    NOT_A_TARBALL = 9


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
    sys.exit(Error.MISSING_PROJECT_ARCHIVE.value)
if not os.path.exists(args.inp) or not os.path.isfile(args.inp):
    print("An error occurred. Please specify the path of the simulation input.")
    sys.exit(Error.MISSING_CORRECT_INPUT.value)
if not os.path.exists(args.out) or not os.path.isfile(args.out):
    print("An error occurred. Please specify the path of the simulation output.")
    sys.exit(Error.MISSING_CORRECT_OUTPUT.value)

simulation_input = str(os.path.abspath(args.inp))
correct_outputs = str(os.path.abspath(args.out))
tar_archive = str(os.path.abspath(args.file))

if tar_archive.endswith(".tar.gz") or tar_archive.endswith(".tar.xz"):
    if "sis" in tar_archive:
        sis_tar_directory = AnalyzerSis.extract_archive(tar_archive)
        if AnalyzerSis.check_extraction_directory(sis_tar_directory):
            if AnalyzerSis.simulate(sis_tar_directory, simulation_input, sis_tar_directory + "/out_exam.txt") == 0:
                correctness = AnalyzerSis.compare(sis_tar_directory + "/out_exam.txt", correct_outputs)
                if correctness > 0:
                    print(correctness)
                    sys.exit(0)
                else:
                    print("Error during correctness calculation")
                    sys.exit(Error.CORRECTNESS_CALCULATION_ERROR.value)
            else:
                print("Something went wrong during the simulation")
                sys.exit(Error.SIMULATION_ERROR.value)
        else:
            print("The archive does not respect the correct structure")
            sys.exit(Error.MALFORMED_ARCHIVE.value)

    elif "asm" in tar_archive:  # TODO: da fare gestione assembly
        asm_tar_directory = AnalyzerSis.extract_archive(tar_archive)

    else:
        print("Error! Project not identified!")
        sys.exit(Error.UNIDENTIFIED_PROJECT_TYPE.value)
else:
    print("The given archive is not a TAR archive")
    sys.exit(Error.NOT_A_TARBALL.value)
