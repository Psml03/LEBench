#!/usr/bin/env python
import os
import platform
import sys
from subprocess import call, run, Popen
from os.path import join
from datetime import datetime
import time
import signal


# Set the working directory
WORKING_DIR = '/mnt/purnya/benchmark/LEBench'
KERN_INDEX_FILE = WORKING_DIR + '/iteration' 
LOCAL_GRUB_FILE = WORKING_DIR + '/grub'  
KERN_LIST_FILE = WORKING_DIR + '/kern_list'  
RESULT_DIR = WORKING_DIR + '/RESULT_DIR/'  
TEST_DIR = WORKING_DIR + '/TEST_DIR/'  
TEST_NAME = 'OS_Eval'

# Set temporary
os.environ['LEBENCH_DIR'] = WORKING_DIR 

""" Running the LEBench tests for the current kernel version.
"""
def run_bench():
    print('[INFO] --------------------------------------------------')
    print('[INFO]              Starting LEBench tests')
    print('[INFO]              Current time: ' + str(datetime.now().time()))

    kern_version = platform.uname()[2]
    print('[INFO] Current kernel version: ' + kern_version + '.')

    test_file = join(TEST_DIR, TEST_NAME)
    print('[INFO] Preparing to run test ' + TEST_NAME + '.')

    print('[INFO] Compiling test ' + TEST_NAME + ".c.")
    call(('make -C ' + TEST_DIR).split())

    result_path = join(RESULT_DIR, kern_version)
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    result_filename = join(RESULT_DIR, kern_version, TEST_NAME)
    result_error_filename = join(RESULT_DIR, kern_version, TEST_NAME + '_err')

    result_fp = open(result_filename, 'w+')
    result_error_fp = open(result_error_filename, 'w+')
    test_cmd = [TEST_DIR + TEST_NAME, '0', kern_version]
    print('[INFO] Running test with command: ' + ' '.join(test_cmd))
    ret = call(test_cmd, stdout=result_fp, stderr=result_error_fp)

    print('[INFO] Finished running test ' + TEST_NAME + \
          ', test returned ' + str(ret) + ', log written to: ' + result_path + ".")
    print('[INFO] Current time: ' + str(datetime.now().time()))

    with open(result_error_filename, 'r') as fp:
        lines = fp.readlines()
        if len(lines) > 0:
            for line in lines:
                print(line)
            raise Exception('[FATAL] Test run encountered error.')

if __name__ == '__main__':
    # Ensure the script runs with sudo
    if not os.geteuid() == 0:
        raise Exception('This script should be run with "sudo".')

    # Start `perf stat` in the background
    print("[INFO] Starting perf stat...")
    perf_process = Popen(
        ["sudo", "perf", "stat", "-e", "cycles,instructions"], 
        stdout=open("/mnt/purnya/benchmark/Perf/perf_stat_output.txt", "w"), 
        stderr=open("/mnt/purnya/benchmark/Perf/perf_stat_error.txt", "w")
    )

    try:
        # Run the benchmark
        print("[INFO] Running benchmark on the current kernel version.")
        run_bench()
    finally:
        # Kill the `perf stat` process after the benchmark completes
        print("[INFO] Stopping perf stat...")
        perf_process.send_signal(signal.SIGINT)
        perf_process.wait()
