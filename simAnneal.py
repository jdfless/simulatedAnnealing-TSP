#!/usr/bin/python

"""
Jonathan Flessner, Chris Sanford, Erin Marshall
Group 14
5-December-2014
Travelling Salesman Problem
Simulated Annealing Method
CS-325
"""
from math import sqrt
from os.path import isfile
from sys import argv
from sys import maxint
from random import randrange
from random import random
from random import choice
from time import clock
import signal

#global variables
cid = []				#holds city ids - not strictly necessary, kept for convenience
x = []					#holds x coords
y = []					#holds y coords
v = []					#holds visited boolean (0 no, 1 yes) - not using currently
lookup = [] 			#holds all distances 2d
n = 0 					#number of cities
routeDistance = maxint	#holds current routes distance
bestDistance = maxint	#holds best distance overall
bestRoute = []			#holds best current route
tempStart = 1.5e+5
tempEnd = 0
temperature = int(tempStart)

#gets data from input file, stores in global variables
def getCities(inFile):
	global cid, x, y, v, n 	#these globals can be modified here

	if not isfile(inFile):
		print "File " + str(inFile) + " does not exist."
		exit(1)
	fd = open(inFile, 'r+')
	for city in fd:
		city = city.split()									#split on whitespace (any amount, spaces or tabs)
		if len(city) != 3:									#if not id, x, y - wrong format
			print "Input data formatted incorrectly."
			fd.close()
			exit(1)
		try:												#if can't cast as ints - wrong format
			cid.append(int(city[0]))		
			x.append(int(city[1]))
			y.append(int(city[2]))
			v.append(0)
		except TypeError:									#end graceful on typeerrors
			print "Input data formatted incorrectly."
			fd.close()
			exit(1)
		n += 1
	fd.close()

	#lookup all distances and store
	distanceTable()
	return

#dump results to file
def outputFunction(inFile):
	outFile = str(inFile) + ".tour"
	wfd = open(outFile, 'w')
	wfd.write(str(bestDistance) + '\n')
	for i in bestRoute:
		wfd.write(str(i) + '\n')
	wfd.close()
	return

#create triangular matrix, accessable through getCityDistance function
def getAllDistances(city):
	global lookup
	lookup.append([])
	j = city
	while j < n:
		lookup[-1].append(getDistance(x[j], x[city], y[j], y[city]))
		j += 1
	return

#create triangular matrix
def distanceTable():
	city = 0
	while city < n:
		getAllDistances(city)
		city += 1
	return

#usable way to access lookup table distances
def getCityDistance(city1, city2):
	if city1 > city2:
		city1 = city1 - city2
		return lookup[city2][city1]
	else:
		city2 = city2 - city1
		return lookup[city1][city2]

#calculate distance from raw data
def getDistance(x2, x1, y2, y1):
	a = (x2 - x1) ** 2
	b = (y2 - y1) ** 2
	c = int(round(sqrt(a+b))) #c is now the distance (as a rounded int) between the 2 cities
	return c

def pickRandomCity():
	return randrange(n)

#pick two non identical random cities
def pickTwoRandomCities():
	a = randrange(n)
	b = randrange(n)
	while a == b:
		a = randrange(n)
		b = randrange(n)
	return a, b

#populate route in order
def fillRoute():
	route = []
	for i in cid:
		route.append(i)
	return route

#swap city locations in route
def swapCities(route, city1, city2):
	route[city1], route[city2] = route[city2], route[city1]
	return route

#calculate entire route cost
def calcRouteCost(currentRoute):
	global routeDistance
	routeDistance = 0
	i = 0
	while i < (n-1):
		routeDistance += getCityDistance(currentRoute[i], currentRoute[i+1])
		i += 1
	routeDistance += getCityDistance(currentRoute[n-1], currentRoute[0])
	return 

#NOT FUNCTIONAL :( - attempt to further optimize
def calcSwapRouteCost(currentRoute, city1, city2):
	global routeDistance
	prev1 = (city1 - 1) % n
	next1 = (city1 + 1) % n
	prev2 = (city2 - 1) % n
	next2 = (city2 + 1) % n
	#subtract old distances
	routeDistance -= getCityDistance(prev1, city1)
	routeDistance -= getCityDistance(prev2, city2)
	routeDistance -= getCityDistance(city1, next1)
	routeDistance -= getCityDistance(city2, next2)

	#add new distances
	routeDistance += getCityDistance(prev1, city2)
	routeDistance += getCityDistance(prev2, city1)
	routeDistance += getCityDistance(city2, next1)
	routeDistance += getCityDistance(city1, next2)
	
	return

#reset route distance
def setDistance(origDist):
	global routeDistance
	routeDistance = origDist
	return

#return bool on whether or not swap decreased cost
def keepNewRoute(origDist):
	global temperature
	if routeDistance < origDist:
		return True
		temperature = tempStart
	else:
		return False

#check for new overall best distance
def checkForBest(route):
	global bestDistance, bestRoute
	if routeDistance < bestDistance:
		bestDistance = routeDistance
		bestRoute = route
		print bestDistance
	return

