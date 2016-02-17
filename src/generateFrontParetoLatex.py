#!/usr/bin/env python

import argparse
from Config import conf
from Util import isNaN, avg, decisionID, locationID, med, numToStr
import os
from os import listdir
from os.path import isdir, isfile, join
import json
import numpy
import re
import sys

def initParser():
    parser = argparse.ArgumentParser(description='Generate the results file for the exhaustive exploration.')
    parser.add_argument('-version', default=conf.defaultResultsVersion, required=False, help='The version of the results')
    return parser.parse_args()

args = initParser()

path = join(conf.resultsFolder, args.version, "bandit_exploration")

def plot(bugName, bug):
    output = """        \\begin{tikzpicture}
            \\begin{axis}[
                enlargelimits=false,
                xmin=1,xmax=200,
                ymin=0,ymax=100,
                ytick={0,10,20,30,40,50,60,70,80,90,100},
                ymajorgrids=true,
                grid style=dashed,
                smooth,
                axis lines=left,
                legend pos=outer north east,
                ylabel={\\% Correct Laps},
                xlabel={Nb Laps Before Max Explored Decision},
                ]
"""
    #ylabel={Nb Laps Before Stabilization},
    epsilons = sorted(bug)
    for epsilon in epsilons:
        if "%.1f" % float(epsilon) == "0.0":
            continue
        coordinates = ""
        seeds = sorted(bug[epsilon])
        for seed in seeds:            
            executionsPath = join(path, bugName, str(bug[epsilon][seed]) + ".json")
            with open(executionsPath) as data_file:    
                data = json.load(data_file)

                index = 0

                countPassedLaps = 0
                nbBeforeStabilization = -1 
                exploredDecisions = {}
                exploredSeqDecisions = {}
                exploredLocations = {}
                learns = []
                sizeCorrectSeqDecisions = []
                sizeFailureSeqDecisions = []

                maxExplredDecision = 0
                nbLapsBeforeMaxDecision = 0
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

                    # learning curve
                    learn = countPassedLaps*100/(index + 1)
                    learns += [learn]
                    if len(learns) >= 10 and nbBeforeStabilization == -1 and learn != 0:
                        minLearn = 100
                        maxLearn = 0
                        for learn in learns[index - 9::]:
                            if learn > maxLearn:
                                maxLearn = learn
                            if learn < minLearn:
                                minLearn = learn
                        diffLearn = maxLearn - minLearn
                        if diffLearn <= 4:
                            nbBeforeStabilization = index - 9

                    if len(exploredDecisions) > maxExplredDecision:
                        maxExplredDecision = len(exploredDecisions)
                        nbLapsBeforeMaxDecision = index + 1

                    index += 1
                #print seed, epsilon, nbLapsBeforeMaxDecision, nbBeforeStabilization
                coordinates += "(%d,%d) " % (nbLapsBeforeMaxDecision, countPassedLaps*100/len(data['executions']))
        output += "                \\addplot+[only marks] coordinates {%s};" % coordinates
        output +="    \\addlegendentry{\\exploitationCoefficient %.1f}\n" % (1 - float(epsilon))
    output += """           \end{axis}
        \end{tikzpicture}"""
    return output

if len(sys.argv) > 1:
    file_name = sys.argv[1]
    print plot(file_name, True)
else:
    resultsPath = join(path, "results.json")
    with open(resultsPath) as data_file: 
        resultsData = (json.load(data_file))
        sortedResultsData = sorted(resultsData)
        for bug in sortedResultsData:
            if bug != "lang587":
                continue
            bugTitle = bug.title().replace("-","")
            titleSplit = re.compile("([0-9]+)").split(bugTitle)
            bugTitle = "-".join(titleSplit[0:2]) + "".join(titleSplit[2::])
            output = """\\begin{figure}[t]
    \\centering
    \\resizebox{\linewidth}{!}{
""" 
            output += plot(bug, resultsData[bug])
            output += """
    }
    \\caption{Front Pareto: %s better view on screen or with color printing.} 
    \\label{plot:exploitation-%s}""" % (bugTitle, bug)
            output += """
\\end{figure}"""
            print output
