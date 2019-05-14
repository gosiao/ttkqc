from __future__ import print_function
from paraview.simple import *
import ttk_helper as helper


class ttk_start( object ):

    """
    this class contains methods to generate starting files for TTK;

    on input:
    * csv file with the data from quantum chemistry calculations

    on output:
    * start_data.vti   - data file (resampled)
    * start_state.pvsm - state file

    these two data files can be directly used in TTK:
      paraview start_data.vti
    or
      paraview --state=start_state.pvsm
    """

    def __init__(self, common_options, start_options):
        """
        """
        self.finp          = common_options['finp']
        self.fout_num      = common_options['fout_num']
        self.start_data    = start_options
        self.resampled_dim = [int(x) for x in common_options['resampled_dim'].split(',')]


    def from_csv_to_start_data(self):

        data = []

        for i, inp in enumerate(self.finp):
            # read the data and create a structured grid
            finp_prep = self.start_data[inp]['finp_prep']
            denscsv = CSVReader(FileName=finp_prep)
            npoints = self.start_data[inp]['npoints'].split(',')
            end_x = int(npoints[0]) - 1
            end_y = int(npoints[1]) - 1
            end_z = int(npoints[2]) - 1

            tableToStructuredGrid = TableToStructuredGrid(Input=denscsv)
            tableToStructuredGrid.WholeExtent = [0, end_x, 0, end_y, 0, end_z]
            tableToStructuredGrid.XColumn = 'x'
            tableToStructuredGrid.YColumn = 'y'
            tableToStructuredGrid.ZColumn = 'z'

            data.append(tableToStructuredGrid)

        final_data = AppendAttributes(Input=data)



        finalResampleToImage = ResampleToImage(Input=final_data)
        finalResampleToImage.SamplingDimensions = [self.resampled_dim[0],
                                                   self.resampled_dim[1],
                                                   self.resampled_dim[2]]

        SaveData(self.fout_num, proxy=finalResampleToImage)




    def rename_vars(self, data, old_names, new_names):

        calc = helper.calculator(new_names[0],
                                      old_names[0],
                                      source_other=data)
        if len(old_names) > 1:
            for n in range(1, len(old_names)):
                calc = helper.calculator(new_names[n],
                                              old_names[n],
                                              source_other=calc)
        return calc




