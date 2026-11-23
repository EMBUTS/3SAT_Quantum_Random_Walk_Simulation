import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy


def readResults(alg,nMin,nMax):
    resultsList = []
    for n in range(nMin, nMax+1):
        df = pd.read_csv(f"results/{alg}_{n}.csv")
        if 'total_steps' not in df.columns:
            df['total_steps'] = df['steps']+df['steps_per_iter']*df['iters']
        resultsList.append(df)

    return resultsList

def plotStepFitGraph(source, type, steps, title):
    a,b = scipy.optimize.curve_fit(lambda t,a,b: a*(np.exp(b*t)), nrange, steps, p0=(4, 0.1))[0]
    fitSteps = a*(np.exp(b*range(algMax+1)))
    plt.title(f"{title} {type} Total Steps")
    plt.plot(nrange,steps)
    plt.plot(range(algMax+1),fitSteps, linestyle='--')
    plt.xlabel("n")
    plt.ylabel(f"{type} number of steps")
    plt.legend(["Simulated", rf"$y={a:.3f}e^{{{b:.3f}n}}$"])
    plt.tight_layout()
    # plt.show()
    plt.savefig(f"graphs/step_fit_{source}_{type}.pdf", dpi=200)
    plt.close()
    print(f"{title} {type} Fit: y = {a:.3f}*e^({b:.3f}n) = {a:.3f}*{np.exp(b):.3f}^n")

def plotPerAlgGraph(resultSet, isAvg, i):
    type = "Average" if isAvg else "Median"

    plt.title(f"\"{problemsets[i]}\" Problem Set - {type} Total Steps Per Algorithm")

    for alg in resultSet:
        algMin, algMax = alg["min"], alg["max"]
        nrange = range(algMin, algMax+1)
        steps = alg["averageSteps"] if isAvg else alg["medianSteps"]
        plt.plot(nrange,steps)
    plt.xlabel("n")
    plt.ylabel(f"{type} number of steps")
    plt.yscale('log')
    plt.legend(algorithms)
    plt.tight_layout()
    # plt.show()
    plt.savefig(f"graphs/per_alg_{problemsets[i]}_{type}.pdf", dpi=200)
    plt.close()

def plotPerSetGraph(resultSet, isAvg, i):
    
    type = "Average" if isAvg else "Median"
    plt.title(f"\"{algorithms[i]}\" - {type} Total Steps Per Problem Set")

    for alg in resultSet:
        algMin, algMax = alg["min"], alg["max"]
        nrange = range(algMin, algMax+1)
        steps = alg["averageSteps"] if isAvg else alg["medianSteps"]
        plt.plot(nrange,steps)
    plt.xlabel("n")
    plt.ylabel(f"{type} number of steps")
    plt.yscale('log')
    plt.legend(problemsets)
    plt.tight_layout()
    # plt.show()
    plt.savefig(f"graphs/per_pset_{algorithms[i]}_{type}.pdf", dpi=200)
    plt.close()

# Could these have been generated dynamically? Perhaps.
algDicts = [{"resultsName":"std_schoning",      "min":3, "max":30, "title": "Medium Schoning"},
            {"resultsName":"std_skw",           "min":3, "max":18, "title": "Medium SKW Search"},
            {"resultsName":"std_grover",        "min":3, "max":19, "title": "Medium Grover Search"},
            {"resultsName":"std_qschoning",     "min":3, "max":22, "title": "Medium Quantum Schoning"},
            {"resultsName":"hard_schoning",     "min":3, "max":30, "title": "Hard Schoning"},
            {"resultsName":"hard_skw",          "min":3, "max":17, "title": "Hard SKW Search"},
            {"resultsName":"hard_grover",       "min":3, "max":19, "title": "Hard Grover Search"},
            {"resultsName":"hard_qschoning",    "min":3, "max":22, "title": "Hard Quantum Schoning"},
            {"resultsName":"unique_schoning",   "min":3, "max":30, "title": "Unique Easy Schoning"},
            {"resultsName":"unique_skw",        "min":3, "max":18, "title": "Unique Easy SKW Search"},
            {"resultsName":"unique_grover",     "min":3, "max":19, "title": "Unique Easy Grover Search"},
            {"resultsName":"unique_qschoning",  "min":3, "max":22, "title": "Unique Easy Quantum Schoning"},
            {"resultsName":"uniquelin_schoning",    "min":3, "max":30, "title": "Unique Hard Schoning"},
            {"resultsName":"uniquelin_skw",         "min":3, "max":15, "title": "Unique Hard SKW Search"},
            {"resultsName":"uniquelin_grover",      "min":3, "max":19, "title": "Unique Hard Grover Search"},
            {"resultsName":"uniquelin_qschoning",   "min":3, "max":22, "title": "Unique Hard Quantum Schoning"}]

problemsets = ["Medium", "Hard", "Unique Easy", "Unique Hard"]
algorithms = ['Schoning','SKW','Grover','Quantum Schoning']

for alg in algDicts:
    algMin, algMax = alg["min"], alg["max"]
    results = readResults(alg["resultsName"],algMin,algMax)
    nrange = range(algMin, algMax+1)
    averageSteps = []
    medianSteps = []
    for result in results:
        totalSteps = result['total_steps']
        averageSteps.append(totalSteps.mean())
        medianSteps.append(totalSteps.median())
    alg["averageSteps"] = averageSteps
    alg["medianSteps"] = medianSteps

    plotStepFitGraph(alg["resultsName"], "Average", averageSteps, alg["title"])
    plotStepFitGraph(alg["resultsName"], "Median", medianSteps, alg["title"])

for i in range(4):
    resultSet = algDicts[i*4:i*4+4]
    plotPerAlgGraph(resultSet,True,i)
    plotPerAlgGraph(resultSet,False,i)

for i in range(4):
    resultSet = algDicts[i::4]
    plotPerSetGraph(resultSet,True,i)
    plotPerSetGraph(resultSet,False,i)



if False:
    algMin, algMax = 3, 19
    results = readResults("uniquelin_grover_unique_guarantee",algMin,algMax)
    nrange = range(algMin, algMax+1)
    averageSteps = []
    medianSteps = []
    for result in results:
        totalSteps = result['total_steps']
        averageSteps.append(totalSteps.mean())
        medianSteps.append(totalSteps.median())
    plotStepFitGraph("uniquelin_grover_unique_guarantee", "Average", averageSteps, "Guaranteed-Unique Hard Grover Search")
    plotStepFitGraph("uniquelin_grover_unique_guarantee", "Median", medianSteps, "Guaranteed-Unique Hard Grover Search")

