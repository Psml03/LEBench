#!/usr/bin/env python
import os
import platform
import sys
from subprocess import call
from os.path import join
from datetime import datetime

DEBUG = True

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

# Define the CPU affinity range
CPU_AFFINITY = "6-11,30-35"

def run_bench():
    print('[INFO] --------------------------------------------------')
    print('[INFO]              Starting LEBench tests')
    print('[INFO]              Current time: ' + str(datetime.now().time()))

    kern_version = platform.uname()[2]
    print('[INFO] current kernel version: ' + kern_version + '.')

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
    
    # Set CPU affinity for the OS_Eval test process only
    print(f'[INFO] Setting CPU affinity to {CPU_AFFINITY} for the test process.')
    ret = call(f"taskset -c {CPU_AFFINITY} {' '.join(test_cmd)}", stdout=result_fp, stderr=result_error_fp)

    print('[INFO]              Finished running test ' + TEST_NAME + \
          ', test returned ' + str(ret) + ', log written to: ' + result_path + ".")
    print('[INFO]              Current time: ' + str(datetime.now().time()))

    with open(result_error_filename, 'r') as fp:
        lines = fp.readlines()
        if len(lines) > 0:
            for line in lines:
                print(line)
            raise Exception('[FATAL] test run encountered error.')

if __name__ == '__main__':
    # Setting up working directory and sanity checks.
    if not os.geteuid() == 0:
        raise Exception('This script should be run with "sudo".')

    # Directly run the benchmark without modifying GRUB
    print("[INFO] Running benchmark on the current kernel version.")
    run_bench()
