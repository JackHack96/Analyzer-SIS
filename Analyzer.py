# -*- coding: utf-8 -*-
# !/usr/bin/env python

import argparse
import os
import os.path
import re
import shutil
import subprocess
import sys
import tarfile
from glob import glob

##
## @file SIS analyzer
## @author Adriano Tumminelli, Matteo Iervasi
##
## <!----------------------------------------------------------------------------------------------
## @usage
## python analyzer.py -d <PROJECTS_DIR> -inp <ABS_INPUT_PATH> -out <ABS_OUTPUT_PATH>
## ----------------------------------------------------------------------------------------------->

# ------------------------
# Configuration
# ------------------------
areaExpected = 2500
areaWeight = 2

slackExpected = 23
slackWeight = 0.1


# ------------------------

def subprocess_cmd(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    stdout_data, stderr_data = process.communicate()


def shellspace(string):
    return string.replace(" ", "\ ")


# case insensitive file exists
def file_exists_ci(directory, filename):
    for path in glob(directory + "/*"):
        base, fname = os.path.split(path)
        if fname.lower() == filename.lower():
            return True
    return False


def get_blif_directory(directory, subDir=False):
    for path in glob(directory + "/*"):
        base, fname = os.path.split(path)
        if file_exists_ci(directory, "fsmd.blif"):
            if subDir:
                return base, "<a class='info'> (sub-directory)</a>"
            else:
                return base, ""
        elif os.path.isdir(path):
            return get_blif_directory(path, True)
    return "", "<a class='error'> (missing directory)</a>"


def get_fsmd_real_name(directory):
    for path in glob(directory + "/*"):
        base, fname = os.path.split(path)
        if fname.lower() == 'fsmd.blif':
            if fname == "FSMD.blif":
                return fname, ""
            else:
                return fname, " <a class='info'>(wrong filename)</a>"
    return "FSMD.blif", "Missing FSMD"


# output
outputList = list()


def check_students(files, extension, start_index):
    idx = start_index

    pattern = re.compile("^Outputs:\s([0-1\s]+)$")

    for f in files:

        tarFileName = os.path.basename(f).split('.')[0]
        print("\n-------------------------\n" + str(idx) + ") " + tarFileName + " \n-------------------------\n")
        extractPath = './exams/' + tarFileName
        # create a sub-directory for each student
        if not os.path.exists(extractPath):
            os.makedirs(extractPath)

        fileExtension = '.'.join(os.path.basename(f).split('.')[1:])
        groups = tarFileName.lstrip('sis_').split('_')
        studentsList = []
        groups = tarFileName.lstrip('sis_').split('_')
        while len(groups):
            studentsList.append(' '.join(groups[:2]).title())
            groups = groups[2:]

        area = sys.maxint
        slack = sys.maxint
        status = ""
        sim = ""

        if f.endswith(extension):

            match = 0
            dirName = os.path.basename(f).split('.')[0]
            warning_extraction_text = "<a class='extract'> WARNING. An error occurred during file extraction.</a>"

            try:
                tar = tarfile.open(f, "r")
                tar.extractall(path=extractPath)
                tar.close()
            except:
                command = "tar zxvf " + shellspace(f) + " -C " + shellspace(extractPath)
                try:
                    subprocess_cmd(command)
                except:
                    status = warning_extraction_text + "Command: %s" % command

            if status == "":

                blifRealDir, dirCheck = get_blif_directory(extractPath)
                blifRealFilename, filenameCheck = get_fsmd_real_name(blifRealDir)
                fsmdPath = blifRealDir + "/" + blifRealFilename
                studentSimulationPath = blifRealDir + "/simulation_output.txt"
                scriptPath = blifRealDir + "/script_exam.txt"
                outExamPath = blifRealDir + "/out_exam.txt"
                command = "cd " + shellspace(blifRealDir) + "/ && sis -t pla -f script_exam.txt \-x"

                # Checks if FSMD.blif exists
                if os.path.exists(fsmdPath) and os.path.isfile(fsmdPath):
                    with open(scriptPath, "w") as s:
                        s.write(examScriptContent.format(blifRealFilename, inSimPath))

                    subprocess_cmd(command)
                    if os.path.exists(outExamPath) and os.path.isfile(outExamPath):

                        full_output = ""
                        i = 0
                        with open(outExamPath, "r") as infile:
                            for line in infile:
                                # output
                                if pattern.match(line):
                                    bits = line.lstrip('Outputs: ').strip()
                                    if bits.replace(" ", "") == correct_outputs[i]:
                                        full_output += bits + "\n"
                                        match += 1
                                    else:
                                        full_output += bits + " *" + "\n"
                                    i += 1
                                # area
                                elif line.startswith("Total Area"):
                                    area = float(line.split('=', 1)[-1].strip())

                                # slack
                                elif line.startswith("Most Negative Slack"):
                                    slack = float(line.split('-', 1)[-1].strip())

                        # save output
                        with open(studentSimulationPath, "w") as s:
                            s.write(full_output)

                        if match == len(correct_outputs):
                            status = "ok" + filenameCheck + dirCheck
                        else:
                            status = "<a class='warning'> Output did not match </a>"

                    else:
                        status = "<a class='error'>WARNING. An error occurred during the simulation \
                        output generation</a>"
                else:
                    status = "<a class='folder'>WARNING. No FSMD.blif file found</a>"
        correctness = float(match) / len(correct_outputs) * 100.0

        outputList.append([', '.join(studentsList), status, correctness, area, slack])
        idx += 1

    return idx


if __name__ == '__main__':

    """
    ////////////////////////////////////////////////////////////////////////////
    Data Arguments
    ////////////////////////////////////////////////////////////////////////////
    """

    # Initializes an AgumentParser object
    commandLineArguments = argparse.ArgumentParser(description=
                                                   "Analyzer for projects of the Computer Architecture \
                                                   course at University of Verona")

    # Checks each command line argument:
    commandLineArguments.add_argument('-d',
                                      type=str,
                                      required="TRUE",
                                      help="Specify the absolute path of the exams directory")

    commandLineArguments.add_argument('-inp',
                                      type=str,
                                      required="TRUE",
                                      help="Specify the absolute path of the simulation input")

    commandLineArguments.add_argument('-out',
                                      type=str,
                                      required="TRUE",
                                      help="Specify the absolute path of the simulation output")

    # Sets all command line argument into args
    args = commandLineArguments.parse_args()

    """
    ////////////////////////////////////////////////////////////////////////////
    Path verification
    ////////////////////////////////////////////////////////////////////////////
    """

    examsDirPath = args.d.rstrip('/')

    if not os.path.exists(examsDirPath) or not os.path.isdir(examsDirPath):
        print("An error occurred. Please specify the absolute path of the exams directory.\n")
        sys.exit(1)

    inSimPath = args.inp

    if not os.path.exists(inSimPath) or not os.path.isfile(inSimPath):
        print("An error occurred. Please specify the absolute path of the simulation input.\n")
        sys.exit(1)

    outSimPath = args.out

    if not os.path.exists(outSimPath) or not os.path.isfile(outSimPath):
        print("An error occurred. Please specify the absolute path of the simulation output.\n")
        sys.exit(1)

    # Creates a list reporting all simulation outputs used to compare the student simulation output
    correct_outputs = list()
    pattern = re.compile("^(Outputs:\s)?([0-1\s]+)$")

    with open(outSimPath, "r") as infile:
        for line in infile:
            if line and pattern.match(line):
                correct_outputs.append(line.lstrip('Outputs: ').replace(" ", "").strip())

    examScriptContent = """
set sisout out_exam.txt
read_blif {}
source {}
read_library synch.genlib
map -m 0 -W
print_map_stats
quit    
"""
    if os.path.exists('./exams'):
        shutil.rmtree('./exams')
    os.makedirs('./exams')

    resultTarGz = [y for x in os.walk(examsDirPath) for y in
                   glob(os.path.join(x[0], '*.tar.gz'))]
    resultTgz = [y for x in os.walk(examsDirPath) for y in
                 glob(os.path.join(x[0], '*.tgz'))]

    idx = check_students(resultTarGz, "tar.gz", 1)
    check_students(resultTgz, "tgz", idx)

    # sort by status, area and slack
    outputList.sort(key=lambda x:
    (100 - x[2])
    + x[3] / areaExpected * areaWeight
    + x[4] / slackExpected * slackWeight)
    idx = 0
    evaluation = ""
    for s in outputList:
        idx += 1
        evaluation += "<tr><td>%d</td><td>%s</td>" % (idx, s[0])
        evaluation += "<td>%s</td><td>%.1f</td><td>%s</td><td>%s</td></tr>" % (s[1], s[2], s[3], s[4])

    htmlTemplate=open("Template.html","r")
    htmlContent = htmlTemplate.read() % evaluation
    with open('./exam_new.html', "w") as f:
        f.write(htmlContent)
