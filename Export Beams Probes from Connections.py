'''
Title:        Beam Probe Exporting Script for ANSYS Mechanical

Author:       Rob Siegwart

Updated:      9/5/2019

Description:  This is a Mechanical ACT script to save out beam result probes to
              a text file.

              This version loops through the beams in the Connections folder and
              searches for the corresponding beam probes in the Solution. If a
              beam probe is not already in the Solution for that beam then a new
              one is created. Therefore you do not need to already have created
              the result probes in the Solution.

              The output text file is tab-delimited with the following
              contents/columns:
              
                  Beam Name    Axial Force    Torque    Shear Force at I    Shear Force at J    Moment at I    Moment at J
              
              Remember that ANSYS uses Python 2.x.

ANSYS         17.1, 2019R1
versions
tested with: 

'''

# Set the working directory to the user_files directory of the project
from os import chdir
MECH_dir = ExtAPI.DataModel.Project.Model.Analyses[0].WorkingDir
user_dir = MECH_dir.split('_files')[0] + r'_files\user_files'
chdir(user_dir)

# Create variables for connections and solution objects
connections = ExtAPI.DataModel.Project.Model.Connections
solution = ExtAPI.DataModel.Project.Model.Analyses[0].Solution

# Filter the connections and solution items for beams and beam probes, respectively
cont_beams = filter(lambda item: item.GetType() == Ansys.ACT.Automation.Mechanical.Connections.Beam, connections.Children)
sol_beam_probes = filter(lambda item: item.GetType() == Ansys.ACT.Automation.Mechanical.Results.ProbeResults.BeamProbe, solution.Children)

# Create a list of beams from the solution beam probes
sol_beams = map(lambda bp: bp.BoundaryConditionSelection, sol_beam_probes)

# Convert the connections and solution beams lists to sets and compare to find differences
beams_to_create = set(cont_beams) - set(sol_beams)

# Create a beam probe for each beam not already having a result probe
if beams_to_create:
    for beam in beams_to_create:
        bp = solution.AddBeamProbe()
        bp.BoundaryConditionSelection = beam
        sol_beam_probes.append(bp)

solution.EvaluateAllResults()

# Open an output file to write results to
f = open('Beam results.txt','w')
f.write('Beam Probes\n\n')
f.write('Name\tAxial Force\tTorque\tShear Force at I\tShear Force at J\tMoment at I\tMoment at J\n\n')

# Write out beam probes to a file
#   the unit segment (e.g. [lbf]) is stripped from the result
for br in sol_beam_probes:
    name = str(br.BoundaryConditionSelection.Name).strip()
    f.write( name + '\t' +
             str(br.AxialForce).split('[')[0] + '\t' +
             str(br.Torque).split('[')[0] + '\t' +
             str(br.ShearForceAtI).split('[')[0] + '\t' +
             str(br.ShearForceAtJ).split('[')[0] + '\t' +
             str(br.MomentAtI).split('[')[0] + '\t' +
             str(br.MomentAtJ).split('[')[0] + '\n' )

f.close()
