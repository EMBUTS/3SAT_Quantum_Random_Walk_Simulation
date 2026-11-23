#include "SATReadProblems.hpp"
#include <iostream>
#include <cmath>

void solveSATBruteForce(int n, int m, std::vector<std::vector<int>>& problem) {
    std::cout << "Brute force solution:" << std::endl;

    if (n > 64) {
        exit(11);
    }

    unsigned long long maxAssignment = 1ULL << n; 
    std::bitset<64> bits;
    bool valid;

    for (unsigned long long assignment = 0; assignment < maxAssignment; ++assignment) {
        bits = assignment;
        valid = true;
        for (int clauseIdx=0; clauseIdx<m; clauseIdx++) {
            if (!(bits[std::abs(problem[clauseIdx][0])-1] == (problem[clauseIdx][0] > 0) || bits[std::abs(problem[clauseIdx][1])-1] == (problem[clauseIdx][1] > 0) || bits[std::abs(problem[clauseIdx][2])-1] == (problem[clauseIdx][2] > 0))) {
                valid = false;
                break;
            }
        }
        if (valid) {
            for (int i = n - 1; i >= 0; --i) {
                std::cout << bits[i];
            }
            std::cout << '\n';
        }
    }

    std::cout << "==================================================" << std::endl;
}

int main() {
    int m;

    for (int n=3; n < 45; n++) {
        std::list<std::vector<std::vector<int>>> SATformulas = readSAT(n, "uniquelin");
        for (auto& problem : SATformulas) {
            m = problem.size();
            solveSATBruteForce(n,m,problem);
        }
    }
}