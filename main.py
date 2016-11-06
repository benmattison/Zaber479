# The main function called for our software. There should not be a lot of code in here, most stuff should be done in other code.

# Pseudocode:

# Have the user select if they want to do a camera calibration or not. If not, load a default calibration.

# Initiate cameras

# For calibration, have markers on the screen that identify where the pattern should go. Automatically take pictures when it is there.
# Save the calibration data to a readable file.

# Identify COM ports, find the stages.

# Begin tracking end effector

# Move stage 1 twice and save motion points.
# Evaluate the motion from those points.

# ...

# Determine the heirarchy of rotary stages

# Output useful data about the axes of motion of the devices, including transformation matrices between stages.