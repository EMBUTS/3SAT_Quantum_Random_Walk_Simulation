import numpy as np
import math

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

def skwSimulate(n, problem, numSteps):
    N = 2**n
    marked = bruteForceSAT(n, problem)
    unmarked = ~marked
    psi = np.full((N,n), 1/np.sqrt(n*N), dtype=np.complex128)
    shiftMat = [np.arange(N) ^ (1 << (n-1-c)) for c in range(n)]

    for _ in range(numSteps):
        psi[marked] *= -1
        psi[unmarked] = (2/n)*psi[unmarked].sum(axis=1, keepdims=True) -psi[unmarked]
        for c in range(n):
            psi[:, c] = psi[shiftMat[c],c]
    return psi


def solveSatSKW(n, m, problem, outputCsv):

    rng = np.random.default_rng()
    numSteps = math.floor(math.pi/2*math.sqrt(2**(n-1)))

    state = skwSimulate(n, problem, numSteps)

    distrib = (np.abs(state)**2).sum(axis=1).astype(np.float64)
    sampleProbs = distrib/distrib.sum()

    iteration = 0
    solution = ""
    valid = True
    while True:
        sample = rng.choice(2**n, p=sampleProbs)
        solution = [(int(sample) >> j) & 1 for j in range(n)]
        valid = True
        for clause in problem:
            if all(solution[abs(k)-1] != (k > 0) for k in clause):
                valid = False
                break
        if valid:
            break
        iteration += 1

    outputCsv.write(f"{n},{m},{''.join(map(str,solution))},{numSteps},{numSteps},{iteration}\n")


if __name__ == "__main__":
    from SATReadProblems import readSAT
    for k in ["std","hard","unique","uniquelin"]:
        for n in range(3,17):
            SATformulas = readSAT(n,k)

            outputCsv = open(f"results/{k}_{n}.csv",'w')
            outputCsv.write("n,m,solution,steps,steps_per_iter,iters\n")

            for problem in SATformulas:
                m = len(problem)

                solveSatSKW(n,m,problem,outputCsv)

            outputCsv.close()