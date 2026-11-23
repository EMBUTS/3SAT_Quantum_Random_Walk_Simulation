CXX = clang++

EXE = SATSchoningExe
SOURCES = SATReadProblems.cpp
BRUTESOURCES = SATBruteForcer.cpp 
SCHOSOURCES = SATSchoning.cpp 
SOURCES += $(SCHOSOURCES)
OBJS = $(addsuffix .o, $(basename $(notdir $(SOURCES))))

CXXFLAGS = -Wall -Wextra -Wformat


%.o:%.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $<

all: $(EXE) clean
	@echo Build complete

$(EXE): $(OBJS)
	$(CXX) -o $@ $^ $(CXXFLAGS) $(LIBS)

run:
	./$(EXE)

br: all run

clean:
	rm $(OBJS)