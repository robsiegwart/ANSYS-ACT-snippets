# ANSYS-ACT-snippets

Collection of some files for performing scripting in ANSYS Mechanical via the ACT API.

Note that scripting in ANSYS Mechanical uses Python 2.

## Contents

### `Export Beams Probes from Connections.py`

This file loops through beam objects in the Connections folder and searches for
the corresponding beam probes in the Solution. If a beam probe is not already
in the Solution for that beam then a new one is created. Beam results are then
saved out to a text file in the `user_files` directory of the project.

The output text file is tab-delimited with the following contents/columns:

    Beam Name    Axial Force    Torque    Shear Force at I    Shear Force at J    Moment at I    Moment at J

### `Export Weld Force-Moment Probes from Solution.py`

This script exports force and moment result probes associated with structural
welds. This is applicable when Bonded contact is used to represent welded
connections. Usage of the script is performed by first creating a force and
moment probe for each contact pair that represents a welded connection. These
are then all placed within a grouping folder in the Solution portion of the tree
having the word "weld" in it (case insensitive). This is used to designate those
result objects that are considered welds. Force and moment results are they
saved to a text file in the `user_files` directory of the project.

The output text file is tab-delimited with the following contents/columns:
    
    Probe Name    FX    FY    FZ    MX    MY    MZ

## Usage

Open the ACT pane with the button (pre-tabbed application shown):
![ANSYS ACT button](images/BTN.png)

Copy and paste script contents into the console of the ANSYS ACT pane:
![ANSYS ACT console](images/console.png)