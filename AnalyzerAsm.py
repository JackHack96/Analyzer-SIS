"""@package Analyzer
Functions for X86 assembly
"""

from subprocess import Popen, PIPE, STDOUT, TimeoutExpired
import time
import os
import tarfile

__NR_FILE_NOT_FOUND = -1
__NR_TIMEOUT = -2
__NR_MEMORY_OUT = -3
__NR_MAX_STDOUT_EXCEEDED = -4


def extract_archive(asm_tarball):
    """
    Extract archive in a sub-directory
    :param asm_tarball: The tarball file path
    :return: Extract directory path
    """
    asm_tar_directory = asm_tarball.split('.')[0]
    if not os.path.exists(asm_tar_directory):
        os.makedirs(asm_tar_directory)
    with tarfile.open(asm_tarball, "r") as tar:
        tar.extractall(path=asm_tar_directory)
        tar.close()
    return asm_tar_directory


def limit_memory(memory):
    """
    Set the maximum usable limit for a process
    :param memory: Maximum memory amount
    :return: setrlimit lambda expression result
    """
    import resource
    return lambda: resource.setrlimit(resource.RLIMIT_AS, (memory, memory))


def run_program(cmd, timeout, memory):
    """
    Run the command line and output (ret, sout, serr)
    :param cmd: Command to be executed in background
    :param timeout: Maximum time allowed
    :param memory: Maximum memory allowed
    :return: Return code of the subprocess
    """
    try:
        proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
                     preexec_fn=limit_memory(memory), timeout=timeout)
    except FileNotFoundError:
        return __NR_FILE_NOT_FOUND, "", ""
    start_time = time.time()  # store a reference timer
    try:
        while True:  # our main listener loop
            # line = proc.stdout.readline()  # read a line from the STDOUT
            if proc.poll() is not None:  # process finished, nothing to do
                break
            # finally, check the current time progress...
            if time.time() >= start_time + timeout:
                raise TimeoutExpired(proc.args, timeout)
        ret = proc.poll()  # get the return code
    except TimeoutExpired:
        proc.kill()  # we're no longer interested in the process, kill it
        ret = __NR_TIMEOUT
    except MemoryError:
        ret = __NR_MEMORY_OUT
    except ValueError:  # max buffer reached
        proc.kill()  # we're no longer interested in the process, kill it
        ret = __NR_MAX_STDOUT_EXCEEDED
    return ret
