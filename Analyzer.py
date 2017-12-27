## @package Analyzer
# Main package for Arkitest Analyzer

import AnalyzerSis
import argparse
import os
import sys

# Check and manage arguments
cmd_args = argparse.ArgumentParser(
    description="Analyzer for projects of the Computer Architecture course at University "
                "of Verona")
cmd_args.add_argument('-f',
                      type=str,
                      required="TRUE",
                      help="Specify the path of the archive that contains the projects")
cmd_args.add_argument('-inp',
                      type=str,
                      required="TRUE",
                      help="Specify the path of the simulation input")
cmd_args.add_argument('-out',
                      type=str,
                      required="TRUE",
                      help="Specify the path of the simulation output")
args = cmd_args.parse_args()

if not os.path.exists(args.f) or not os.path.isfile(args.f):
    print("An error occurred. Please specify the path of the archive that contains the projects.")
    sys.exit(1)
if not os.path.exists(args.inp) or not os.path.isfile(args.inp):
    print("An error occurred. Please specify the path of the simulation input.")
    sys.exit(1)
if not os.path.exists(args.out) or not os.path.isfile(args.out):
    print("An error occurred. Please specify the path of the simulation output.")
    sys.exit(1)

sis_simulation_input = str(os.path.abspath(args.inp))
sis_simulation_output = str(os.path.abspath(args.out))

sis_tar_directory = AnalyzerSis.extract_archive(str(os.path.abspath(args.f)))
if AnalyzerSis.check_fsmd(sis_tar_directory):
    AnalyzerSis.simulate(sis_tar_directory, sis_simulation_input, sis_tar_directory + "/out_exam.txt")
    print(AnalyzerSis.compare(sis_tar_directory + "/out_exam.txt",
                              AnalyzerSis.load_correct_outputs(sis_simulation_output)))
else:
    print("Something went wrong during archive extraction")
    sys.exit(1)
