#!/usr/bin/env python

import argparse
from Config import conf
import os
from os.path import isdir, isfile, join
import json
import sys
import re
from Util import decisionID

def initParser():
    parser = argparse.ArgumentParser(description='Generate the results file for the exhaustive exploration.')
    parser.add_argument('-version', default=conf.defaultResultsVersion, required=False, help='The version of the results')
    return parser.parse_args()

args = initParser()

path = os.path.dirname(os.path.realpath(__file__))

def plot(file, legend):
    with open(join(path, file)) as data_file:
        data = json.load(data_file)

        output = """
            \\begin{tikzpicture}
                \\begin{axis}[
                    xlabel={Laps},
                    xmin=1, xmax=%d,
                    ymin=0, ymax=100,
                    ytick={0,20,40,60,80,100},
                    legend pos=north east,
                    ymajorgrids=true,
                    grid style=dashed,
                    smooth,
                    axis lines=left
                ]
""" % len(data['executions'])

        countDecision = 0;
        countPassedExecution = 0;
        usedDecisions = {};
        index = 1
        outputPassed = ""
        outputSearch = ""
        outputLean = ""
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
            outputPassed += "(%d,%d) " % (index, countPassedExecution*100/(len(data['executions'])))
            outputSearch += "(%d,%d) " % (index, len(usedDecisions)*100/(len(data['searchSpace'])))
            outputLean += "(%d,%d) " % (index, countPassedExecution*100/(index))
            index += 1
        output += "\n               \\addplot[color=primary] coordinates {%s};" % outputPassed
        if legend:
            output +=" \\addlegendentry{Nb correct Laps}"
        output += "\n               \\addplot[color=secondary] coordinates {%s};" % outputSearch
        if legend:
            output +=" \\addlegendentry{\\% Explored Decision}"
        output += "\n               \\addplot[color=tertiary] coordinates {%s};" % outputLean
        if legend:
            output +=" \\addlegendentry{\\% Correct Laps}"
        output += """
                \end{axis}
            \end{tikzpicture}"""
    return output

if len(sys.argv) > 1:
    file_name = sys.argv[1]
    print plot(file_name, True)
else:
    resultsPath = join(conf.resultsFolder, args.version, "bandit_exploration")
    with open(join(resultsPath, "results.json")) as data_file:
        resultsData = (json.load(data_file))
        sortedResultsData = sorted(resultsData)
        for bug in sortedResultsData:
            if bug != "lang587":
                continue
            bugTitle = bug.title().replace("-","")
            titleSplit = re.compile("([0-9]+)").split(bugTitle)
            bugTitle = "-".join(titleSplit[0:2]) + "".join(titleSplit[2::])
            output = """
\\begin{figure*}
\\caption{%s} 
\\label{plot:%s}""" % (bugTitle, bug)
            epsilons = sorted(resultsData[bug])
            for epsilon in epsilons:
                if epsilon not in ["0.2", "0.5", "0.8"]:
                    continue
                seeds = sorted(resultsData[bug][epsilon])
                for seed in seeds:
                    if seed != "10":
                        continue
                    output += """
    \\begin{subfigure}[b]{0.32\\textwidth}
        \\centering
        \\resizebox{\\linewidth}{!}{"""
                    executionsPath = join(resultsPath, bug, str(resultsData[bug][epsilon][seed]) + ".json")
                    output += plot(executionsPath, "0.8" == epsilon)
                    output += """
            }
        \\caption{Epsilon %s}
        \\label{fig:%s%s%s}
    \\end{subfigure}""" % (epsilon, bug, epsilon, seed)
            output += """
\\end{figure*}"""
            print output
