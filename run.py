#!/usr/bin/env python
import os
import signal
import platform
import sys
from subprocess import check_call, check_output, call
from os.path import join
from datetime import datetime

DEBUG = True

GRUB_CFG_FILE = '/boot/grub/grub.cfg'
GRUB_FILE = '/etc/default/grub' 

WORKING_DIR = '/home/purnya/benchmark/LEBench/'
KERN_INDEX_FILE = '/iteration' 
LOCAL_GRUB_FILE = '/grub'
KERN_LIST_FILE = '/kern_list' 
RESULT_DIR = '/RESULT_DIR/'
TEST_DIR = '/TEST_DIR/'
TEST_NAME = 'OS_Eval'

""" Set temporary
"""
os.environ['LEBENCH_DIR'] = '/home/purnya/benchmark/LEBench'

#... (rest of your code remains unchanged)

if __name__ == '__main__':
    # Setting up working directory and sanity checks.
    if not os.geteuid() == 0:
        raise Exception('This script should be run with "sudo".')

    try:
        WORKING_DIR = os.environ['LEBENCH_DIR']
    except:
        raise ValueError('$LEBENCH_DIR is not set. Example: "/home/username/LEBench/".')

    if 'LEBench' not in WORKING_DIR:
        raise ValueError('$LEBENCH_DIR should point to the directory containing LEBench. Example: "/home/username/LEBench/".')

    KERN_INDEX_FILE = WORKING_DIR + KERN_INDEX_FILE
    LOCAL_GRUB_FILE = WORKING_DIR + LOCAL_GRUB_FILE
    KERN_LIST_FILE = WORKING_DIR + KERN_LIST_FILE
    RESULT_DIR = WORKING_DIR + RESULT_DIR
    TEST_DIR = WORKING_DIR + TEST_DIR

    if not os.path.exists(KERN_LIST_FILE):
        raise IOError('Cannot open "kern_list" file. If it\'s not present, '
                      'run "get_kern.py" to generate this file by grepping all install kernels.')

    with open(KERN_LIST_FILE, 'r') as fp:
        lines = fp.readlines()
        if len(lines) == 0:
            raise ValueError('"kern_list" file is empty, '
                             'run "get_kern.py" to generate this file by grepping all install kernels.')

    # For running LEBench on one specified kernel version.
    if len(sys.argv) > 1:
        kern_version = sys.argv[1]
        print("[INFO] Configuring to boot into " + kern_version + ".")
        generate_grub_file(os.path.join(WORKING_DIR, 'template/grub'), get_kern_list(next_kern_idx))
        install_grub_file()
        sys.exit(0)

    # For running LEBench on a list of specified kernel versions.
    if not os.path.exists(KERN_INDEX_FILE):
        with open(KERN_INDEX_FILE, 'w') as f:
            f.write("-1\n")

    with open(KERN_INDEX_FILE, 'r') as f:
        kern_idx = int(f.read())
    next_kern_idx = kern_idx + 1
    if DEBUG: print('[DEBUG] Running at kernel index: ' + str(kern_idx))
    
    with open(KERN_INDEX_FILE, 'w') as fp:
        fp.write(str(next_kern_idx).strip())

    if DEBUG: print('[DEBUG] Done writing kernel index %d for the next iteration' % next_kern_idx + '.')

    if next_kern_idx == 0:
        # Need to boot into the right kernel version first.
        print('[INFO] LEBench tests will start after booting into the first kernel.')
    else:
        # We are at the right kernel version, actually run LEBench.
        run_bench()

    if DEBUG: print('[DEBUG] Preparing to modify grub.')
    if generate_grub_file(os.path.join(WORKING_DIR, 'template/grub'), get_kern_list(next_kern_idx)):
        install_grub_file()
        if DEBUG: print('[DEBUG] Done configuring grub for the next kernel.')
        restart()
