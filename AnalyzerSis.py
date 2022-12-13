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
    tar_directory = os.path.split(sis_tarball)[0]
    if not os.path.exists(tar_directory):
        os.makedirs(tar_directory)

    try:
        with tarfile.open(sis_tarball, "r") as tar:
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(tar, path=tar_directory)
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
    :return: Tuple containing percentage of correctness, circuit area, most negative slack and total gates,otherwise -1
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
        area = 0
        slack = 0
        gate_count = 0
        with open(sis_simulation_output, "r") as infile:
            for line in infile:
                if pattern.match(line):
                    if line.lstrip("Outputs: ").replace(" ", "").strip() == correct_outputs[i]:
                        match += 1
                    i += 1
                elif line.startswith("Total Area"):
                    area = float(line.split('=')[1].strip())
                elif line.startswith("Most Negative Slack"):
                    slack = -(float(line.split('-')[1].strip()))
                elif line.startswith("Gate Count"):
                    gate_count = int(line.split('=')[1].strip())
        return float(match) / float(i) * 100.0, area, slack, gate_count
    except IOError:
        return -1
