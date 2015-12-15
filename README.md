# MAS863.Alcoholics
The software behind the drink bot 3000. (It needs a new name)


The following helper functions are defined in gestaltdrinkomatic.py - which handles all of the absrtaction to the hardware.

All magic number variables are defined in the top of the virtural machine class. 

From within drinkomatic.py (which is the application to run) you can call the following interfaces

for the purpose of the API you can think of coordinates being (drinknumber, platform_height, platform_height). The internals are a little more complex. 

After defining the machine (which is called stages) You can call:

# blocks on a move
# based on nadya's code... I don't think it works quite as expected yet
# is close enough for now
# will try to fix later.
stages.blockOnMove():

# moves to (x, top, top)
# this would be the pouring position
# magic number in class definition
stages.moveUp():

# moves to (x, 0, 0)
# this would be the grabbing a drink position at the end
stages.moveBottom():

# moves the platform down enough to spin the platform
#magic number of enough in class definition
# moves to (x, top-jog, top-jog)
self.jogDown():

# rotates the platform to drink x
# moves to (drink_location, x, x)
self.rotateDrink(bottle):

# rotate to bottle x, move up, pour for y seconds, then move down
self.pourDrink(bottle, seconds):

# does a spin pouring from each bottle for x seconds
self.do_a_spin(seconds):

A common failure mode is that something happens to the test.vmp file if you crash the program and the nodes can't communicate anymore - delete it and re-ID the nodes.  

Right now the front end hasn't been integrated so from the command line after running drinkomatic.py you can use:

u: move up
d: move down
r: rotate a random ammount!
e: exit the program'