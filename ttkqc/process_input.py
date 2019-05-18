from __future__ import print_function
import os
import sys
import numpy
import shutil
import fileinput
import argparse


def ensure_prep(func):
    """
    decorator to ensure that the data files are to be formatted to the TTK-convenient format
    """
    def _wrapper(self, *args, **kwargs):
        if self.options['noprep']:
            return True
        else:
            return False
    return _wrapper




class input_data:

    def __init__(self, args_list=None):

        """
        initialize a class for handling input options
        these options can be read from file or from the command line,
        that's why "args_list" is a list of options and not a script file
        """

        self.args_list       = args_list if args_list is not None else sys.argv[1:]
        self.options         = {}
        self.nr_inp_blocks   = 0
        self.ttk_start_data  = {}
        self.ttk_scalar_data = {}
        self.ttk_multi_data  = {}
        self.ttk_postprocess = {}



    def parse_options(self):

        #parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
        parser = argparse.ArgumentParser()

        # define mandatory arguments:
        required_args = parser.add_argument_group('required arguments')

        required_args.add_argument('--ttk_task',
                                   dest='ttk_task',
                                   action='store',
                                   required=True,
                                   choices=['start', 'ms', 'scatterplot', 'bottleneck', 'jacobi'],
                                   help='which TTK task will be performed')

        required_args.add_argument('--finp',
                                   dest='finp',
                                   action='append',
                                   metavar='FILE',
                                   required=True,
                                   help='''
                                        input file(s) for TTK (can be more than one, see test examples);
                                        one file per one "--finp" (sets one input block)
                                        ''')

        # define optional arguments, common for all ttk tasks:
        optional_args = parser.add_argument_group('optional arguments')

        optional_args.add_argument('--fout_num',
                                   dest='fout_num',
                                   action='store',
                                   metavar='FILE',
                                   required=False,
                                   help='''
                                        name of output file with the numerical data from TTK;
                                        if more than one output can be generated, this name is used as a suffix, see test examples
                                        ''')

        optional_args.add_argument('--fout_vis',
                                   dest='fout_vis',
                                   action='append',
                                   metavar='FILE',
                                   required=False,
                                   help='output file(s) with the visual data from TTK (state files)')

        optional_args.add_argument('--fout_num_scope',
                                   dest='fout_num_scope',
                                   action='store',
                                   required=False,
                                   choices=['full','point_data','cell_data','field_data'],
                                   help='type of numerical data expected from TTK ("full" exports all available data)')

        optional_args.add_argument('--resampled_dim',
                                   dest='resampled_dim',
                                   action='store',
                                   required=False,
                                   help='''
                                        number of points in x,y,z directions for the "ResampleToImage" filter in TTK;
                                        default: 256x256x256
                                        ''')

        optional_args.add_argument('--calc_fun',
                                   dest='calc_fun',
                                   action='append',
                                   required=False,
                                   help='function to apply in the Calculator filter')

        optional_args.add_argument('--calc_gradient',
                                   dest='calc_gradient',
                                   action='append',
                                   required=False,
                                   help='apply the gradientOfUnstructuredDataSet filter')

        optional_args.add_argument('--choose_data',
                                   dest='choose_data',
                                   #action='append',
                                   action='store',
                                   nargs='*',
                                   required=False,
                                   help='''
                                        it gives the possibility to choose the data to proceed with;
                                        mandatory for selected ttk tasks (see examples)
                                        ''')

        optional_args.add_argument('--fout_num_postprocess',
                                   dest='fout_num_postprocess',
                                   action='append',
                                   #action='store',
                                   #nargs='*',
                                   choices=['cps_summary', 'cps_sort_by_pairs'],
                                   required=False,
                                   help='''
                                        postprocess the data
                                        ''')



        # other arguments depend on the ttk_task:
        ttk_start_args = parser.add_argument_group('arguments if ttk_task=="start"')

        # mandatory:
        ttk_start_args.add_argument('--prep',
                                    dest='prep',
                                    #action='append_const',
                                    #const=True,
                                    action='append',
                                    type=self.str2bool,
                                    required=False,
                                    help='preprocess finp (if finp already has the correct format for TTK, use --prep=False)')


        # optional:
        ttk_start_args.add_argument('--finp_prep',
                                    dest='finp_prep',
                                    action='append',
                                    metavar='FILE',
                                    required=False,
                                    help='''
                                         file(s) to which the input data in the TTK-convenient format is written;
                                         default: formatted_[finp] in the same directory;
                                         can be suppressed with the "--prep=False" keyword
                                         ''')

        ttk_start_args.add_argument('--sep',
                                    dest='sep',
                                    action='append',
                                    required=False,
                                    #default=',',
                                    type=str,
                                    help='column separator on input files (makes sense only if --prep=True)')


        ttk_start_args.add_argument('--varnames',
                                    dest='varnames',
                                    action='append',
                                    #nargs='*',
                                    required=False,
                                    help='''
                                         column names for data columns in the input file(s) file from qchem calculations 
                                         (grid's x, y, z coordinates are expected as 3 first columns and should not be given here);
                                         makes sense only if --prep=True
                                         ''')

        ttk_start_args.add_argument('--varnames_rename',
                                    dest='varnames_rename',
                                    action='append',
                                    #nargs='*',
                                    required=False,
                                    help='rename variables on formatted files (makes sense only if --prep=False)')

        ttk_start_args.add_argument('--nr_header_lines',
                                    dest='nr_header_lines',
                                    action='append',
                                    required=False,
                                    type=int,
                                    help='number of header lines on input file (lines to skip); makes sense only if --prep=True')

        ttk_start_args.add_argument('--npoints',
                                    dest='npoints',
                                    action='append',
                                    #nargs='*',
                                    required=False,
                                    help='''
                                         number of points in x,y,z directions on input file(s) from qchem calculations;
                                         (should be separated by a coma)
                                         ''')



        # parse all arguments and assign
        args = parser.parse_args(self.args_list)

        if args.ttk_task is not None:
            self.options["ttk_task"] = args.ttk_task
        else:
            parser.error('--ttk_task is required')

        if args.finp is not None:
            self.options["finp"] = args.finp
            self.nr_inp_blocks   = len(args.finp)
        else:
            parser.error('--finp is required')



        if args.fout_num is not None:
            self.options["fout_num"] = args.fout_num

        if args.fout_num_scope is not None:
            self.options["fout_num_scope"] = args.fout_num_scope

        if args.fout_vis is not None:
            self.options["fout_vis"] = args.fout_vis


        if args.resampled_dim is not None:
            self.options["resampled_dim"] = args.resampled_dim
        else:
            self.options["resampled_dim"] = '256,256,256'


        if args.calc_fun is not None:
            self.options["calc_fun"] = args.calc_fun
        else:
            self.options["calc_fun"]  = [None for x in range(self.nr_inp_blocks)]

        if args.calc_gradient is not None:
            self.options["calc_gradient"] = args.calc_gradient
        else:
            #self.options["calc_gradient"]  = [None for x in range(self.nr_inp_blocks)]
            self.options["calc_gradient"]  = None


        # to do - choose_data

        if args.fout_num_postprocess is not None:
            self.options["fout_num_postprocess"] = args.fout_num_postprocess
        else:
            self.options["fout_num_postprocess"] = None


        if (self.options['ttk_task'] == 'start'):
            # generate (resampled) start data in vti format for TTK
            # todo: check input format!

            d = {}

            # set to None if absent (optional keywords)
            args.prep            = self.test_start_option(args.prep)
            args.finp_prep       = self.test_start_option(args.finp_prep)
            args.varnames        = self.test_start_option(args.varnames)
            args.varnames_rename = self.test_start_option(args.varnames_rename)


            for i in range(self.nr_inp_blocks):

                f = self.options["finp"][i]
                d[f] = {}

                if args.prep[i] is not None:
                    d[f]['prep'] = args.prep[i]

                    # number of points in x/y/z directions:
                    if args.npoints[i] is not None:
                        d[f]['npoints'] = args.npoints[i]
                    else:
                        parser.error('if "ttk_task=start", then --npoints is required')


                    if args.prep[i]:
                        # prepare data for TTK:

                        # name of prepared files:
                        if args.finp_prep[i] is not None:
                            d[f]["finp_prep"] = self.set_finp_prep(finp_prep=args.finp_prep[i])
                        else:
                            d[f]["finp_prep"] = self.set_finp_prep(finp=f)

                        # names of variables:
                        if args.varnames[i] is not None:
                            d[f]['varnames'] = args.varnames[i]
                        else:
                            parser.error('if "ttk_task=start" and --prep=True, then --varnames is required')
                        # set rename option (None)
                        d[f]['varnames_rename'] = args.varnames_rename[i]
                        # number of header lines:
                        if args.nr_header_lines[i] is not None:
                            d[f]['nr_header_lines'] = args.nr_header_lines[i]
                        else:
                            parser.error('if "ttk_task=start" and --prep=True, then --nr_header_lines is required')
                        # column separator:
                        if args.sep[i] is not None:
                            d[f]['sep'] = args.sep[i]
                        else:
                            d[f]['sep'] = None

                    else:
                        # skip the preprocessing step
                        d[f]["finp_prep"] = os.path.abspath(f)
                        # you may want to rename variables

                        d[f]['varnames_rename'] = args.varnames_rename[i]
                        d[f]['varnames'] = self.varnames_rename(args.varnames_rename[i], d[f]['finp_prep'])

                else:
                    parser.error('if "ttk_task=start" then --prep=True/False is mandatory')


            self.ttk_start_data = d


        else:
            # for every ttk task finp should be a "start" vti file
            # to do - check that!

            # the input should be a *vti file from TTK ("start_data.vti")
            if (args.ttk_task == 'ms'):
                d = {}
                if args.choose_data is not None:
                    if len(args.choose_data) > 1:
                        parser.error('choose one variable for which Morse-Smale complex will be calculated (--chose_data=var)')
                    else:
                        d['choose_data'] = args.choose_data[0] # args.choose_data is in this case a one-element list; get this one element
                else:
                    parser.error('choose a variable for which Morse-Smale complex will be calculated (--chose_data=var)')

                if args.fout_num_postprocess is not None:
                    d['fout_num_postprocess'] = args.fout_num_postprocess
                else:
                    d["fout_num_postprocess"] = None


                self.ttk_scalar_data = d

            elif (args.ttk_task == 'bottleneck'):
                d = {}
                if args.choose_data is not None:
                    if len(args.choose_data[0].split(',')) == 2:
                        #d['choose_data'] = args.choose_data
                        d['choose_data'] = args.choose_data[0].split(',')
                    else:
                        parser.error('bottleneck filter requires exactly two variables, use --chose_data=var1,var2 in the input')
                else:
                    parser.error('bottleneck filter requires specifying two variables, use --chose_data=var1,var2 in the input')

                if args.fout_num_postprocess is not None:
                    d['fout_num_postprocess'] = args.fout_num_postprocess

                self.ttk_multi_data = d

        #    elif (args.ttk_task == 'scatterplot'):
        #        print('to do')

        #    if (args.fout_num_scope) is None:
        #        parser.error('please provide fout_num_scope = what type of numerical data is expected from TTK?')
        #    else:
        #        self.options['fout_num_scope'] = args.fout_num_scope

    def test_start_option(self, key):
        if key is None:
            key = [None for x in range(self.nr_inp_blocks)]
        else:
            if len(key) != self.nr_inp_blocks:
                sys.exit('please use as many {} keys as blocks or do not use them at all, quitting...'.format(key))
        return key


    def varnames_rename(self, args, finp):

        new_colnames = []
        with open(finp, 'r') as f:
            f.seek(0)
            colnames = f.readline().split(',')

            if args is not None:
                # replace
                for arg in args.split(','):
                    for col in colnames:
                        if arg.split(':')[0] == col:
                            # replace:
                            col = arg.split(':')[1]
                        new_colnames.append(col)
                fout=finp+'.cp'
                with open(fout, 'w') as g:
                    g.write(','.join(new_colnames))
                    for line in f.readlines():
                        g.write(line)

            else:
                new_colnames = colnames

        all_varnames=[x.strip() for x in new_colnames[3:]]

        if args is not None:
            shutil.copyfile(fout, finp)
            os.remove(fout)

        return all_varnames



    def set_finp_prep(self, finp_prep=None, finp=None):

        if finp_prep is not None:
            if os.path.isabs(finp_prep):
                f_out = finp_prep
            else:
                f_out = os.path.abspath(finp_prep)

        elif finp is not None:
            inp_path, inp_name = os.path.split(os.path.abspath(finp))
            f_out = os.path.join(inp_path, "formatted_"+inp_name)

        return f_out
 

    def str2bool(self,s):
        """Convert string to bool (in argparse context)."""
        if s.lower() not in ['true', 'false']:
            raise ValueError('Need bool; got %r' % s)
        return {'true': True, 'false': False}[s.lower()]


    def append_data_or_None(self, s):
        return s


    def prepare_csvdata_files_for_ttk(self):

        grid_column_names_3D = ['x', 'y', 'z']

        for i in range(self.nr_inp_blocks):

            f = self.options["finp"][i]

            if self.ttk_start_data[f]['prep']:

                # column names:
                varnames = self.ttk_start_data[f]['varnames'].split(',')
                input_column_names = [x.strip() for x in (grid_column_names_3D + varnames)]

                # header lines to skip:
                skip = self.ttk_start_data[f]['nr_header_lines']

                # column separator:
                #if self.options['sep'][i] is not None:

                # prepare file:
                self.prepare_csvdata_file_for_ttk(f,
                                                  input_column_names,
                                                  skip,
                                                  sep=self.ttk_start_data[f]['sep'],
                                                  fout=self.ttk_start_data[f]['finp_prep'])



    def prepare_csvdata_file_for_ttk(self, finp, cols, skip, sep=None, fout=None):
        """
        preparing the csv file to be read by TTK:
        - the csv file should have a header with column names
        - the columns on that file should be separated by a coma
        - additionally make sure that all elements are numeric

        to do:
        * sep is not working properly, now hardcoded to r"\s+" on the input and "," on the output
        """

        if sep is not None:
            data = numpy.genfromtxt(finp,
                                    dtype=float,
                                    comments='#',
                                    delimiter=sep,
                                    skip_header=skip,
                                    names=cols,
                                    autostrip=True)
        else:
            data = numpy.genfromtxt(finp,
                                    dtype=float,
                                    comments='#',
                                    skip_header=skip,
                                    names=cols,
                                    autostrip=True)

        numpy.savetxt(fout,
                      data,
                      fmt='%.6e',
                      delimiter=',',
                      comments='',
                      newline='\n',
                      header=','.join(cols))



    def print_options(self):

        #self.parse_options()

        print("\n")
        print("all input options:")
        for option_key, option_value in self.options.items():
            print("{}: {}".format(option_key, option_value))

        print("\n")
        print("ttk_start_data:")
        for k, v in self.ttk_start_data.items():
            print("{}: {}".format(k, v))

        print("ttk_scalar_data:")
        for k, v in self.ttk_scalar_data.items():
            print("{}: {}".format(k, v))


    def apply_calculator(self, val):
        # parse:
        result    = val.split(':')[0].strip()
        operation = val.split(':')[1].strip()





if __name__ == '__main__':
    data = input_data()  # for testing this module read keywords from the command line
    data.print_options()




