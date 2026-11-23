from SATGenerator import write_sat

minN = 3
maxN = 30
numProblems = 250

for n in range(minN, maxN+1):
    genAlg = "UPT1" # "G3" "G3Hard" "UPT4"
    write_sat(n, genAlg, numProblems)
