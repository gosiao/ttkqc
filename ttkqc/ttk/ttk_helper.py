from __future__ import print_function
from paraview.simple import *
import os
#import pandas as pd   # to do: fix import pandas
import csv


def set_pipeline(calc=None, grad=None):
    """
    get the order of calculator, gradient and threshold filters in the correct order
    """
    print('calc = ', calc)
    print('grad = ', grad)
    pipeline = {}
    if calc is not None:
        for c in calc:
            k_calc = c.strip().split(':')[0]
            v_calc = c.strip().split(':')[1]
            n_calc = c.strip().split(':')[2]
            #print('k, v, n = ', k_calc, v_calc, n_calc)
            pipeline[int(k_calc)] = ['calc', v_calc, n_calc]
    if grad is not None:
        for g in grad:
            k_grad = g.strip().split(':')[0]
            v_grad = g.strip().split(':')[1]
            n_grad = g.strip().split(':')[2]
            #print('k, v, n = ', k_grad, v_grad, n_grad)
            pipeline[int(k_grad)] = ['grad', v_grad, n_grad]
    #for k in sorted(pipeline):
    #    print('k = ', k, pipeline[k])
    return pipeline


def get_value_in_point(data, varname, point_x, point_y, point_z):

    """
    not tested!!
    """

    probe_location = ProbeLocation(Input=data,
                                   ProbeType='Fixed Radius Point Source')

    probe_location.ProbeType.Center = [point_x, point_y, point_z]

    probe.UpdatePipeline()
    probePoint = paraview.servermanager.Fetch(probe)
    value_at_probe = probePoint.GetPointData().GetArray(varname).GetValue(0)

    return value_at_probe



def apply_threshold(source, source_type, source_name, min_value, max_value):
    """
    source      = input TTK object
    source_type = 'POINTS' or 'CELLS'
    source_name = string, depends on the "source"
    min_value, max_value = range of data
    """

    threshold = Threshold(Input=source)
    threshold.Scalars = [source_type, source_name]
    threshold.ThresholdRange = [min_value, max_value]

    return threshold

def apply_gradientOfUnstructuredDataSet(source, source_type, source_name, result_name):
    """
    source      = input TTK object
    source_type = 'POINTS' or 'CELLS'
    source_name = string, depends on the "source"
    result_name = name of the calculated gradient
    """

    gradient = GradientOfUnstructuredDataSet(Input=source)
    gradient.ScalarArray = [source_type, source_name]
    gradient.ResultArrayName = result_name

    return gradient


def calculator(name, function, source_file=None, source_other=None):

    if source_file is not None:
        inpdata = XMLImageDataReader(FileName=source_file)
    elif source_other is not None:
        inpdata = source_other

    calculator = Calculator(Input=inpdata)

    calculator.ResultArrayName = name
    calculator.Function = function

    debug = False
    if debug:
        print('output from ttk_helper.calculator: source_file=  ', source_file)
        print('output from ttk_helper.calculator: source_other= ', source_other)
        print('output from ttk_helper.calculator: name=         ', name)
        print('output from ttk_helper.calculator: function=     ', function)

    return calculator



def save_num_data(out_file, out_data, out_type=None, precision=6, sci_notation=1):

    if out_type is not None:
        SaveData(out_file,
                 proxy=out_data,
                 Precision=precision,
                 UseScientificNotation=sci_notation,
                 FieldAssociation=out_type)
    else:
        # the default in TTK is 'Points'
        SaveData(out_file,
                 proxy=out_data,
                 Precision=precision,
                 UseScientificNotation=sci_notation)



def save_data(data_type, data_object, file_out, postprocess=None):

#  save numerical data:
    if postprocess is not None:
        all_outputs = {}

    if data_type == 'full' or data_type == 'point_data':
        if data_type == 'full':
            p, n = os.path.split(file_out)
            fout = os.path.join(p, "point_data_"+n)
        else:
            fout = file_out

        save_num_data(fout, data_object)

        if postprocess is not None:
            all_outputs['point_data'] = fout

    if data_type == 'full' or data_type == 'cell_data':
        if data_type == 'full':
            p, n = os.path.split(file_out)
            fout = os.path.join(p, "cell_data_"+n)
        else:
            fout = file_out

        save_num_data(fout, data_object, out_type='Cells')

        if postprocess is not None:
            all_outputs['cell_data'] = fout


    if data_type == 'full' or data_type == 'field_data':
        if data_type == 'full':
            p, n = os.path.split(file_out)
            fout = os.path.join(p, "field_data_"+n)
        else:
            fout = file_out

        save_num_data(fout, data_object, out_type='Field Data')

        if postprocess is not None:
            all_outputs['field_data'] = fout

    if postprocess is not None:
        postprocess_num_data(postprocess, all_outputs)

