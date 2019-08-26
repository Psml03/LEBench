# LEBench
set the env var "LEBENCH_DIR" to the directory containing the repo

run "crontab -e" and add the following entries:

PATH=/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin

@reboot python <path>/LEBench/run.py >> <path>/LEBench.out 2>&1

run "python get_kern.py" to generate the kernel list

set the number in "iteration" to "-1"

go to "TEST_DIR" and run "make"

run "python run.py"

results will be saved in .csv files in the LEBench folder
