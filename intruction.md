# Set up CPLEX in the environment

set CPLEX_HOME=C:/Program Files/IBM/ILOG/CPLEX_Studio128/cplex
set CPO_HOME=C:/Program Files/IBM/ILOG/CPLEX_Studio128/cpoptimizer
set PATH=%PATH%;%CPLEX_HOME%/bin/x64_win64;%CPO_HOME%/bin/x64_win64
set LD_LIBRARY_PATH=%LD_LIBRARY_PATH%;%CPLEX_HOME%/bin/x64_win64;%CPO_HOME%/bin/x64_win64
set PYTHONPATH=%PYTHONPATH%;/opt/ibm/ILOG/CPLEX_Studio128/cplex/python/3.5/x64_win64
