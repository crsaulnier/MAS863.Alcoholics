import math

mydict = {}

#initialize drink list,n_drinks,radii
drinks = ['white_wine','gin','whisky','tequila','cognac','vodka','bourbon','cointreau']
ndrinks = 8
r = [1]*ndrinks #same radius; change if needed
angles = [ind*(2*math.pi/ndrinks) for ind in range(0,ndrinks)]


#populate the directory
for i,drink in enumerate(drinks):
    mydict[drink] = (r[i],angles[i])


print 'my drink dictionary:\n %s' %mydict

def mymix(list_drinks): #list_drinks contains components of mix
    n_mix = len(list_drinks)
    mixdict = {} #will contain (r_drink,theta_drink,amount)
    for drink in list_drinks:
        mixdict[drink] = mydict[drink]+(1/float(n_mix),)
    
    return mixdict


#test
print 'positions and amount for my mix:\n %s' %mymix(['whisky','tequila'])
