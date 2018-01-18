"""@package Analyzer
Functions for SIS
"""

import os
import re
import tarfile
import subprocess


def extract_archive(sis_tarball):
    """
    Extract archive in a sub-directory
    :param sis_tarball: The tarball file path
    :return: Path of the directory
    """
    tar_directory = sis_tarball.split('.')[0]
    if not os.path.exists(tar_directory):
        os.makedirs(tar_directory)

    try:
        with tarfile.open(sis_tarball, "r") as tar:
            tar.extractall(path=tar_directory)
            tar.close()
    except IOError:
        return ""
    return tar_directory


def check_extraction_directory(sis_tar_directory):
    """
    Check for FSMD.blif presence
    :param sis_tar_directory: The directory containing the SIS files
    :return: True if it exists, False otherwise
    """
    return os.path.exists(sis_tar_directory + "/FSMD.blif")


def simulate(sis_tar_directory, sis_simulation_input, sis_simulation_output):
    """
    Simulate the circuit with SIS
    :param sis_tar_directory: The directory containing the SIS files
    :param sis_simulation_input: The input to be simulated
    :param sis_simulation_output: Path to save the outputs
    :return: 0 if everything is ok, otherwise -1
    """
    sis_command = "(cd " + sis_tar_directory + "; sis -t pla -f script_exam.txt \-x)"
    sis_script = sis_tar_directory + "/script_exam.txt"
    sis_simulation_script = "set sisout " + sis_simulation_output + "\n" + \
                            "read_blif " + sis_tar_directory + "/FSMD.blif\n" + \
                            "source " + sis_simulation_input + "\n" + \
                            "read_library synch.genlib\n" + \
                            "map -m 0 -W\n" + \
                            "print_map_stats\n" + \
                            "quit"
    try:
        with open(sis_script, "w") as s:
            s.write(sis_simulation_script)
        subprocess.Popen(sis_command, stdout=subprocess.PIPE, shell=True).communicate()  # Launch SIS subprocess
    except IOError:
        return -1
    return 0


def compare(sis_simulation_output, sis_correct_outputs):
    """
    Compare the student's circuit output with the correct one
    :param sis_simulation_output: File containing the simulated outputs
    :param sis_correct_outputs: File containing the correct outputs
    :return: Percentage of correctness, otherwise -1
    """
    correct_outputs = list()
    pattern = re.compile("^(Outputs:\s)?([0-1].+)$")
    try:
        with open(sis_correct_outputs, "r") as infile:
            for line in infile:
                if pattern.match(line):
                    correct_outputs.append(line.lstrip("Outputs: ").replace(" ", "").strip())
        match = 0
        i = 0
        with open(sis_simulation_output, "r") as infile:
            for line in infile:
                if pattern.match(line):
                    if line.lstrip("Outputs: ").replace(" ", "").strip() == correct_outputs[i]:
                        match += 1
                    i += 1
        return float(match) / float(i) * 100.0
    except IOError:
        return -1
