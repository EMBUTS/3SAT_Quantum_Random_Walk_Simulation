#include <fstream>
#include <iostream>
#include <list>
#include <sstream>

std::list<std::vector<std::vector<int>>> readSAT(int n, std::string problemSource) {
    std::ostringstream prefix;
    if (problemSource == "hard")
        prefix << "problems/3SATHARD_" << n << "_";
    else if (problemSource == "unique")
        prefix << "problems/3SATUNIQUE_" << n << "_";
    else if (problemSource == "uniquelin")
        prefix << "problems/3SATUNIQUELIN_" << n << "_";
    else
        prefix << "problems/3SAT_" << n << "_";

    std::ifstream problemFile;

    for (const auto & entry : std::__fs::filesystem::directory_iterator("problems")) {
        if (entry.path().string().compare(0, prefix.str().size(), prefix.str()) == 0) {
            problemFile.open(entry.path().string());
            break;
        }
    }

    if (!problemFile.is_open()) {
        exit(10);
    }

    std::string line;
    std::stringstream numStream;
    int m;
    std::list<std::vector<std::vector<int>>> formulaList;

    while(std::getline(problemFile, line)) {
        numStream.str(line);
        numStream.clear();
        numStream >> m; // Should be n
        numStream >> m;

        std::vector<std::vector<int>> formula(m,std::vector<int>(3));

        for (int i=0; i<m; i++) {
            std::getline(problemFile, line);
            numStream.str(line);
            numStream.clear();
            for (int j=0; j<3; j++) {
                numStream >> formula[i][j];
            }
        }

        formulaList.push_back(formula);
        std::getline(problemFile, line);
    }

    return formulaList;
}