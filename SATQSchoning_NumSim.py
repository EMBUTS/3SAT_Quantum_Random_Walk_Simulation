import math
import numpy as np


def isSatisfied(assignment, problem):
    return all(any(assignment[abs(k)-1] == (k > 0) for k in clause) for clause in problem)

def toBits(x, n):
    return [(int(x) >> j) & 1 for j in range(n)]

def schoningRun(problem, initX, selectedTrits):
    # Single classical Schoning run given known start params
    x = list(initX)
    for i in range(len(selectedTrits)):
        unsat = [cl for cl in problem if not any(x[abs(k)-1] == (k > 0) for k in cl)]
        if not unsat:
            return x, i
        if selectedTrits[i] < 3:
            v = abs(unsat[0][selectedTrits[i]]) - 1
            x[v] ^= 1
    return x, len(selectedTrits)


class SchoningTables:
    # Per-assignment lookup tables.""

    def __init__(self, n, problem, numSteps):
        for clause in problem:
            if len(clause) != 3 or len({abs(k) for k in clause}) != 3:
                raise ValueError(f"clause {clause} must have 3 distinct variables")
        self.n = n
        self.problem = problem
        self.numSteps = numSteps
        x = np.arange(2**n, dtype=np.int64)
        clauseUnsat = np.array([np.logical_and.reduce([((x >> (abs(lit)-1)) & 1) != (lit > 0) for lit in clause]) for clause in problem])
        self.solvedX = ~clauseUnsat.any(axis=0)
        firstUnsat = clauseUnsat.argmax(axis=0)
        # X walk transition matrix
        self.nextX = x[:, None] ^ np.array([[1 << (abs(lit)-1) for lit in clause] for clause in problem])[firstUnsat]
        self.nextX[self.solvedX] = x[self.solvedX, None]  # solved, is not flipped

        # successProbTable[t][x]: probability that a run at step t, with assignment x, ends solved
        self.successProbTable = np.empty((numSteps + 1, 2**n))
        self.successProbTable[numSteps] = self.solvedX
        # backwards dp
        for t in range(numSteps - 1, -1, -1):
            self.successProbTable[t] = self.successProbTable[t + 1][self.nextX].mean(axis=1)
        self.p = self.successProbTable[0].mean()  # prob of good initial params for problem

def sampleGoodParams(tables, good, rng):
    # Sample params at uniform matching goodness measurement
    tb = tables
    weight = tb.successProbTable if good else 1 - tb.successProbTable
    # Randomly select initial X according to success prob dist
    initX = rng.choice(2**tb.n, p=(weight[0] / weight[0].sum()))
    x, trits = initX, []
    # Randomly select trits leading to states with positive success weight at t (always works by last step)
    for t in range(tb.numSteps):
        w = weight[t + 1][tb.nextX[x]]
        trit = int(rng.choice(3, p=w / w.sum()))
        trits.append(trit)
        x = tb.nextX[x, trit]
    return toBits(initX, tb.n), trits


class Grover2DSimulator:
    # Reduce Grover amp-amp search to 2D system

    def __init__(self, p):
        self.p = p
        # collect params superposition into good/bad states
        self.state = np.array([math.sqrt(p), math.sqrt(1 - p)])
        self.oracleMatrix = np.diag([-1.0, 1.0])
        self.diffusionMatrix = 2 * np.outer(self.state, self.state) - np.eye(2)

    def groverIteration(self):
        self.state = self.diffusionMatrix @ (self.oracleMatrix @ self.state)

    def probGood(self):
        return self.state[0]**2


def solveSatQuantumSchoning(n, m, problem, outputCsv, repetitions=70, numSteps=None, seed=None):
    # Grover amplitude amplification with an unknown number of good states
    rng = np.random.default_rng(seed)
    numSteps = 3*n if numSteps is None else numSteps
    tables = SchoningTables(n, problem, numSteps)

    totalSteps = 0
    for attempt in range(repetitions):
        groverIterations = math.floor(math.pi/4*math.sqrt(2**attempt))
        groverSim = Grover2DSimulator(tables.p)
        for _ in range(groverIterations):
            groverSim.groverIteration()

        # simulate searchable measurement for good params
        good = (tables.p > 0 and rng.random() < groverSim.probGood())
        # sample random params matching measurement
        x0, trits = sampleGoodParams(tables, good, rng)
        solution, schoRunSteps = schoningRun(problem, x0, trits)
        totalSteps += 2*numSteps*groverIterations + schoRunSteps
        if isSatisfied(solution, problem):
            outputCsv.write(f"{n},{m},{''.join(map(str, solution))},{totalSteps},{attempt}\n")
            return
    outputCsv.write(f"{n},{m},None,{totalSteps},{repetitions}\n")


if __name__ == "__main__":
    from SATReadProblems import readSAT
    for k in ["std","hard","unique","uniquelin"]:
        for n in range(3, 23):
            SATformulas = readSAT(n,k)
            outputCsv = open(f"results/{k}_qschoning_{n}.csv", 'w')
            outputCsv.write("n,m,solution,total_steps,iters\n")

            for problem in SATformulas:
                m = len(problem)

                solveSatQuantumSchoning(n, m, problem, outputCsv)

            outputCsv.close()
