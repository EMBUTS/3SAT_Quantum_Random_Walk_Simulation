import os
import re

def readSAT(n, sourceAlg):
    if sourceAlg == "hard":
        prefix = f"3SATHARD_{n}_"
    elif sourceAlg == "unique":
        prefix = f"3SATUNIQUE_{n}_"
    elif sourceAlg == "uniquelin":
        prefix = f"3SATUNIQUELIN_{n}_"
    else:
        prefix = f"3SAT_{n}_"

    problemDir = "problems"

    problemFile = None

    for file in os.listdir(problemDir):
        fName = os.fsdecode(file)
        if fName.startswith(prefix):
            print(f"Reading {fName}")
            problemFile = open(os.path.join(problemDir, file), 'r')

    if not problemFile:
        print(f"Could not find {prefix} prefix")
        exit()
    if not problemFile.readable():
        exit()

    formulaList = []

    line = next(problemFile, None)
    while line:
        params = re.search(r"(\d+) (\d+)", line)
        _, m = map(int, params.groups())

        formula = []

        for i in range(m):
            line = next(problemFile, None)
            clause = [int(x) for x in re.findall(r"(-?\d+)", line)]
            formula.append(clause)

        formulaList.append(formula)
        line = next(problemFile, None)
        line = next(problemFile, None)

    return formulaList

def __main__():
    SATformulas = readSAT(3)
    for k in SATformulas[0]:
        print(k[0], k[1], k[2])
