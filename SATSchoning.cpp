#include <cmath>
#include <random>
#include <list>
#include <iostream>
#include <fstream>
#include <sstream>
#include "SATReadProblems.hpp"

std::vector<int> getUnsatisfiedClauses(std::vector<std::vector<int>>& problem, std::vector<bool> assignment) {
    std::vector<int> unsatClauses;
    for (std::size_t i=0; i<problem.size(); i++) {
        if (assignment[std::abs(problem[i][0])-1] != (problem[i][0] > 0) &&
            assignment[std::abs(problem[i][1])-1] != (problem[i][1] > 0) &&
            assignment[std::abs(problem[i][2])-1] != (problem[i][2] > 0)) {
            
            unsatClauses.push_back(i);
        }
    }
    return unsatClauses;
}

void writeSchoningResults(std::ofstream& outputCsv, int n, int m, std::vector<bool> solution, int steps, int iters) {
    std::stringstream resultString;
    resultString << n << "," << m << ",";
    for (int i=0; i<n; i++) {
        resultString << solution[i];
    }
    resultString << "," << steps << "," << 3*n << "," << iters << '\n';
    outputCsv.write(resultString.str().c_str(),resultString.str().size());
}

void solveSatSchoning(int n, int m, std::vector<std::vector<int>>& problem, std::ofstream& outputCsv, bool verbose=false) {

    int iter = 0;
    std::vector<bool> a(n);
    std::vector<int> unsatClauses;

    while (true) {
        for (int i=0; i<n; i++) {
            a[i] = std::rand()%2;
        }

        for (int step=0; step<n*3; step++) {
            unsatClauses = getUnsatisfiedClauses(problem, a);
            if (unsatClauses.size() == 0) {
                if (verbose) {
                    std::cout << "Solution found on iter " << iter << ": ";
                    for (int i=0; i<n; i++) {
                        std::cout << a[i];
                    }
                    std::cout << '\n';
                }
                writeSchoningResults(outputCsv, n, m, a, step, iter);
                return;
            }

            a[std::abs(problem[unsatClauses[std::rand()%(unsatClauses.size())]][std::rand()%3])-1].flip();
        }
        iter ++;
    }

    std::cout << "No solution found.";
}

int main() {
    int m;

    for (int n=3; n < 31; n++) {
        std::list<std::vector<std::vector<int>>> SATformulas = readSAT(n, "uniquelin");

        std::stringstream fname;
        fname << "results/uniquelin_schoning_" << n << ".csv";
        std::ofstream outputCsv(fname.str());
        outputCsv.write("n,m,solution,steps,steps_per_iter,iters\n",40);

        for (auto& problem : SATformulas) {
            m = problem.size();

            solveSatSchoning(n,m,problem,outputCsv);
        }

        outputCsv.close();
    }
}