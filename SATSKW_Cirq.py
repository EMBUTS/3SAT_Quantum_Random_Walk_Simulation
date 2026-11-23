import numpy as np
import math
from SATReadProblems import readSAT

import cirq
import qsimcirq

class SATClause(cirq.Gate):
    def __init__(self, idx, literal_labels):
        super(SATClause, self)
        self.idx = idx
        self.literal_labels = literal_labels

    def _num_qubits_(self):
        return 5

    def _decompose_(self, qubits):
        q0, q1, q2, qOut, qFree = qubits
        #literal nots
        if self.literal_labels[0]:
            yield cirq.X(q0)
        if self.literal_labels[1]:
            yield cirq.X(q1)
        if self.literal_labels[2]:
            yield cirq.X(q2)
        #multi x
        yield cirq.decompose_multi_controlled_x(controls=[q0,q1,q2], target=qOut, free_qubits=[qFree])
        #literal nots
        if self.literal_labels[0]:
            yield cirq.X(q0)
        if self.literal_labels[1]:
            yield cirq.X(q1)
        if self.literal_labels[2]:
            yield cirq.X(q2)
        #last x
        yield cirq.X(qOut)

    def _circuit_diagram_info_(self, args):
        return [f"C{self.idx}"] * 5

class GroverCoin(cirq.Gate):
    def __init__(self, size):
        super(GroverCoin, self)
        self.size = size
        self.coinDim = math.ceil(np.log2(self.size))

    def _num_qubits_(self):
        return self.coinDim

    def _unitary_(self):
        subcoin = np.full((self.size,self.size),2/self.size) - np.eye(self.size)
        coin = np.eye(2**self.coinDim)
        coin[:self.size,:self.size] = subcoin
        return coin

    def _circuit_diagram_info_(self, args):
        return ["G"] * self.coinDim

class GroverFull(cirq.Gate):
    def __init__(self, size):
        super(GroverFull, self)
        self.size = size

    def _num_qubits_(self):
        return self.size

    def _decompose_(self,qubits):
        yield cirq.H.on_each(*qubits)
        yield cirq.X.on_each(*qubits)
        yield cirq.Z(qubits[-1]).controlled_by(*qubits[:-1])
        yield cirq.X.on_each(*qubits)
        yield cirq.H.on_each(*qubits)

    def _circuit_diagram_info_(self, args):
        return ["G"] * self.size
    
class WalkShift(cirq.Gate):
    def __init__(self, size):
        super(WalkShift, self)
        self.size = size
        self.coinDim = math.ceil(np.log2(self.size))

    def _num_qubits_(self):
        return self.size + self.coinDim

    def _decompose_(self, qubits):
        # first n = x, last n = coin
        for i in range(self.size):
            binstring = format(i, f'0{self.coinDim}b')
            for k in range(self.coinDim):
                if binstring[k]=='0':
                    yield cirq.X(qubits[self.size+k])
            yield cirq.X(qubits[i]).controlled_by(*qubits[self.size:])
            for k in range(self.coinDim):
                if binstring[k]=='0':
                    yield cirq.X(qubits[self.size+k])
            
    def _circuit_diagram_info_(self, args):
        return ["S"] * (self.size + self.coinDim)

class UniformCoinInit(cirq.Gate):
    def __init__(self, size):
        super(UniformCoinInit, self)
        self.size = size
        self.coinDim = math.ceil(np.log2(self.size))

    def _num_qubits_(self):
        return self.coinDim

    def _unitary_(self):
        indices = np.arange(self.size)
        jk = np.outer(indices, indices)
        omega = np.exp(2j * np.pi / self.size)
        submatr = (omega**jk) / np.sqrt(self.size)

        matr = np.eye(2**self.coinDim, dtype="complex128")
        matr[:self.size,:self.size] = submatr
        return matr
            
    def _circuit_diagram_info_(self, args):
        return ["#"] * (self.coinDim)


def solveSatSKW(n, m, problem, outputCsv):

    coinDim = math.ceil(np.log2(n))

    xQubits = cirq.LineQubit.range(n)
    clauseQubits = cirq.LineQubit.range(n, n+m)
    CNFCircuit = cirq.Circuit()
    freeQubit = cirq.NamedQubit('free')
    phaseAncillaQubit = cirq.NamedQubit('phaseAncilla')
    coinQubits = cirq.LineQubit.range(n+m, n+m+coinDim)

    for i in range(m):
        variableQubits = [xQubits[j] for j in [abs(k)-1 for k in problem[i]]]
        outputQubit = clauseQubits[i]
        literalLabels = [k > 0 for k in problem[i]]
        CNFCircuit.append(SATClause(i, literalLabels).on(*variableQubits,outputQubit,freeQubit))
    inverseCNFCircuit = cirq.inverse(CNFCircuit)

    coinCircuit = cirq.Circuit()
    coinCircuit.append(CNFCircuit)
    coinCircuit.append(cirq.X(phaseAncillaQubit).controlled_by(*clauseQubits))
    coinCircuit.append(GroverCoin(n).on(*coinQubits).controlled_by(phaseAncillaQubit, control_values=[0]))
    coinCircuit.append(cirq.Z(phaseAncillaQubit))
    coinCircuit.append(cirq.X(phaseAncillaQubit).controlled_by(*clauseQubits))
    coinCircuit.append(inverseCNFCircuit)


    SKWCircuit = cirq.Circuit()
    SKWCircuit.append(cirq.H.on_each(xQubits))
    SKWCircuit.append(UniformCoinInit(n).on(*coinQubits))

    numSteps = math.floor(math.pi/2*math.sqrt(2**(n-1)))

    for i in range(numSteps):
        SKWCircuit.append(coinCircuit)
        SKWCircuit.append(WalkShift(n).on(*xQubits,*coinQubits))
    SKWCircuit.append(cirq.measure(*xQubits, key='out'))

    repetitions = 100
    qsim_simulator = qsimcirq.QSimSimulator()
    qsim_results = qsim_simulator.run(SKWCircuit,repetitions=repetitions)

    samples = qsim_results.measurements['out']
    np.random.shuffle(samples)

    iteration = 0
    solution = ""
    valid = True
    while iteration < repetitions:
        solution = samples[iteration]
        valid = True
        for clause in problem:
            if solution[abs(clause[0])-1] != (clause[0] > 0) and solution[abs(clause[1])-1] != (clause[1] > 0) and solution[abs(clause[2])-1] != (clause[2] > 0):
                valid = False
                break
        if valid:
            break
        iteration += 1
    if not valid:
        outputCsv.write(f"{n},{m},None,{numSteps},{numSteps},100\n")
        return

    outputCsv.write(f"{n},{m},{''.join(map(str,solution))},{numSteps},{numSteps},{iteration}\n")



for n in range(3,4):
    SATformulas = readSAT(n,"std")[:5]

    outputCsv = open(f"results/cirq_skw_{n}.csv",'w')
    outputCsv.write("n,m,solution,steps,steps_per_iter,iters\n")

    for problem in SATformulas:
        m = len(problem)

        solveSatSKW(n,m,problem,outputCsv)

    outputCsv.close()