#  save screenshots:



def postprocess_num_data(scope, outputs):

    if 'cps_sort_by_pairs' in scope:
        try:
            with open(outputs['point_data'], 'r') as f_points:
                # read all points
                #point_data = pd.read_csv(f_points, sep=',', index_col=False)
                point_data = csv.DictReader(f_points, delimiter=',')
                list_point_data = []
                for row in point_data:
                    list_point_data.append(row)
        except IOError:
            print('error with outputs["point_data"]')

        try:
            with open(outputs['cell_data'], 'r') as f_cells:
                cell_data = csv.DictReader(f_cells, delimiter=',')
                list_cell_data = []
                for row in cell_data:
                    list_cell_data.append(row)
        except IOError:
            print('error with outputs["cell_data"]')

        combined_data = []
        if len(list_point_data) == 2*len(list_cell_data):
            keys = 'PairIdentifier,PairType,Persistence,cp1_x,cp1_y,cp1_z,cp1_birth,cp1_death,cp2_x,cp2_y,cp2_z,cp2_birth,cp2_death'.split(',')
            fout = 'cps_summary.csv'
            fout_type_m1 = 'cps_summary_pairtype_m1.csv'
            fout_type_0  = 'cps_summary_pairtype_0.csv'
            fout_type_1  = 'cps_summary_pairtype_1.csv'
            fout_type_2  = 'cps_summary_pairtype_2.csv'
            with open(fout, 'w') as f:
                f.write(','.join(keys)+'\n')
            with open(fout_type_m1, 'w') as f:
                f.write(','.join(keys)+'\n')
            with open(fout_type_0, 'w') as f:
                f.write(','.join(keys)+'\n')
            with open(fout_type_1, 'w') as f:
                f.write(','.join(keys)+'\n')
            with open(fout_type_2, 'w') as f:
                f.write(','.join(keys)+'\n')
            for i, row in enumerate(list_cell_data):
                data = {}
                data["PairIdentifier"] = list_cell_data[i]["PairIdentifier"]
                data["PairType"]       = list_cell_data[i]["PairType"]
                data["Persistence"]    = list_cell_data[i]["Persistence"]

                data["cp1_x"]          = list_point_data[2*i]["Points:0"]
                data["cp1_y"]          = list_point_data[2*i]["Points:1"]
                data["cp1_z"]          = list_point_data[2*i]["Points:2"]
                data["cp1_birth"]      = list_point_data[2*i]["Birth"]
                data["cp1_death"]      = list_point_data[2*i]["Death"]

                data["cp2_x"]          = list_point_data[2*i+1]["Points:0"]
                data["cp2_y"]          = list_point_data[2*i+1]["Points:1"]
                data["cp2_z"]          = list_point_data[2*i+1]["Points:2"]
                data["cp2_birth"]      = list_point_data[2*i+1]["Birth"]
                data["cp2_death"]      = list_point_data[2*i+1]["Death"]

                combined_data.append(data)
                with open(fout, 'a') as f:
                    sorted_data = ','.join(data[k] for k in keys)
                    f.write(sorted_data+'\n')
                if data["PairType"] == '-1':
                    with open(fout_type_m1, 'a') as f:
                        sorted_data = ','.join(data[k] for k in keys)
                        f.write(sorted_data+'\n')
                elif data["PairType"] == '0':
                    with open(fout_type_0, 'a') as f:
                        sorted_data = ','.join(data[k] for k in keys)
                        f.write(sorted_data+'\n')
                elif data["PairType"] == '1':
                    with open(fout_type_1, 'a') as f:
                        sorted_data = ','.join(data[k] for k in keys)
                        f.write(sorted_data+'\n')
                elif data["PairType"] == '2':
                    with open(fout_type_2, 'a') as f:
                        sorted_data = ','.join(data[k] for k in keys)
                        f.write(sorted_data+'\n')


        else:
            print('error1')




def resample(data, resampled_dim=[256,256,256]):

    print('resampleToImage filter applied; sampling dimensions: ', resampled_dim)

    resampleToImage = ResampleToImage(Input=data)

    resampleToImage.SamplingDimensions = [resampled_dim[0],
                                          resampled_dim[1],
                                          resampled_dim[2]]




