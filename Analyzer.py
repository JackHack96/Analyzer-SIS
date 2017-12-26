import argparse
import os
import sys
import re
import tarfile
import subprocess

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
sis_tarball = str(os.path.abspath(args.f))
if not os.path.exists(args.inp) or not os.path.isfile(args.inp):
    print("An error occurred. Please specify the path of the simulation input.")
    sys.exit(1)
sis_simulation_input = str(os.path.abspath(args.inp))
if not os.path.exists(args.out) or not os.path.isfile(args.out):
    print("An error occurred. Please specify the path of the simulation output.")
    sys.exit(1)
sis_simulation_output = str(os.path.abspath(args.out))

# Creates a list reporting all simulation outputs used to compare the student simulation output
correct_outputs = list()
pattern = re.compile("^(Outputs:\s)?([0-1\s]+)$")
with open(sis_simulation_output, "r") as infile:
    for line in infile:
        if line and pattern.match(line):
            correct_outputs.append(line.lstrip("Outputs: ").replace(" ", "").strip())

# Extract archive in a sub-directory
sis_tar_directory = sis_tarball.split('.')[0]
if not os.path.exists(sis_tar_directory):
    os.makedirs(sis_tar_directory)
with tarfile.open(sis_tarball, "r") as tar:
    tar.extractall(path=sis_tar_directory)
    tar.close()

# Check if the directory contains FSMD.blif
if not os.path.exists(sis_tar_directory + "/FSMD.blif"):
    print("No FSMD.blif file found! Please check the project!")
    sys.exit(1)
sis_fsmd_path = sis_tar_directory + "/FSMD.blif"

# Create the SIS commands for simulating the circuit
sis_command = "(cd " + sis_tar_directory + "; sis -t pla -f script_exam.txt -x)"
sis_script = sis_tar_directory + "/script_exam.txt"
sis_simulation_script = "set sisout out_exam.txt\n" \
                        "read_blif " + sis_fsmd_path + "\n" + \
                        "source " + sis_simulation_input + "\n" + \
                        "read_library synch.genlib\n" + \
                        "map -m 0 -W\n" + \
                        "print_map_stats\n" + \
                        "quit"
with open(sis_script, "w") as s:
    s.write(sis_simulation_script)
subprocess.Popen(sis_command, stdout=subprocess.PIPE, shell=True).communicate()  # Launch SIS subprocess

# Compare the student's circuit output with the correct one
sis_output_file = sis_tar_directory + "/out_exam.txt"
if os.path.exists(sis_output_file) and os.path.isfile(sis_output_file):
    i = 0
    match = 0
    with open(sis_output_file, "r") as infile:
        for line in infile:
            if pattern.match(line) and line != "\n":
                bits = line.lstrip("Outputs: ").strip()
                if bits.replace(" ", "") == correct_outputs[i]:
                    match += 1
                i += 1

    if match != len(correct_outputs):
        print("Output did not match")
        sys.exit(1)

    print("Correctness: " + str(float(match) / len(correct_outputs) * 100.0))
else:
    print("An error occurred during the simulation")
    sys.exit(1)
