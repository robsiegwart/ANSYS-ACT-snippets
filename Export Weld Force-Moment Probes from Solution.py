# MIT License

# Copyright (c) 2020 Rob Siegwart

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

'''
Weld Exporting Script for ANSYS Mechanical
==========================================

This is a Mechanical ACT script to save out Force and Moment probes defined in
the Solution portion of the tree, associated with Bonded contact representing
welds.

To mark Force/Moment probes as welds, they must be in a group with the word
'weld' in it (case insensitive). Then, all force and moment probes contained
in it are exported.

The file is saved to the 'user_files' directory associated with the project
and is called 'Weld Results.txt'.

Force probes are used as the master list and so the program loops through the
forces and finds the corresponding moment probe for the same contact item.
Stray moment probes will not be discovered. If no moment probe exists, a new
line is added and the data for the moment fields are blank.

The output text file is tab-delimited with the following contents/columns:
    
    Probe Name    FX    FY    FZ    MX    MY    MZ


To Use
------
Put a Force and Moment probe for each desired contact item in the Solution,
within a folder with the word 'weld' in it. This can be sped up by
right-clicking on the Contact item in the Connections folder and choosing
"Create > Force Reaction" and "Create > Moment Reaction".

For example:

    [-] Solution (A6)
        |-- Solution Information
        |-- [-] Welds 1
            |-- [-] Box 1
            |    |-- Force Reaction 1
            |    |-- Moment Reaction 1
            |-- [-] Box 2 
            |    |-- Force Reaction 3
            |    |-- Moment Reaction 3
            |-- Force Reaction 4
            |-- Moment Reaction 4


Notes
-----
For moment summation the default is to use the centroid of the contact element
set. If your contact geometry accurately represents the weld geometry then this
will be ok. Otherwise you will likely need some small value of trim set in the
contact definition, so that the moment summation point is approximately at the
actual centroid of the weld group. Alternatively, a custom coordinate system
could be used but this is not supported in this script yet.

Remember that ANSYS uses Python 2.x.

Limitations:
  Does not support custom coordinate systems for the moment summation. Could be
  a future feature.

ANSYS versions tested with:
  17.1

A nice future feature for this script would be to grab the contacts
marked as welds in the **connections** folder and then find the
corresponding force and moment probes in the solution object if
they exist or create new ones if they don't already exist.


VERSION 0.2.0
'''

# Set the working directory to the user_files directory of the project
from os import chdir
MECH_dir = ExtAPI.DataModel.Project.Model.Analyses[0].WorkingDir
user_dir = MECH_dir.split('_files')[0] + r'_files\user_files'
chdir(user_dir)

# Create variables for connections and solution objects
connections = ExtAPI.DataModel.Project.Model.Connections
solution = ExtAPI.DataModel.Project.Model.Analyses[0].Solution

# The unit portion (e.g. [lbf] and [lbf-in]) is stripped from the result so that it may be imported into Excel and used as is
solution_weld_groups = filter(lambda item: item.GetType() == Ansys.ACT.Automation.Mechanical.TreeGroupingFolder, solution.Children)
solution_weld_groups = filter(lambda item: 'weld' in item.Name.lower(), solution_weld_groups)


def cleanup_name(string):
    '''
    Clean up the default ANSYS names after you right-click and select
    "Rename Based on Definition". Removes common elements that show up in the
    name.
    '''
    to_remove = ['All - ', ' (Underlying Element)', 'End Time', ' - ', 'Force Reaction', 'Contact', '1. s' ]
    name = string
    for each in to_remove:
        name.replace(each,'')
    return name.strip()
   
   
def save_forces_moments(items_list, folder_name=None):
    '''
    Loop through a list of ANSYS items and save force and moment probes. The
    forces are used as the master - moments are looked up based on the force.
    Stray moment probes won't be discovered.
        
    Set a string to folder_name to have it print the folder name in the output
    file.

    Parameters
    ----------
    items_list      a list of ANSYS objects to filter for force, moments
    folder_name     an optional name to include in the output text name description
    '''
    forces = filter(lambda x: x.GetType() == Ansys.ACT.Automation.Mechanical.Results.ProbeResults.ForceReaction, items_list)
    moments = filter(lambda x: x.GetType() == Ansys.ACT.Automation.Mechanical.Results.ProbeResults.MomentReaction, items_list)
    
    if not forces:
        return
        
    if folder_name:
        f.write(' {} '.format(folder_name).center(20,'-') + '\n')

    for force in forces:
        bc = force.ContactRegionSelection
        name = cleanup_name(bc.Name)
        f.write( name + '\t' +
                 str(force.XAxis).split('[')[0] + '\t' +
                 str(force.YAxis).split('[')[0] + '\t' +
                 str(force.ZAxis).split('[')[0] + '\t' )
        
        # look for the moment load that is of the same contact item
        moment_sel = filter(lambda mr: mr.ContactRegionSelection == bc, moments)
        if len(moment_sel) > 1:
            f.write('\n')
            continue
        try:
            moment = moment_sel[0]
            f.write( str(moment.XAxis).split('[')[0] + '\t' +
                     str(moment.YAxis).split('[')[0] + '\t' +
                     str(moment.ZAxis).split('[')[0] + '\n' )
        except IndexError:
            f.write('\n')
            print 'Cannot find corresponding Moment Probe'


def loop(items, name=None):
    '''
    Loop function to recursively save out force/moments from nested folders.

    Parameters
    ----------
    items       a list of ANSYS solution objects
    '''
    save_forces_moments(items, name)
    sub_folders = filter(lambda x: x.GetType() == Ansys.ACT.Automation.Mechanical.TreeGroupingFolder, items)
    for group in sub_folders:
        loop(group.Children, group.Name)
        

# Write out force/moment probes to a file
f = open('Weld results.txt','w')
f.write('Welds\n\n')
f.write('Name\tFX\tFY\tFZ\tMX\tMY\tMZ\n\n')
loop(solution_weld_groups)
f.close()