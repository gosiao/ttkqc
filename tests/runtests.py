#!/usr/local/bin/pvpython

from __future__ import print_function
import os
import sys
sys.path.insert(0, os.path.abspath('..'))
import ttkqc.process_input
#from .. import ttkqc
import ttkqc.ttk.ttk_start as ttk0
import ttkqc.ttk.ttk_cps   as ttkcps
import ttkqc.ttk.ttk_multi as ttkmulti


def read_input(finp):
    args = []
    with open(finp, "r") as f:
        for line in f:
            if line[0] != '#' and line != '\n':
                args.append(line.strip())
        return args

##########################################
## tests generating "start data" from TTK:
##########################################
testdirs=["onedim_one_start_from_qc",
          "onedim_one_start_noprep",
          "multidim_many_start_from_qc",
          "multidim_many_start_noprep",
          "multidim_many_start_noprep_rename"]

for d in testdirs:

    print("running test: ", d)
    os.chdir(d)
    inp = "test.inp"
    args=read_input(inp)
    data = ttkqc.process_input.input_data(args)
    data.parse_options()
    data.print_options()
    data.prepare_csvdata_files_for_ttk()

    ttk_data = ttk0.ttk_start(data.options, data.ttk_start_data)
    ttk_data.from_csv_to_start_data()
    os.chdir('../')
    print("-------------------------------------------")

####################################################
## tests - critical points from persistence diagrams
####################################################
testdirs=["onedim_one_ms",
          "onedim_one_calc_ms",
          "multidim_many_calc_ms"]

for d in testdirs:
    print("running test: ", d)
    # we assume that start_data.vti is in the directory
    os.chdir(d)
    inp = "test.inp"
    args=read_input(inp)
    data = ttkqc.process_input.input_data(args)
    data.parse_options()
    data.print_options()

    ttk_data = ttkcps.ttk_cps(data.options, data.ttk_scalar_data)
    ttk_data.get_cps(save_cps_to_file=True)
    os.chdir('../')
    print("-------------------------------------------")

#
#
#
#testdirs=["multidim_many_calc_bottleneck"]
#
#for d in testdirs:
#    print("running test: ", d)
#    # we assume that start_data.vti is in the directory
#    os.chdir(d)
#    inp = "test.inp"
#    args=read_input(inp)
#    data = ttkqc.process_input.input_data(args)
#    data.parse_options()
#    data.print_options()
#
#    fulloptions = data.options
#    #
#    #
#    ttk_btln = ttkmulti.ttk_multi(data.options, data.ttk_multi_data)
#    ttk_btln.bottleneck_distance()
#    os.chdir('../')
#    print("-------------------------------------------")

# tests new
testdirs=["multidim_many_calc_ms_real"]

for d in testdirs:
    print("running test: ", d)
    # we assume that start_data.vti is in the directory
    os.chdir(d)
    inp = "test.inp"
    args=read_input(inp)
    data = ttkqc.process_input.input_data(args)
    data.parse_options()
    data.print_options()

    ttk_data = ttkcps.ttk_cps(data.options, data.ttk_scalar_data)
    ttk_data.get_cps(save_cps_to_file=True)
    os.chdir('../')
    print("-------------------------------------------")


