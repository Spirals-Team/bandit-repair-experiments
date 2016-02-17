#!/usr/bin/env python

import argparse
from Config import conf
from Util import isNaN, avg, decisionID, locationID, med, numToStr
import os
from os import listdir
from os.path import isdir, isfile, join
import json
import re

def initParser():
    parser = argparse.ArgumentParser(description='Generate the latex table for the Exhaustive exploration.')
    parser.add_argument('-version', default=conf.defaultResultsVersion, required=False, help='The version of the results')
    return parser.parse_args()

args = initParser()

resultsPath = join(conf.resultsFolder, args.version, "exhaustive_exploration")
with open(join(resultsPath, "results.json")) as data_file:   
	resultsData = (json.load(data_file))
	sortedResultsData = sorted(resultsData)
	average = {
		"nbPassedSeqLaps": [],
		"nbExploredDecision": [],
		"nbExploredSeqDecision": [],
		"nbExploredLocation": [],
		"nbDetectedDecision": [],
		"totalSize": [],
		"minSizeCorrectSeqDecision": [],
		"maxSizeCorrectSeqDecision": [],
		"medSizeCorrectSeqDecision": [],
		"minSizeFailureSeqDecision": [],
		"maxSizeFailureSeqDecision": [],
		"medSizeFailureSeqDecision": []
	}
	for bug in sortedResultsData:
		bugTitle = bug.title().replace("-","")
		titleSplit = re.compile("([0-9]+)").split(bugTitle)
		bugTitle = "-".join(titleSplit[0:2]) + "".join(titleSplit[2::])
		executionsPath = join(resultsPath, bug, str(resultsData[bug]) + ".json")
		with open(executionsPath) as data_file:
			data = json.load(data_file)
			countPassedLaps = 0
			nbPassedSeqLaps = 0;

			index = 0

			nbDetectedDecision = []
			exploredDecisions = {}
			exploredSeqDecisions = {}
			exploredLocations = {}
			sizeCorrectSeqDecisions = []
			sizeFailureSeqDecisions = []

			for execution in data['executions']:
				if 'decisions' not in execution:
					continue
				if execution['result']['success']:
					countPassedLaps += 1
				sID = ""
				for decision in execution['decisions']:
					lID = locationID(decision['location'])
					if lID not in exploredLocations:
						exploredLocations[lID] = 0
					exploredLocations[lID] += 1

					dID = decisionID(decision)
					sID += dID
					if dID not in exploredDecisions:
						exploredDecisions[dID] = 0
					exploredDecisions[dID] += 1

				if sID not in exploredSeqDecisions:
					exploredSeqDecisions[sID] = 0
					if execution['result']['success']:
						nbPassedSeqLaps += 1
				exploredSeqDecisions[sID] += 1

				if execution['result']['success']:
					sizeCorrectSeqDecisions += [len(execution['decisions'])]
				else:
					sizeFailureSeqDecisions += [len(execution['decisions'])]

				index += 1

				
			average['nbPassedSeqLaps'] += [nbPassedSeqLaps]
			average['nbDetectedDecision'] += [len(data['searchSpace'])]
			average['nbExploredDecision'] += [len(exploredDecisions)]
			average['nbExploredLocation'] += [len(exploredLocations)]
			average['totalSize'] += [len(data['executions'])]

			if len(sizeCorrectSeqDecisions) > 0:
				average['minSizeCorrectSeqDecision'] += [min(sizeCorrectSeqDecisions)]
				average['maxSizeCorrectSeqDecision'] += [max(sizeCorrectSeqDecisions)]
				average['medSizeCorrectSeqDecision'] += [med(sizeCorrectSeqDecisions)]

			if len(sizeFailureSeqDecisions) > 0:
				average['minSizeFailureSeqDecision'] += [min(sizeFailureSeqDecisions)]
				average['maxSizeFailureSeqDecision'] += [max(sizeFailureSeqDecisions)]
				average['medSizeFailureSeqDecision'] += [med(sizeFailureSeqDecisions)]

			print "%s & %s & %s & %s & %s & %s & %s & %s & %s & %s  \\\\" % (
				"{:15}".format(bugTitle),
				numToStr(len(exploredLocations)),
				numToStr(len(data['executions'])),
				numToStr(nbPassedSeqLaps),
				numToStr(min(sizeCorrectSeqDecisions) if len(sizeCorrectSeqDecisions) > 0 else None),
				numToStr(med(sizeCorrectSeqDecisions) if len(sizeCorrectSeqDecisions) > 0 else None),
				numToStr(max(sizeCorrectSeqDecisions) if len(sizeCorrectSeqDecisions) > 0 else None),
				numToStr(min(sizeFailureSeqDecisions) if len(sizeFailureSeqDecisions) > 0 else None),
				numToStr(med(sizeFailureSeqDecisions) if len(sizeFailureSeqDecisions) > 0 else None),
				numToStr(max(sizeFailureSeqDecisions) if len(sizeFailureSeqDecisions) > 0 else None)
				)
	print "\\hline"
	print "Total           & %s & %s & %s & %s & %s & %s & %s & %s & %s  \\\\" % (
				numToStr(sum(average['nbExploredLocation'])),
				numToStr(sum(filter(lambda x: x is not None,average['totalSize']))),
				numToStr(sum(average['nbPassedSeqLaps'])),
				numToStr(min(filter(lambda x: x is not None,average['minSizeCorrectSeqDecision']))),
				numToStr(med(average['medSizeCorrectSeqDecision'])),
				numToStr(max(filter(lambda x: x is not None,average['maxSizeCorrectSeqDecision']))),
				numToStr(min(filter(lambda x: x is not None,average['minSizeFailureSeqDecision']))),
				numToStr(med(average['medSizeFailureSeqDecision'])),
				numToStr(max(filter(lambda x: x is not None,average['maxSizeFailureSeqDecision']))))
	print "\\hline"