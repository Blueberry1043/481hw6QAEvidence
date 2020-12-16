import os
import subprocess
from random import randint
from subprocess import Popen, PIPE, STDOUT
import math
import copy
import sys


# Tests the given seedless input logs on the pokemonshowdown simulator. Runs the input logs
# multiple times, recording the results to see if the ordering of certain events are deterministic
def main():
	test_primal(5)
	test_entrance(5)


entrance_input_log = '''
>version 045fe4560980ea53a7763c2ebc8c584bb1ef3f53
>start {"formatid":"gen7doublescustomgame"}
>player p1 {"name":"Zamazzenta","avatar":"1","team":"Tapu Koko||||explosion|||||||]Tapu Bulu||||explosion||,,,,,80|||||]Tapu Fini||||explosion|||||||]Tapu Lele||||explosion|||||||","rating":0}
>player p2 {"name":"AldrichYan","avatar":"archie-gen3","team":"Tapu Bulu||||explosion||,,,,,80|||||]Tapu Fini||||explosion|||||||]Tapu Koko||||explosion|||||||]Tapu Lele||||explosion|||||||","rating":0}
>p1 team 1, 4, 3, 2
>p2 team 1, 2, 3, 4
>p1 move explosion, move explosion
>p2 move explosion, move explosion
>p1 switch 4, switch 3
>p2 switch 3, switch 4
>p1 move explosion, move explosion
>p2 move explosion, move explosion
'''

primal_input_log = '''
>version 61a3c6f2492a129b9f83fe559d28a432b6a583fd
>start {"formatid":"gen7doublescustomgame"}
>player p1 {"name":"AldrichYan","avatar":"archie-gen3","team":"1|kyogre|blueorb||explosion|Serious|||||50|]2|groudon|redorb||explosion|Serious|||||50|]3|kyogre|blueorb||explosion|Serious|||||50|]4|groudon|redorb||explosion|Serious|||||50|]5|kyogre|blueorb||explosion|Serious|||||50|]6|groudon|redorb||explosion|Serious|||||50|","rating":0}
>player p2 {"name":"Zamazzenta","avatar":"265","team":"7|kyogre|blueorb||explosion|Serious|||||50|]8|groudon|redorb||explosion|Serious|||||50|]9|kyogre|blueorb||explosion|Serious|||||50|]10|groudon|redorb||explosion|Serious|||||50|]11|kyogre|blueorb||explosion|Serious|||||50|]12|groudon|redorb||explosion|Serious|||||50|","rating":0}
>p1 team 1, 2, 3, 4, 5, 6
>p2 team 1, 2, 3, 4, 5, 6
>p1 move explosion, move explosion
>p2 move explosion, move explosion
>p1 switch 3, switch 4
>p2 switch 3, switch 4
>p1 move explosion, move explosion
>p2 move explosion, move explosion
>p1 switch 5, switch 6
>p2 switch 5, switch 6
>p1 move explosion, move explosion
>p2 move explosion, move explosion
'''

test_input = '''
>start {"formatid":"gen7randombattle"}
>player p1 {"name":"Alice"}
>player p2 {"name":"Bob"}
'''

# Run the primal input log nAttempts times to see if the ordering is deterministic
def test_primal(nAttempts):
	# Run the simulator once and record results
	simulator = subprocess.Popen(['./pokemon-showdown','simulate-battle'],stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf8')
	output = simulator.communicate(input=primal_input_log)[0]
	# There are 3 instances where pokemon are switched in. Record the ordering of the positions that become
	# primal for each turn start
	[aFirst, aSecond, aThird] = parse_primal_output(output)
	print([aFirst, aSecond, aThird])
	firstdiff = False
	seconddiff = False
	thirddiff = False
	for i in range(0,nAttempts - 1):
		# Run the simulator and record results
		simulator = subprocess.Popen(['./pokemon-showdown','simulate-battle'],stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf8')
		output = simulator.communicate(input=primal_input_log)[0]
		[sampleFirst, sampleSecond, sampleThird] = parse_primal_output(output)
		print([sampleFirst, sampleSecond, sampleThird])
		if sampleFirst != aFirst:
			firstdiff = True
		if sampleSecond != aSecond:
			seconddiff = True
		if sampleThird != aThird:
			thirddiff = True
			# Exit if we see each event have different orderings
		if firstdiff and seconddiff and thirddiff:
			print("We have observed different orderings for all instances of primal reversions",end='\n\n')
			return
	print("We did not see differing orderings for primal reversions. Probability that a single ordering occurred", nAttempts, "times: ",end='')
	probablity = pow(1/4, nAttempts) * 100
	print(probablity, "%", sep='')

# Takes simulator output log, returns list of three lists
# each sublist contains the positions of pokemon to turn primal in the order
# they turned primal
def parse_primal_output(output):
	aLines = output.split('\n')
	aRet = []
	aFirst = []
	aSecond = []
	aThird = []
	count = 0
	for line in aLines:
		aWords = line.split()
		if aWords and aWords[0].startswith('|-primal|'):
			if count < 4:
				aFirst.append(aWords[0].replace('|-primal|',''))
			elif count < 8:
				aSecond.append(aWords[0].replace('|-primal|',''))
			else:
				aThird.append(aWords[0].replace('|-primal|',''))
			count += 1
	aRet.append(aFirst)
	aRet.append(aSecond)
	aRet.append(aThird)
	return aRet

# Run the given sample input logs seedlessly nAttemps number of times and output whether we have demonstrably 
# seen nondeterministic tapu entrance ability ordering, otherwise print the probability it could still be deterministic
def test_entrance(nAttempts):
	# Run the simulator once and store results
	simulator = subprocess.Popen(['./pokemon-showdown','simulate-battle'],stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf8')
	output = simulator.communicate(input=entrance_input_log)[0]
	[aFirstOccurence, aSecondOccurence] = parse_entrance_output(output)
	print([aFirstOccurence, aSecondOccurence])
	firstdiff = False
	seconddiff = False
	for i in range(0,nAttempts - 1):
		# Run the server again and compare to the results from the first test
		simulator = subprocess.Popen(['./pokemon-showdown','simulate-battle'],stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf8')
		output = simulator.communicate(input=entrance_input_log)[0]
		[sampleFirst, sampleSecond] = parse_entrance_output(output)
		print([sampleFirst, sampleSecond])
		if sampleFirst != aFirstOccurence:
			firstdiff = True
		if sampleSecond != aSecondOccurence:
			seconddiff = True
		# If both entrance events 
		if firstdiff and seconddiff:
			print("We have observed different orderings for both instances of tapu entrances")
			return
	print("We did not see differing orderings for tapu entrances. Probability that a single ordering occurred", nAttempts, "times: ",end='')
	probablity = pow(1/2, nAttempts) * 100
	print(probablity, "%", sep='')


# Returns two arrays that are the order in which the entrance abilities occur
# for each instance of entrances
def parse_entrance_output(output):
	aLines = output.split('\n')
	if len(aLines) < 123:
		print("Error parsing output")
		exit()
	aRet = []
	aFirstEntrance = []
	aSecondEntrance = []
	count = 0
	for line in aLines:
		aWords = line.split()
		if aWords and aWords[0] == '|-fieldstart|move:':
			if count < 4:
				aFirstEntrance.append(aWords[1])
			else:
				aSecondEntrance.append(aWords[1])
			count += 1
	aRet.append(aFirstEntrance)
	aRet.append(aSecondEntrance)
	return aRet


if __name__ == '__main__':
    main()    

