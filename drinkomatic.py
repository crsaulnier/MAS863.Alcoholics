import time
import math
import copy
import random
from drink_mixing import mymix
from gesaltdrinkomatic import *

from MeteorClient import MeteorClient

client = MeteorClient('ws://127.0.0.1:3000/websocket')

list_drinks=[];
list_drinks_alcohol=[];
list_drinks_bin=[];
#global list_drinks_alcohol_all
#global list_drinks_bin_all
#global list_drinks_all_final
list_drinks_alcohol_all=[];
list_drinks_bin_all=[];


global count_old
count_old=0
times=0


###########################  (Defining mix) ############################

mydict = {}

#initialize drink list,n_drinks,radii
drinks = ['white_wine','gin','whisky','tequila','cognac','vodka','bourbon','cointreau'];
ndrinks = 8;
r = [1]*ndrinks #same radius; change if needed
angles = [ind*(2*math.pi/ndrinks) for ind in range(0,ndrinks)]


#populate the directory
for i,drink in enumerate(drinks):
    mydict[drink] = (r[i],angles[i]);

#print 'my drink dictionary:\n %s' %mydict

###########################  (Defining mix) ############################

def subscribed(subscription):
    print('* SUBSCRIBED {}'.format(subscription))


def unsubscribed(subscription):
    print('* UNSUBSCRIBED {}'.format(subscription))


def added(collection, id, fields):
    #print('* ADDED {} {}'.format(collection, id))
    global times
    times = times+1
    print('*** entered added() - times: %s ' %times)
    list_drinks_alcohol=[];
    list_drinks_bin=[];
    list_drinks_alcohol_return=[];
    check= False;
    

    for key, value in fields.items():

        if key == 'incompleteCount':
            Alcohol_not_used=value;
            print (Alcohol_not_used)
            
        if key == 'text':
            list_drinks_alcohol.insert(0,value);

        if key == 'checked':
            list_drinks_bin.insert(0,value);
            check=value

        if check == True:
            #print('  - FIELD Added {} {}'.format(key, value))
            list_drinks_bin_all.extend(list_drinks_bin);
            #print ('Adding this alcohol')
            #print(list_drinks_alcohol)
            list_drinks_alcohol_all.extend(list_drinks_alcohol);
            #print('checked = true, added to list')
            #print (list_drinks_alcohol_all)


    #print (list_drinks_alcohol)
    #print (list_drinks_bin)
    #print (list_drinks_bin_all)
    
    print('list_drinks_alcohol_all list:')
    print (list_drinks_alcohol_all)

    print('list_drinks_alcohol_return list:')
    print (list_drinks_alcohol_return)
    
    
    
    #while len(list_drinks_alcohol_all) > 0 : list_drinks_alcohol_all.pop()
    
    if (len(list_drinks_alcohol_all) == 0) :
        times = 0
    
    
    if (times >= 8) :
        times=0;
        print('list reached all elem')
        list_drinks_alcohol_return=copy.copy(list_drinks_alcohol_all)
        del list_drinks_alcohol_all[:]
        print('list_drinks_alcohol_return now:')
        print (list_drinks_alcohol_return)
        mymix(list_drinks_alcohol_return)
		  
		  #### add the gestalt function ******
        return list_drinks_alcohol_return
    else :
        print('not reached all elem list_drinks_alcohol_all return:')
        return list_drinks_alcohol_all
    
    
    #count_old=count_old+count_new


   
   ######## This is for collection subscription - DO NOT REMOVE
    if collection == 'lists':
        client.subscribe('todoall')
        all_todoschange = client.find('todoall', selector={})
        client.unsubscribe('todoall')
    ######## This is for collection subscription - DO NOT REMOVE





###### added to populate the drink mix components ##########

def mymix(list_drinks): #list_drinks contains components of mix
    n_mix = len(list_drinks);
    mixdict = {} #will contain (r_drink,theta_drink,amount)
    for drink in list_drinks:
        mixdict[drink] = mydict[drink]+(1/float(n_mix),);

    print 'positions and amount for my mix:\n %s' %mixdict
    return mixdict

#test




###### added to populate the drink mix components ##########

# if collection == 'list' you could subscribe to the list here
# with something like
# client.subscribe('todos', id)
# all_todos = client.find('todos', selector={})
# print 'Todos: {}'.format(all_todos)




def changed(collection, id, fields, cleared):
    print('* CHANGED {} {}'.format(collection, id))
    for key, value in fields.items():
        print('  - FIELD Changed {} {}'.format(key, value))
    for key, value in cleared.items():
        print('  - CLEARED Changed {} {}'.format(key, value))
    if collection == 'lists':
        print (id)
        client.subscribe('todoall')
        all_todoschange = client.find('todoall', selector={})
        print 'TodosChange: {}'.format(all_todoschange)
        print('Num TodosChange: {}'.format(len(all_todoschange)))
        client.unsubscribe('todoall')



    #FIXME:
    #added(collection, id, fields)
#added(collection, id, cleared)



def connected():
    print('* CONNECTED')


def subscription_callback(error):
    if error:
        print(error)

client.on('subscribed', subscribed)
client.on('unsubscribed', unsubscribed)
client.on('added', added)
client.on('connected', connected)
client.on('changed', changed)

client.connect()
client.subscribe('publicLists')
#client.subscribe('lists')
#client.subscribe('todos',id)


# -------------------------------------------------------------------------
# THIS IS WHERE THE MACHINE MAGIC HAPPENS
# -------------------------------------------------------------------------
# The persistence file remembers the node you set. It'll generate the first time you run the
# file. If you are hooking up a new node, delete the previous persistence file.
stages = virtualMachine(persistenceFile = "test.vmp")

# This is for how fast the
stages.machineNode.setVelocityRequest(8)
	
# THESE ARE THE HELPER FUNCTIONS YOU NEED TO MOVE THINGS AROUND

# pour from each bottle for x seconds

while True:
	command = raw_input("Command:")
	if command == "u":
		stages.moveUp()
	elif command == "d":
		stages.moveBottom()
	elif command == "r":
		stages.machineNode.setVelocityRequest(1)
		stages.rotateDrink(random.randint(0, 50))
		stages.machineNode.setVelocityRequest(8)
	elif command == "e":
		break


# (sort of) hacky way to keep the client alive
# ctrl + c to kill the script


client.unsubscribe('publicLists')
#client.unsubscribe('lists')
client.unsubscribe('todos')