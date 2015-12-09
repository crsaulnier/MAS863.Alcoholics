# Drink-o-matic
# Has two y-stages to move a platform up and down and one polar stage
# we might have to hack the polar stage to be linear
# moves get set in Main
# usb port needs to be set in initInterfaces
# Nadya Peek Dec 2014
# Chris Saulnier December 2015

#------IMPORTS-------
from pygestalt import nodes
from pygestalt import interfaces
from pygestalt import machines
from pygestalt import functions
from pygestalt.machines import elements
from pygestalt.machines import kinematics
from pygestalt.machines import state
from pygestalt.utilities import notice
from pygestalt.publish import rpc	#remote procedure call dispatcher
import time
import io
import math

#------VIRTUAL MACHINE------
class virtualMachine(machines.virtualMachine):

	# THESE ARE MAGIC NUMBERS THAT LET EVERYTHING WORK TOGETHER
	diameter = 100
	numBottles = 8
	top = 120
	deltaDown = 120

	def initInterfaces(self):
		if self.providedInterface: self.fabnet = self.providedInterface		#providedInterface is defined in the virtualMachine class.
		else: self.fabnet = interfaces.gestaltInterface('FABNET', interfaces.serialInterface(baudRate = 115200, interfaceType = 'ftdi', portName = '/dev/tty.usbserial-FTY4ULMS'))
		
	def initControllers(self):

		self.polarAxisNode = nodes.networkedGestaltNode('Polar Axis', self.fabnet, filename = '086-005a.py', persistence = self.persistence)

		self.y1AxisNode = nodes.networkedGestaltNode('Y1 Axis', self.fabnet, filename = '086-005a.py', persistence = self.persistence)
		self.y2AxisNode = nodes.networkedGestaltNode('Y2 Axis', self.fabnet, filename = '086-005a.py', persistence = self.persistence)

		#self.yyNode = nodes.compoundNode(self.y1AxisNode, self.y2AxisNode)
		self.machineNode = nodes.compoundNode(self.polarAxisNode, self.y1AxisNode, self.y2AxisNode)

	def initCoordinates(self):
		self.position = state.coordinate(['mm', 'mm', 'mm'])
	
	def initKinematics(self):

		self.polarAxis = elements.elementChain.forward([elements.microstep.forward(4), elements.stepper.forward(1.8), elements.pulley.forward(100), elements.invert.forward(False)])

		# the argument to pulley.forward is the diameter of the circle that the button poker travels in
		# one full revolution of the poker is a coordinate of the diameter of the circle it travels in, times pi

		self.y1Axis = elements.elementChain.forward([elements.microstep.forward(4), elements.stepper.forward(1.8), elements.leadscrew.forward(8), elements.invert.forward(False)])
		self.y2Axis = elements.elementChain.forward([elements.microstep.forward(4), elements.stepper.forward(1.8), elements.leadscrew.forward(8), elements.invert.forward(False)])

		self.stageKinematics = kinematics.direct(3)	#direct drive on all axes
	
	def initFunctions(self):
		self.move = functions.move(virtualMachine = self, virtualNode = self.machineNode, axes = [self.polarAxis, self.y1Axis, self.y2Axis], kinematics = self.stageKinematics, machinePosition = self.position,planner = 'null')
		self.jog = functions.jog(self.move)	#an incremental wrapper for the move function
		pass
		
	def initLast(self):
		#self.machineControl.setMotorCurrents(aCurrent = 0.8, bCurrent = 0.8, cCurrent = 0.8)
		#self.xNode.setVelocityRequest(0)	#clear velocity on nodes. Eventually this will be put in the motion planner on initialization to match state.
		pass
	
	def publish(self):
		#self.publisher.addNodes(self.machineControl)
		pass
	
	def getPosition(self):
		return {'position':self.position.future()}
	
	def setPosition(self, position  = [None]):
		self.position.future.set(position)

	def setSpindleSpeed(self, speedFraction):
		#self.machineControl.pwmRequest(speedFraction)
		pass

	# THESE ARE THE HELPER FUNCTIONS THAT MAKE THINGS HAPPEN
	def blockOnMove(self):
		status = self.y1AxisNode.spinStatusRequest()
		# This checks to see if the move is done.
		while status['stepsRemaining'] > 0:
			time.sleep(0.001)
			status = self.y1AxisNode.spinStatusRequest()

	# moves to (x, top, top)
	def moveUp(self):
		current = self.getPosition()
		newPosition = [0, self.top, self.top]
		newPosition[0] = current['position'][0]
		self.move(newPosition, 0)

	# moves to (x, 0, 0)
	def moveBottom(self):
		current = self.getPosition()
		newPosition = [0, 0, 0]
		newPosition[0] = current['position'][0]
		self.move(newPosition, 0)
	
	# moves down enough to spin the platform
	def jogDown(self):
		current = self.getPosition()
		newPosition = [0, self.top-self.deltaDown, self.top-self.deltaDown]
		newPosition[0] = current['position'][0]
		self.move(newPosition, 0)

	# rotates the platform to drink x
	def rotateDrink(self, bottle):
		current = self.getPosition()
		newPosition = [self.diameter*math.pi*bottle/self.numBottles, 0, 0]
		newPosition[1] = current['position'][1]
		newPosition[2] = current['position'][2]
		self.move(newPosition, 0)

	# pour drink x for y seconds
	def pourDrink(self, bottle, seconds):

		# rotate to the proper bottle
		self.rotateDrink(bottle)
		# move to top as defined in the gestalt machine
		self.moveUp()
		# will not return until the platform is done the current move
		self.blockOnMove()
		# pour the drink for x seconds
		time.sleep(seconds)
		# jog down so you can rotate the platform and are no longer sleeping
		self.jogDown()

	# does a spin pouring from each bottle for x seconds
	def do_a_spin(self, seconds):

		for x in range (0, self.numBottles):
			self.pourDrink(x, seconds)
		
		self.moveBottom()







