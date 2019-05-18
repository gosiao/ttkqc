from __future__ import print_function
import os
from paraview.simple import *
import ttk_helper as helper


class ttk_cps( object ):

    """
    this class contains methods to generate starting files for TTK;

    on input:
    * start_data.vti

    on output:
    * num data: 
    * vis data:

    """



    def __init__(self, common_options, scalar_options):

        # common options
        self.finp          = common_options['finp']
        self.fout_num      = common_options['fout_num']
        self.fout_num_scope= common_options['fout_num_scope']
        self.calc_fun      = common_options['calc_fun']
        self.calc_gradient          = common_options['calc_gradient']

        self.resampled_dim = [int(x) for x in common_options['resampled_dim'].split(',')]

        # data specific to calculations of critical points:
        self.cps_data      = scalar_options




    def calculate_or_get_data(self):
        """
        called from from_start_data_to_cps, but can be used in the beginnig of every TTK pipeline

        allows to get the data either from file or from calculator filter;
        in the latter case - it is important to start with the FIRST calculator (first in the input),
        as we allow workflows with more than one calculator filter applied
        """

        data = XMLImageDataReader(FileName=self.finp)
        #print('hello calculate_or_get_data')
        #if self.calc_fun[0] is not None:
        #    data = helper.calculator(self.calc_name[0],
        #                             self.calc_fun[0],
        #                             source_file=self.finp)
        #else:
        #    data = XMLImageDataReader(FileName=self.finp)

        return data




    def persistence_diag_on_selected_data(self, data, data_name):

        tTKPersistenceDiagram = TTKPersistenceDiagram(Input=data)

        tTKPersistenceDiagram.ScalarField                  = data_name
        tTKPersistenceDiagram.InputOffsetField             = data_name
        tTKPersistenceDiagram.ComputesaddlesaddlepairsSLOW = 1
        tTKPersistenceDiagram.EmbedinDomain                = 1

        return tTKPersistenceDiagram



    def from_start_data_to_cps(self, selected_data, pipeline, save_to_file=False):

        start_data = self.calculate_or_get_data()

        if pipeline is not None:
            for k in sorted(pipeline):
                t=pipeline[k][0]  # type: 'calc' or 'grad'
                w=pipeline[k][1]  # what
                n=pipeline[k][2]  # name

                if t == 'calc':
                    data = helper.calculator(n, w, source_other=start_data)
                elif t == 'grad':
                    #data = helper.apply_gradientOfUnstructuredDataSet(self.finp, 'POINTS', w, n)
                    data = helper.apply_gradientOfUnstructuredDataSet(start_data, 'POINTS', w, n)
                start_data = data

        #if self.calc_fun[0] is not None and len(self.calc_fun) > 1:
        #    for i in range(1, len(self.calc_fun)):
        #        data = helper.calculator(self.calc_name[i],
        #                                 self.calc_fun[i],
        #                                 source_other=start_data)
        #        start_data = data

        #elif self.calc_gradient[0] is not None:
        #    data = helper.apply_gradientOfUnstructuredDataSet(self.finp,
        #                                                      'POINTS',
        #                                                      self.calc_gradient[0],
        #                                                      self.calc_gradient_name[0])
        #    start_data = data


        test_resample_again = False
        if test_resample_again:
            helper.resample(start_data, [self.resampled_dim[0],
                                         self.resampled_dim[1],
                                         self.resampled_dim[2]])

        tTKPointDataSelector  = TTKPointDataSelector(Input=start_data)
        tTKPointDataSelector.ScalarFields = selected_data

        tTKPersistenceDiagram = self.persistence_diag_on_selected_data(tTKPointDataSelector, selected_data)

        # save data
        if save_to_file:
            if self.cps_data['fout_num_postprocess'] is not None:
                print('BUBA postprocessing!')
                helper.save_data(self.fout_num_scope,
                                 tTKPersistenceDiagram,
                                 self.fout_num,
                                 postprocess=self.cps_data['fout_num_postprocess'])

            else:
                helper.save_data(self.fout_num_scope,
                                 tTKPersistenceDiagram,
                                 self.fout_num)


        return tTKPersistenceDiagram


    def get_cps(self, save_cps_to_file=False, selected_data=None):

        pipeline = helper.set_pipeline(calc=self.calc_fun, grad=self.calc_gradient)

        if selected_data is not None:
            tTKPersistenceDiagram = self.from_start_data_to_cps(selected_data, pipeline, save_to_file=save_cps_to_file)
        else:
            tTKPersistenceDiagram = self.from_start_data_to_cps(self.cps_data['choose_data'], pipeline, save_to_file=save_cps_to_file)

        return tTKPersistenceDiagram


#    def get_selected_cp_pair(self, save_cps_to_file=False, selected_data=None, pair_number=None):
#
#        pipeline = helper.set_pipeline(calc=self.calc_fun, grad=self.calc_gradient)
#
#        if selected_data is not None:
#            tTKPersistenceDiagram = self.from_start_data_to_cps(selected_data, pipeline, save_to_file=save_cps_to_file)
#        else:
#            tTKPersistenceDiagram = self.from_start_data_to_cps(self.cps_data['choose_data'], pipeline, save_to_file=save_cps_to_file)
#
#        # fixme! hardcoded
#        pair_number = 10
#        selected_pair = helper.apply_threshold(tTKPersistenceDiagram,
#                                               'CELLS', 'PairIdentifier',
#                                               pair_number, pair_number)
#
#        # to do: add other thresholds (e.g. persistence)
#
#        return tTKPersistenceDiagram



    def from_start_data_to_start_state(self):
        """
        also save state... to do
        """
        return


