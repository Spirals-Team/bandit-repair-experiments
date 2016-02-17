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
    parser = argparse.ArgumentParser(description='Generate the latex table for the Bandit exploration.')
    parser.add_argument('-version', default=conf.defaultResultsVersion, required=False, help='The version of the results')
    parser.add_argument('-epsilons', nargs='+', default=["0", "1", "0.2", "0.8"], required=False, help='The list of displayed epsilon.')
    return parser.parse_args()

args = initParser()

resultsPath = join(conf.resultsFolder, args.version, "bandit_exploration")
with open(join(resultsPath, "results.json")) as data_file:
    resultsData = (json.load(data_file))
    sortedResultsData = sorted(resultsData)
    average = {}
    for bug in sortedResultsData:
        bugTitle = bug.title().replace("-","")
        titleSplit = re.compile("([0-9]+)").split(bugTitle)
        bugTitle = "-".join(titleSplit[0:2]) + "".join(titleSplit[2::])
        print "\multirow{%d}{*}{%s}" % (len(args.epsilons), bugTitle)
        epsilons = sorted(resultsData[bug])
        for epsilon in epsilons:
            if epsilon not in args.epsilons:
                continue
            seedExploredDecisions = []
            seedExploredSeqDecisions = []
            seedExploredLocations = []
            seedMinSizeCorrectSeqDecisions = []
            seedMaxSizeCorrectSeqDecisions = []
            seedMedSizeCorrectSeqDecisions = []
            seedMinFailureSeqDecisions = []
            seedMaxFailureSeqDecisions = []
            seedMedFailureSeqDecisions = []
            seedNbPassedSeqLaps = []
            seedNbBeforeStabilization = []
            seedNbBeforeSuccess = []
            seedCountPassedLaps = []
            seedNbLaps = []
            seedCountPassedLaps = []
            seedNbBeforeMaxExploration = []

            seeds = sorted(resultsData[bug][epsilon])
            for seed in seeds:
                if epsilon not in average:
                    average[epsilon] = {
                        "nbBeforeStabilization": [],
                        "nbBeforeSuccess": [],
                        "nbPassedSeqLaps": [],
                        "nbExploredDecision": [],
                        "nbExploredSeqDecision": [],
                        "nbExploredLocation": [],
                        "nbDetectedDecision": [],
                        "nbLaps": [],
                        "minSizeCorrectSeqDecision": [],
                        "maxSizeCorrectSeqDecision": [],
                        "medSizeCorrectSeqDecision": [],
                        "minSizeFailureSeqDecision": [],
                        "maxSizeFailureSeqDecision": [],
                        "medSizeFailureSeqDecision": [],
                        "countPassedLaps": [],
                        "nbBeforeMaxExploration": []
                    }
                executionsPath = join(resultsPath, bug, str(resultsData[bug][epsilon][seed]) + ".json")
                with open(executionsPath) as data_file:
                    data = json.load(data_file)

                    nbBeforeSuccess = -1
                    nbBeforeStabilization = -1
                    countPassedLaps = 0
                    nbPassedSeqLaps = 0;
                    maxExploredDecision = 0
                    nbLapsBeforeMaxDecision = 0

                    index = 0

                    nbDetectedDecision = []
                    exploredDecisions = {}
                    exploredSeqDecisions = {}
                    exploredLocations = {}
                    learns = []
                    sizeCorrectSeqDecisions = []
                    sizeFailureSeqDecisions = []

                    for execution in data['executions']:
                        if 'decisions' not in execution:
                            continue
                        if execution['result']['success']:
                            if nbBeforeSuccess == -1:
                                nbBeforeSuccess = index + 1
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

                        learn = countPassedLaps*100/(index)
                        learns += [learn]
                        if len(learns) >= 8 and nbBeforeStabilization == -1 and learn != 0:
                            minLearn = len(data['executions'])
                            maxLearn = 0
                            for learn in learns[index - 8::]:
                                if learn > maxLearn:
                                    maxLearn = learn
                                if learn < minLearn:
                                    minLearn = learn
                            diffLearn = maxLearn - minLearn
                            if diffLearn <= 5:
                                nbBeforeStabilization = index - 7

                        if len(exploredDecisions) > maxExploredDecision:
                            maxExploredDecision = len(exploredDecisions)
                            nbLapsBeforeMaxDecision = index + 1
                        

                    if len(sizeCorrectSeqDecisions) is not 0:
                        seedMinSizeCorrectSeqDecisions += [min(sizeCorrectSeqDecisions)]
                        seedMaxSizeCorrectSeqDecisions += [max(sizeCorrectSeqDecisions)]
                        seedMedSizeCorrectSeqDecisions += [med(sizeCorrectSeqDecisions)]
                    if len(sizeFailureSeqDecisions) is not 0:
                        seedMinFailureSeqDecisions += [min(sizeFailureSeqDecisions)]
                        seedMaxFailureSeqDecisions += [max(sizeFailureSeqDecisions)]
                        seedMedFailureSeqDecisions += [med(sizeFailureSeqDecisions)]
                    if nbBeforeSuccess != -1:
                        seedNbBeforeSuccess += [nbBeforeSuccess]
                    if nbBeforeStabilization != -1:
                        seedNbBeforeStabilization += [nbBeforeStabilization]

                    seedNbBeforeMaxExploration += [nbLapsBeforeMaxDecision]
                    seedCountPassedLaps += [countPassedLaps]
                    seedNbPassedSeqLaps += [nbPassedSeqLaps]
                    seedExploredDecisions += [len(exploredDecisions)]
                    seedExploredSeqDecisions += [len(exploredSeqDecisions)]
                    seedExploredLocations += [len(exploredLocations)]
                    nbDetectedDecision += [len(data['searchSpace'])]
                    seedNbLaps += [index]

            if len(seedNbBeforeSuccess) is not 0:
                average[epsilon]['nbBeforeSuccess'] += [med(seedNbBeforeSuccess)]
            if len(seedNbBeforeStabilization) is not 0:
                average[epsilon]['nbBeforeStabilization'] += [med(seedNbBeforeStabilization)]
            average[epsilon]['nbPassedSeqLaps'] += [med(seedNbPassedSeqLaps)]
            average[epsilon]['nbDetectedDecision'] += [med(nbDetectedDecision)]
            average[epsilon]['nbExploredDecision'] += [med(seedExploredDecisions)]
            average[epsilon]['nbExploredSeqDecision'] += [med(seedExploredSeqDecisions)]
            average[epsilon]['nbExploredLocation'] += [med(seedExploredLocations)]
            average[epsilon]['countPassedLaps'] += [med(seedCountPassedLaps)]
            average[epsilon]['nbBeforeMaxExploration'] += [med(seedNbBeforeMaxExploration)]

            average[epsilon]['minSizeCorrectSeqDecision'] += seedMinSizeCorrectSeqDecisions
            average[epsilon]['maxSizeCorrectSeqDecision'] += seedMaxSizeCorrectSeqDecisions
            average[epsilon]['medSizeCorrectSeqDecision'] += seedMedSizeCorrectSeqDecisions

            average[epsilon]['minSizeFailureSeqDecision'] += seedMinFailureSeqDecisions
            average[epsilon]['maxSizeFailureSeqDecision'] += seedMaxFailureSeqDecisions
            average[epsilon]['medSizeFailureSeqDecision'] += seedMedFailureSeqDecisions

            average[epsilon]['nbLaps'] += [med(seedNbLaps)]

            print " & $%.1f$   & %s & %s & %s & %s & %s & %s  \\\\" % (
                1 - float(epsilon),
                numToStr(med(seedExploredLocations)),
                #numToStr(med(nbDetectedDecision)),
                #numToStr(med(seedExploredDecisions)),
                numToStr(med(seedExploredSeqDecisions)),
                numToStr(med(seedNbPassedSeqLaps)),
                numToStr(med(seedCountPassedLaps)),
                numToStr(med(seedNbBeforeMaxExploration)),
                numToStr(med(seedNbBeforeStabilization)),
                #numToStr(med(seedMinSizeCorrectSeqDecisions)),
                #numToStr(med(seedMedSizeCorrectSeqDecisions)),
                #numToStr(med(seedMaxSizeCorrectSeqDecisions)),
                #numToStr(med(seedMinFailureSeqDecisions)),
                #numToStr(med(seedMedFailureSeqDecisions)),
                #numToStr(med(seedMaxFailureSeqDecisions))
                )
        print "\\hline"
    print "\\hline"
    print "\multirow{3}{*}{Average}"
    for epsilon in sorted(average):
        print " & $%.1f$   & %s & %s & %s & %s & %s & %s  \\\\" % (
                    1 - float(epsilon),
                    numToStr(avg(average[epsilon]['nbExploredLocation'])),
                    #numToStr(avg(average[epsilon]['nbDetectedDecision'])),
                    #numToStr(avg(average[epsilon]['nbExploredDecision'])),
                    numToStr(avg(average[epsilon]['nbExploredSeqDecision'])),
                    numToStr(avg(average[epsilon]['nbPassedSeqLaps'])),
                    numToStr(avg(average[epsilon]['countPassedLaps'])),
                    numToStr(avg(average[epsilon]['nbBeforeMaxExploration'])),
                    numToStr(avg(average[epsilon]['nbBeforeStabilization']))
                    #numToStr(avg(average[epsilon]['minSizeCorrectSeqDecision'])),
                    #numToStr(avg(average[epsilon]['medSizeCorrectSeqDecision'])),
                    #numToStr(avg(average[epsilon]['maxSizeCorrectSeqDecision'])),
                    #numToStr(avg(average[epsilon]['minSizeFailureSeqDecision'])),
                    #numToStr(avg(average[epsilon]['medSizeFailureSeqDecision'])),
                    #numToStr(avg(average[epsilon]['maxSizeFailureSeqDecision']))
                    )
    print "\\hline"
    print "\multirow{3}{*}{Total}"
    for epsilon in sorted(average):
        print " & $%.1f$   & %s & %s & %s & %s & %s & %s  \\\\" % (
                    1 - float(epsilon),
                    numToStr(sum(average[epsilon]['nbExploredLocation'])),
                    #numToStr(sum(average[epsilon]['nbDetectedDecision'])),
                    #numToStr(sum(average[epsilon]['nbExploredDecision'])),
                    numToStr(sum(average[epsilon]['nbExploredSeqDecision'])),
                    numToStr(sum(filter(lambda x: x is not None,average[epsilon]['nbPassedSeqLaps']))),
                    numToStr(sum(filter(lambda x: x is not None,average[epsilon]['countPassedLaps']))),
                    numToStr(sum(filter(lambda x: x is not None,average[epsilon]['nbBeforeMaxExploration']))),
                    numToStr(sum(filter(lambda x: x is not None,average[epsilon]['nbBeforeStabilization'])))
                    #numToStr(min(filter(lambda x: x is not None,average[epsilon]['minSizeCorrectSeqDecision']))),
                    #numToStr(med(average[epsilon]['medSizeCorrectSeqDecision'])),
                    #numToStr(max(filter(lambda x: x is not None,average[epsilon]['maxSizeCorrectSeqDecision']))),
                    #numToStr(min(filter(lambda x: x is not None,average[epsilon]['minSizeFailureSeqDecision']))),
                    #numToStr(med(average[epsilon]['medSizeFailureSeqDecision'])),
                    #numToStr(max(filter(lambda x: x is not None,average[epsilon]['maxSizeFailureSeqDecision'])))
                    )
    print "\\hline"