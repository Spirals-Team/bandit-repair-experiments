import numpy

def isNaN(num):
    return num != num

def med(lst):
    return numpy.median(numpy.array(lst))

def avg(lst):
	if len(lst) == 0 or lst is None:
		return None
	return sum(filter(lambda x: x is not None, lst))/float(len(lst))

def locationID(location):
	output = location['class']
	output += ":%d" % location['line']
	output += "(%d" % location['sourceEnd']
	output += "%d" % location['sourceStart']
	return output

def decisionID(decision):
	output = decision['strategy'];
	if 'variableName' in decision['value'] :
		output += decision['value']['variableName']
	output += "[" + decision['value']['type']
	output +=  decision['value']['value']
	output += "at " + locationID(decision['location'])
	return output

def numToStr(num, size=6):
	if num is None or isNaN(num):
		form = "{:^"+str(size)+"}"
		return form.format("---")
	if num == int(num):
		form = "{:"+str(size)+"d}"
		return form.format(int(num))
	form = "{:"+str(size)+".2f}"
	return form.format(num)