description of tests:
=====================

* tests that generate "start state" for TTK:

    * onedim_one_start_from_qc:
        * on input we take the density on ONE text file (as from Dirac or pyadf calculations),
          the first step is to re-format the density file to the TTK-convenient input csv format

    * onedim_one_start_noprep
        * on input we take the density on ONE text file, already formatted for TTK
          (no preprocessing step)

    * multidim_many_start_from_qc
        * on input we take the density on FEW text files (as from Dirac or pyadf calculations)
          the first step is to re-format the density file to the TTK-convenient input csv format

    * multidim_many_start_noprep
        * on input we take the density on FEW text files, already formatted for TTK
          (no preprocessing step)


    all these tests generate a vti file which can be opened as:
    
    ```
    paraview file.vti
    ```


* tests that calculate the critical points from the Morse-Smale complex:

    * onedim_one_ms

    data generated in these tests:
