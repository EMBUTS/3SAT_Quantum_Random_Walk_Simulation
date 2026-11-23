import numpy as np
import math
from SATReadProblems import readSAT

def isSatisfied(assignment, problem):
    return all(any(assignment[abs(k)-1] == (k > 0) for k in clause) for clause in problem)

def bruteForceSAT(n, problem):
    X = np.arange(2**n, dtype=np.int64)
    satisfied = np.ones(2**n, dtype=bool)
    for clause in problem:
        clauseSatisfied = np.zeros(2**n, dtype=bool)
        for k in clause:
            bit = ((X >> (abs(k)-1)) & 1).astype(bool)
            clauseSatisfied |= bit if k>0 else ~bit
        satisfied &= clauseSatisfied
    return satisfied

def groverSimulate(n, problem, numSteps):
    N = 2**n
    marked = bruteForceSAT(n, problem)
    psi = np.full(N, 1/np.sqrt(N), dtype=np.complex128)

    for _ in range(numSteps):
        psi[marked] *= -1
        psi = (2/N)*psi.sum(axis=0) -psi
    return psi


def solveSatGrover(n, m, problem, outputCsv, repetitions=50, sampleRepetitions=5):

    rng = np.random.default_rng()
    totalSteps = 0
    for iteration in range(repetitions):
        numSteps = math.floor(math.pi/4*math.sqrt(2**iteration))

        state = groverSimulate(n, problem, numSteps)

        distrib = (np.abs(state)**2).astype(np.float64)
        sampleProbs = distrib/distrib.sum()

        solution = ""
        for sampleAttempt in range(sampleRepetitions):
            sample = rng.choice(2**n, p=sampleProbs)
            totalSteps += numSteps
            solution = [(int(sample) >> j) & 1 for j in range(n)]
            if isSatisfied(solution,problem):
                outputCsv.write(f"{n},{m},{''.join(map(str,solution))},{totalSteps},{iteration*sampleRepetitions+sampleAttempt}\n")
                return

    outputCsv.write(f"{n},{m},None,{totalSteps},{iteration}\n")

for k in ["std","hard","unique","uniquelin"]:
    for n in range(17,20):
        SATformulas = readSAT(n,k)[:100]

        outputCsv = open(f"results/{k}_grover5_{n}.csv",'w')
        outputCsv.write("n,m,solution,total_steps,iters\n")

        it=1
        for problem in SATformulas:
            m = len(problem)

            solveSatGrover(n,m,problem,outputCsv)
            print(f"Solved {it}/250 for n={n}")
            it+=1

        outputCsv.close()



def solveSatGroverGuaranteedUnique(n, m, problem, outputCsv, repetitions=50):

    rng = np.random.default_rng()
    totalSteps = 0
    numSteps = math.floor(math.pi/4*math.sqrt(2**iteration))
    state = groverSimulate(n, problem, numSteps)
    distrib = (np.abs(state)**2).astype(np.float64)
    sampleProbs = distrib/distrib.sum()
    for iteration in range(repetitions):
        sample = rng.choice(2**n, p=sampleProbs)
        totalSteps += numSteps
        solution = [(int(sample) >> j) & 1 for j in range(n)]
        if isSatisfied(solution,problem):
            outputCsv.write(f"{n},{m},{''.join(map(str,solution))},{totalSteps},{iteration}\n")
            return
    outputCsv.write(f"{n},{m},None,{totalSteps},{iteration}\n")
