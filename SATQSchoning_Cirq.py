import math
import numpy as np
import cirq
from SATReadProblems import readSAT

def bitsOf(value, width):
    return [int(b) for b in format(value, f'0{width}b')]

def isSatisfied(assignment, problem):
    return all(any(assignment[abs(k)-1] == (k > 0) for k in clause) for clause in problem)

class UniformInit(cirq.Gate):
    def __init__(self, size, numQubits):
        super().__init__()
        self.size = size
        self.numQubits = numQubits

    def _num_qubits_(self):
        return self.numQubits

    def _unitary_(self):
        dim = 2**self.numQubits
        psi = np.zeros(dim)
        psi[:self.size] = 1 / np.sqrt(self.size)
        psi[0] -= 1
        return np.eye(dim) - 2 * np.outer(psi, psi) / np.dot(psi, psi)

    def __pow__(self, exp):
        return self if exp in (1,-1) else NotImplemented

    def _circuit_diagram_info_(self, args):
        return ["#"] * self.numQubits

class QuantumSchoning:
    def __init__(self, n, problem, numSteps):
        for clause in problem:
            if len(clause) != 3 or len({abs(k) for k in clause}) != 3:
                raise ValueError(f"clause {clause} must have 3 distinct variables")
        self.n = n
        self.problem = problem
        self.m = len(problem)
        self.numSteps = 3*n if numSteps is None else numSteps
        self.selectedClauseDim = math.ceil(np.log2(self.m + 1))

        self.xQubits = cirq.LineQubit.range(n)
        self.selectedTritQubits = [cirq.NamedQubit.range(2, prefix=f'trit{t}_') for t in range(self.numSteps)]
        self.selectedClauseQudits = [cirq.NamedQubit.range(self.selectedClauseDim, prefix=f'selectedClause{t}_') for t in range(self.numSteps)]
        self.unsatClauseQubits = cirq.NamedQubit.range(self.m, prefix='unsatClause')
        self.phaseQubit = cirq.NamedQubit('phase')
        self.searchableQubits = [*self.xQubits, *[q for trit in self.selectedTritQubits for q in trit]]
        self.allQubits = [*self.searchableQubits, *[q for rec in self.selectedClauseQudits for q in rec],
                          *self.unsatClauseQubits, self.phaseQubit]

    def unsatGates(self):
        # flip unsatClauseQubits[c] if clause c is false
        for c, clause in enumerate(self.problem):
            yield cirq.X(self.unsatClauseQubits[c]).controlled_by(*[self.xQubits[abs(k)-1] for k in clause],
                                                           control_values=[0 if k > 0 else 1 for k in clause])

    def schoningStep(self, t):
        selectedClauseQudit = self.selectedClauseQudits[t]
        yield from self.unsatGates()
        # selectedClauseQudit assigned to idx of the first unsat clause
        for clauseIdx in range(1, self.m + 1):
            if clauseIdx != self.m:
                controls, values = self.unsatClauseQubits[:clauseIdx+1], [0]*clauseIdx + [1]
            else:  # no unsat clause: selectedClause = m, solved, is not flipped
                controls, values = self.unsatClauseQubits, [0]*self.m
            for b, bit in enumerate(bitsOf(clauseIdx, self.selectedClauseDim)):
                if bit:
                    yield cirq.X(selectedClauseQudit[b]).controlled_by(*controls, control_values=values)
        yield from self.unsatGates()
        # flip the variable of literal trit[t] of the selected clause
        for clauseIdx, clause in enumerate(self.problem):
            for i, lit in enumerate(clause):
                yield cirq.X(self.xQubits[abs(lit)-1]).controlled_by(
                    *selectedClauseQudit, *self.selectedTritQubits[t], control_values=bitsOf(clauseIdx, self.selectedClauseDim) + bitsOf(i, 2))

    def schoningRunOracle(self):
        # Run a whole Schoning iteration
        for t in range(self.numSteps):
            yield self.schoningStep(t)

    def superposeSearchableQubits(self):
        return cirq.Circuit(cirq.H.on_each(*self.xQubits),
                            [UniformInit(3, 2).on(*trit) for trit in self.selectedTritQubits])

    def oracle(self):
        schoRun = self.schoningRunOracle()
        mark = cirq.Circuit(self.unsatGates(),
                            cirq.X(self.phaseQubit).controlled_by(*self.unsatClauseQubits, control_values=[0]*self.m), # all satisfied
                            self.unsatGates())
        return schoRun + mark + cirq.inverse(schoRun)

    def diffusion(self):
        searchableQubits = self.searchableQubits
        return (cirq.inverse(self.superposeSearchableQubits())
                + cirq.Circuit(cirq.X.on_each(*searchableQubits),
                               cirq.Z(searchableQubits[-1]).controlled_by(*searchableQubits[:-1]),
                               cirq.X.on_each(*searchableQubits))
                + self.superposeSearchableQubits())

    def circuit(self, groverIterations, measure=True):
        circuit = cirq.Circuit(cirq.X(self.phaseQubit), cirq.H(self.phaseQubit)) + self.superposeSearchableQubits()
        iteration = self.oracle() + self.diffusion()
        for _ in range(groverIterations):
            circuit += iteration
        if measure:
            circuit.append(cirq.measure(*self.searchableQubits, key='params'))
        return circuit

def schoningRun(problem, initX, selectedTrits):
    # Single classical Schoning iteration given known start params
    x = list(initX)
    for trit in selectedTrits:
        unsat = [cl for cl in problem if not any(x[abs(k)-1] == (k > 0) for k in cl)]
        if not unsat:
            return x
        if trit < 3:
            v = abs(unsat[0][trit]) - 1
            x[v] ^= 1
    return x

def decodeSeed(n, numSteps, bits):
    bits = list(bits)
    x0 = bits[:n]
    trits = [2*bits[n + 2*t] + bits[n + 2*t + 1] for t in range(numSteps)]
    return x0, trits

def solveSatQuantumSchoning(n, m, problem, outputCsv, repetitions=50, numSteps=None, seed=None):
    # Grover amplitude amplification with an unknown number of good states

    rng = np.random.default_rng(seed)
    numSteps = 3*n
    qs = QuantumSchoning(n, problem, numSteps)
    simulator = cirq.Simulator(dtype=np.complex128, seed=int(rng.integers(2**31)))

    totalSteps = 0
    for attempt in range(repetitions):
        groverIterations = math.floor(math.pi/4*math.sqrt(2**attempt))
        bits = simulator.run(qs.circuit(groverIterations), repetitions=1).measurements['params'][0]
        totalSteps += 2*numSteps*groverIterations
        x0, trits = decodeSeed(n, numSteps, bits)
        solution = schoningRun(problem, x0, trits)
        if isSatisfied(solution, problem):
            outputCsv.write(f"{n},{m},{''.join(map(str, solution))},{qs.numSteps},{totalSteps},{attempt}\n")
            return
    outputCsv.write(f"{n},{m},None,{qs.numSteps},{totalSteps},{repetitions}\n")

for n in range(3,4):
    SATformulas = readSAT(n,"std")[:5]

    outputCsv = open(f"results/cirq_qschoning_{n}.csv",'w')
    outputCsv.write("n,m,solution,steps,total_steps,iters\n")

    for problem in SATformulas:
        m = len(problem)

        solveSatQuantumSchoning(n,m,problem,outputCsv)

    outputCsv.close()