#------IF RUN DIRECTLY FROM TERMINAL------
if __name__ == '__main__':
	# The persistence file remembers the node you set. It'll generate the first time you run the
	# file. If you are hooking up a new node, delete the previous persistence file.
	stages = virtualMachine(persistenceFile = "test.vmp")

	# You can load a new program onto the nodes if you are so inclined. This is currently set to 
	# the path to the 086-005 repository on Nadya's machine. 
	#stages.xyNode.loadProgram('../../../086-005/086-005a.hex')
	
	# This is a widget for setting the potentiometer to set the motor current limit on the nodes.
	# The A4982 has max 2A of current, running the widget will interactively help you set. 
	#stages.xyNode.setMotorCurrent(0.7)

	# This is for how fast the 
	stages.machineNode.setVelocityRequest(8)
	
	# Some random moves to test with
	# moves = [[10,10, 10],[20,20, 20],[10,10, 10],[0,0,0]]
	#moves = [[31.5,0, 0]]
	moves = [[166.6875*math.pi*1/8, 0, 0], [166.6875*math.pi*1/8, 20, 20], [166.6875*math.pi*1/8, 0, 0],
				[166.6875*math.pi*2/8, 0, 0], [166.6875*math.pi*2/8, 20, 20], [166.6875*math.pi*2/8, 0, 0],
				[166.6875*math.pi*3/8, 0, 0], [166.6875*math.pi*3/8, 20, 20], [166.6875*math.pi*3/8, 0, 0],
				[166.6875*math.pi*4/8, 0, 0], [166.6875*math.pi*4/8, 20, 20], [166.6875*math.pi*4/8, 0, 0],
				[166.6875*math.pi*5/8, 0, 0], [166.6875*math.pi*5/8, 20, 20], [166.6875*math.pi*5/8, 0, 0],
				[166.6875*math.pi*6/8, 0, 0], [166.6875*math.pi*6/8, 20, 20], [166.6875*math.pi*6/8, 0, 0],
				[166.6875*math.pi*7/8, 0, 0], [166.6875*math.pi*7/8, 20, 20], [166.6875*math.pi*7/8, 0, 0],
				[166.6875*math.pi*8/8, 0, 0], [166.6875*math.pi*8/8, 20, 20], [166.6875*math.pi*8/8, 0, 0]]
	
	# one full revolution of the poker is a coordinate of the diameter of the circle it travels in, times pi
	
	# Move!
	for move in moves:
		stages.move(move, 0)
		status = stages.y1AxisNode.spinStatusRequest()
		# This checks to see if the move is done.
		while status['stepsRemaining'] > 0:
			time.sleep(0.001)
			status = stages.y1AxisNode.spinStatusRequest()
	


