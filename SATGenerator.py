from random import randint, sample, shuffle, choice
import math

# generate 3CNF with at least 1 solution
def gen_unique_instance(n: int, m: int) -> None:
    # Randomly generate clauses until all variables are distinct and at least one literal is valid
    for i in range(m):
        while True:
            for h in range(3):
                v[i][h] = randint(0,n-1)
                lit[i][h] = randint(0,1)
            if not ((v[i][0] == v[i][1]) or (v[i][1] == v[i][2]) or (v[i][2] == v[i][0]) or (lit[i][0] != t[v[i][0]] and lit[i][1] != t[v[i][1]] and lit[i][2] != t[v[i][2]]) ): break
    return

def print_sat(n: int, m: int):
    print(f"{n} vars, {m} clauses, 3-SAT")
    for j in range(m):
        for h in range(3):
            if (lit[j][h] == 0):
                print("-", end='')
            print(f"{v[j][h]+1} ", end='')
        print()
    return

def shuffle_sat(m: int) -> None:
    # Shuffle clauses
    for j in range(m-1,-1,-1):
        tmp = randint(0,j)
        v[tmp], v[j] = v[j], v[tmp]
        lit[tmp], lit[j] = lit[j], lit[tmp]
    return

def G2(n: int, m: int, verbose = False):
    global v            # variable number in each clause
    global lit          # literal type in each clause
    global t            # solution for formula generator

    v = [[0,0,0] for _ in range(m)]
    lit = [[0,0,0] for _ in range(m)]
    t = [randint(0,1) for _ in range(n)]

    # Randomly generate m clauses (except last n)
    gen_unique_instance(n, m-n)

    # For remaining n clauses, generate clauses where only the ith variable is correct
    for i in range(m-n, m):
        while True:
            for h in range(3):
                v[i][h] = randint(0,n-1)
                lit[i][h] = 1 - t[v[i][h]]
            h = randint(0,2)
            v[i][h] = i - m + n
            lit[i][h] = t[i - m + n]

            if not ((v[i][0] == v[i][1]) or (v[i][1] == v[i][2]) or (v[i][2] == v[i][0])): break
    shuffle_sat(m)

    if verbose:
        print("# instance by G2\n# solution = ")
        for i in range(n):
            print(f"{t[i]}", end='')
        print()

        print("="*50)

    return v, lit

def G3(n: int, m: int, verbose = False):
    global v            # variable number in each clause
    global lit          # literal type in each clause
    global t            # solution for formula generator
    
    v = [[0,0,0] for _ in range(m)]
    lit = [[0,0,0] for _ in range(m)]
    t = [randint(0,1) for _ in range(n)]

    # Randomly generate m clauses (except last 3n)
    gen_unique_instance(n, m-n-n-n)

    # For remaining 3n clauses, generate clauses where only the ith variable is correct, 3 times
    for i in range(m-n-n-n, m-n-n):
        while True:
            for h in range(3):
                v[i][h] = randint(0,n-1)
                lit[i][h] = 1 - t[v[i][h]]
            h = randint(0,2)
            v[i][h] = i - m + n + n + n
            lit[i][h] = t[i - m + n + n + n]

            if not ((v[i][0] == v[i][1]) or (v[i][1] == v[i][2]) or (v[i][2] == v[i][0])): break

    for i in range(m-n-n, m-n):
        while True:
            for h in range(3):
                v[i][h] = randint(0,n-1)
                lit[i][h] = 1 - t[v[i][h]]
            h = randint(0,2)
            v[i][h] = i - m + n + n
            lit[i][h] = t[i - m + n + n]

            if not ((v[i][0] == v[i][1]) or (v[i][1] == v[i][2]) or (v[i][2] == v[i][0])): break

    for i in range(m-n, m):
        while True:
            for h in range(3):
                v[i][h] = randint(0,n-1)
                lit[i][h] = 1 - t[v[i][h]]
            h = randint(0,2)
            v[i][h] = i - m + n
            lit[i][h] = t[i - m + n]

            if not ((v[i][0] == v[i][1]) or (v[i][1] == v[i][2]) or (v[i][2] == v[i][0])): break
    
    shuffle_sat(m)

    if verbose:
        print("# instance by G3\n# solution = ")
        for i in range(n):
            print(f"{t[i]}", end='')
        print()

        print("="*50)

    return v, lit

def UPT4(n: int, m: int):
    clauses = []
    solution = [randint(0,1) for _ in range(n)]
    for i in range(1,n+1):
        j,k = sample([_ for _ in range(1,i)]+[_ for _ in range(i+1,n+1)],2)
        iLit = i if solution[i-1] == 1 else -i
        clauses += [[iLit,j,k],[iLit,j,-k],[iLit,-j,k],[iLit,-j,-k]]

    shuffle(clauses) 
    for sublist in clauses:
        shuffle(sublist)
    v = [[abs(lit)-1 for lit in clause] for clause in clauses]
    lit = [[1 if lit>0 else 0 for lit in clause] for clause in clauses]
    return v, lit

def UPT1(n: int, m: int):
    clauses = []
    solution = [randint(0,1) for _ in range(n)]
    A = []
    B = [i for i in range(1,n+1)]
    p,q = sample(B,2)
    for i in [p,q]:
        j,k = sample([_ for _ in range(1,i)]+[_ for _ in range(i+1,n+1)],2)
        iLit = i if solution[i-1] == 1 else -i
        clauses += [[iLit,j,k],[iLit,j,-k],[iLit,-j,k],[iLit,-j,-k]]
    B.remove(p)
    A.append(p)
    B.remove(q)
    A.append(q)
    for i in range(3,n+1):
        r,t = sample(A,2)
        w = choice(B)
        wLit = w if solution[w-1] == 1 else -w
        rLit = -r if solution[r-1] == 1 else r
        tLit = -t if solution[t-1] == 1 else t
        clauses.append([wLit,rLit,tLit])
        B.remove(w)
        A.append(w)

    shuffle(clauses) 
    for sublist in clauses:
        shuffle(sublist)
    v = [[abs(lit)-1 for lit in clause] for clause in clauses]
    lit = [[1 if lit>0 else 0 for lit in clause] for clause in clauses]
    return v, lit

def write_sat(n: int, genAlg: str, numProblems: int):
    if genAlg == "G3HARD":
        alg = G3
        m = n*7
        satfile = open(f"problems/3SATHARD_{n}_{m}.txt", "w")
    elif genAlg == "UPT4":
        alg = UPT4
        m = n*4
        satfile = open(f"problems/3SATUNIQUE_{n}_{m}.txt", "w")
    elif genAlg == "UPT1":
        alg = UPT1
        m = n+6
        satfile = open(f"problems/3SATUNIQUELIN_{n}_{m}.txt", "w")
    else:
        alg = G3
        m = math.ceil(n*4.3)
        satfile = open(f"problems/3SAT_{n}_{m}.txt", "w")

    for i in range(numProblems):
        vars, lit = alg(n, m)
        satfile.write(f"{n} {m}\n")
        for j in range(m):
            for h in range(3):
                if (lit[j][h] == 0):
                    satfile.write("-")
                satfile.write(f"{vars[j][h]+1} ")
            satfile.write(f"\n")
        satfile.write(f"\n")
    satfile.close()
