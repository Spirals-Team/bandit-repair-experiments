#!/usr/bin/env python

import argparse
from Config import conf
import os
from os.path import isdir, isfile, join
import json
import sys
import re
import matplotlib
matplotlib.use('Agg') # Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt

def decisionID(decision):
    output = decision['strategy'];
    if 'variableName' in decision['value'] :
        output += decision['value']['variableName']
    output += "[" + decision['value']['type']
    output +=  decision['value']['value']
    output += "at " + decision['location']['class']
    output += ":%d" % decision['location']['line']
    output += "(%d" % decision['location']['sourceEnd']
    output += "%d" % decision['location']['sourceStart']
    return output

path = os.path.dirname(os.path.realpath(__file__))

def plot(file, bug, seed, epsilon):
    with open(join(path, file)) as data_file:    
        data = json.load(data_file)

        countDecision = 0;
        countPassedExecution = 0;
        usedDecisions = {};
        index = 1
        xPassed = []
        yPassed = []
        xSearch = []
        ySearch = []
        xLearn = []
        yLearn = []
        fig = plt.figure()
        
        for execution in data['executions']:
            if 'decisions' not in execution:
                continue
            if execution['result']['success']:
                countPassedExecution += 1
            for decision in execution['decisions']:
                dID = decisionID(decision)
                if dID not in usedDecisions:
                    usedDecisions[dID] = 0
                usedDecisions[dID] += 1
            xPassed += [index]
            xSearch += [index]
            xLearn += [index]
            yPassed += [int(countPassedExecution*100/(len(data['executions'])))]
            ySearch += [int(len(usedDecisions)*100/(len(data['searchSpace'])))]
            yLearn += [int(countPassedExecution*100/(index))]

            index += 1
        plt.plot(xPassed, yPassed, color='#afeeee', label='Nb Passed')
        plt.plot(xSearch, ySearch, color='#333333', label='% Explored Decision')
        plt.plot(xLearn, yLearn, color='#999999', label='% Passed')
        plt.xlabel('Laps ID')
        plt.legend(loc='lower right', shadow=False , fontsize='small')
        plt.ylim(ymin=0, ymax=100)
        plt.xlim(xmin=0, xmax=max([200, len(data['executions'])]))
        fig.savefig("%s_%s_%.2f.svg" % (bug, seed, float(epsilon)))
        plt.close()

if len(sys.argv) > 1:
    file_name = sys.argv[1]
    print plot(file_name, True)
else:
    resultsPath = join(path, "www/data/results2.json")
    with open(resultsPath) as data_file: 
        resultsData = (json.load(data_file))
        sortedResultsData = sorted(resultsData)
        for bug in sortedResultsData:
            bugTitle = bug.title().replace("-","")
            titleSplit = re.compile("([0-9]+)").split(bugTitle)
            bugTitle = "-".join(titleSplit[0:2]) + "".join(titleSplit[2::])
            print bugTitle
            epsilons = sorted(resultsData[bug])
            for epsilon in epsilons:
                seeds = sorted(resultsData[bug][epsilon])
                for seed in seeds:    
                    executionsPath = join(path, "GreedySelector", bug, str(resultsData[bug][epsilon][seed]) + ".json")
                    plot(executionsPath, bug, seed, epsilon)
