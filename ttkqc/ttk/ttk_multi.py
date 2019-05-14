from __future__ import print_function
import os
from paraview.simple import *
#from ttk_helper import ttk_helper
import ttk_helper as helper
from ttk_cps import ttk_cps

class ttk_multi( object ):

    """
    write me
    """

    def __init__(self, common_options, multi_options):
        """
        """

        # common options
        self.finp          = common_options['finp']
        self.fout_num      = common_options['fout_num']
        self.fout_num_scope= common_options['fout_num_scope']
        self.calc_fun      = common_options['calc_fun']
        self.calc_name     = common_options['calc_name']

        self.resampled_dim = [int(x) for x in common_options['resampled_dim'].split(',')]

        # data specific to calculations of critical points:
        #self.ttk_cps       = ttk_cps(common_options, multi_options) # redo
        self.ttk_cps       = ttk_cps(common_options, multi_options) # redo

        # data specific to multivariate runs
        self.multi_data    = multi_options



    def from_start_data_to_bottleneck_distance_between_two(self, tTKPersistenceDiagram1, tTKPersistenceDiagram2):

        tTKBottleneckDistance = TTKBottleneckDistance(Persistencediagram1=tTKPersistenceDiagram1,
                                                      Persistencediagram2=tTKPersistenceDiagram2)

        #self.helper.save_data(OutputPort(tTKBottleneckDistance, 2))
        helper.save_data(self.fout_num_scope,
                          tTKBottleneckDistance,
                          self.fout_num)

        ## set active source
        #SetActiveSource(tTKBottleneckDistance)
        #SaveData('/home/gosia/devel/ttkqc/tests/multidim_many_calc_bottleneck/btln_test.csv', proxy=OutputPort(tTKBottleneckDistance, 2), Precision=6,
        #         UseScientificNotation=1,
        #         FieldAssociation='Cells')


    def from_start_data_to_bottleneck_distance_between_many(self, tTKPersistenceDiagrams_list):
        """
        test
        """

        pass


    def bottleneck_distance(self):

        ttk_persistence_diagrams = []

        for data in self.multi_data['choose_data']:
            print('btl data = ', data)
            diag = self.ttk_cps.get_cps(save_cps_to_file=False, selected_data=data)
            ttk_persistence_diagrams.append(diag)

        if len(ttk_persistence_diagrams) == 2:
            self.from_start_data_to_bottleneck_distance_between_two(ttk_persistence_diagrams[0], ttk_persistence_diagrams[1])