#return two closest cities to a start value
def getTwoClosest(here):
	#get two closest cities, move to each, put one at end, other at beginning
	closest1 = maxint
	closest2 = maxint
	city1 = -1
	city2 = -1
	for i in cid:
		if i == here:
			pass
		else:
			cost = getCityDistance(here, i)
			if cost < closest1:
				closest2 = closest1
				city2 = city1
				closest1 = cost
				city1 = i
			elif cost < closest2 and cost >= closest1:
				closest2 = cost
				city2 = i
	return city1, city2

#check if -1 return, then all values visited
def getClosest(here):
	cost = maxint
	city = -1
	for i in cid:
		if v[i] == 1:
			pass
		else:
			newCost = getCityDistance(here, i)
			if newCost < cost:
				cost = newCost
				city = i
	return city

#move around in two directions to next closests
#input random startCity
def setTwoGreedyRoute(startCity):
	global v
	route = []
	front, back = getTwoClosest(startCity)
	v[startCity] = 1
	v[front] = 1
	v[back] = 1
	route.extend((startCity, front, back))
	insrt = 2
	count = 3
	while count < n:
		nextFront = getClosest(front)
		if nextFront < 0:
			break
		else:
			v[nextFront] = 1
		route.insert(insrt, nextFront)
		front = nextFront
		count += 1
		if count >= n:
			break
		insrt += 1
		nextBack = getClosest(back)
		if nextBack < 0:
			break
		else:
			v[nextBack] = 1
		route.insert(insrt, nextBack)
		back = nextBack
		count += 1
	#route complete
	v = [0]*len(v)
	
	calcRouteCost(route)
	checkForBest(route)
	go(route)

	return

#sets a basic greedy/nearest neighbour route - not using currently
def setGreedyRoute(startCity):
	route = fillRoute()
	swapCities(route, startCity, 0)
	i = 1
	while i < n:
		nextCity = i
		j = i
		while j < n:
			if getCityDistance(i-1, j) < getCityDistance(i-1, nextCity):
				nextCity = j
			j += 1
		swapCities(route, i, nextCity)
		i += 1
	calcRouteCost(route)
	checkForBest(route)
	go(route)
	return

#creates totally random route
def setRandomRoute():
	#create copy of cid list
	allCities = list(cid)
	route = []
	routeCount = 0
	while routeCount < n:
		addCity = choice(allCities)
		allCities.remove(addCity)
		route.append(addCity)
		routeCount += 1
	calcRouteCost(route)
	checkForBest(route)
	go(route)

	return	

#annealing function
def go(route):
	while temperature > tempEnd:
		lookForBestRoute(route)
	return

#do the annealing
def lookForBestRoute(route):
	global temperature
	x, y = pickTwoRandomCities()
	originalDistance = routeDistance
	swapCities(route, x, y)
	calcRouteCost(route)
	boolKeepRoute = keepNewRoute(originalDistance)
	if boolKeepRoute:
		checkForBest(route)
	else:
		swapCities(route, x, y)
		setDistance(originalDistance)
	temperature -= 1
	return

#helper function for small n values - not used
def getLowestTwoGreedyRoute():
	twoGreedyList = []
	loop = 0
	while loop < n:
		setTwoGreedyRouteOnly(loop)
		tup = (routeDistance, loop)
		twoGreedyList.append(tup)
		loop += 1
	twoGreedyList.sort(key=lambda tup: tup[0])
	return twoGreedyList

#sig handler for watch.py
def sig_term(num, frame):
	outputFunction(argv[1])
	exit()

#main
startClock = clock()
try:
	getCities(argv[1])
except IndexError:
	print "Please give an input file."
	exit(1)

#start signal handler
signal.signal(signal.SIGTERM, sig_term)

#do tsp work - includes some feedback timing commented out for clean running
while 1:
	try:
		randomStart = pickRandomCity()
		#include randomness on smallish city numbers
		#remove it otherwise
		if n < 2500:
			roll = random()
		else:
			roll = .01

		if roll < .60:
			setTwoGreedyRoute(randomStart)
		elif roll < .75:
			setGreedyRoute(randomStart)
		else:	
			setRandomRoute()
		
		temperature = int(tempStart)
		stopClock = clock()
		print "Reset", stopClock - startClock, "Roll -", "%.2f" % roll
	except KeyboardInterrupt:
		outputFunction(argv[1])
		if n < 500:
			print '\n', bestDistance, bestRoute
		exit()		

"""
note: known issue exists where code can fail validation if a keyboard interrupt occurs quickly,
usually before the first reset.  The smaller the number of cities, the shorter this time lasts,
but this can occur for some time if the city set is large enough (like test case 3). This can 
cause validation to fail, even though all the methods produce accurate results (tested ad nauseum). 
Letting the program run for a longer period of time eliminates this error. This error could not be 
reproduced without the KeyboardInterrupt which has been kept for ease of use.
"""

exit()