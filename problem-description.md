# GALACTIC TOLL STATIONS PROBLEM

Objective - Find smallest set of vertices such that every edge is incident
            to a vertex in that set.

Input - First line: N number of vertices and M number of edges
        Next M lines: two ids i and j, (0 <= i, j < N), where i and j
                        are vertices that are connected with an edge.

Output - Minimum number of star systems that solves the problem.

c++ runtime: 5 seconds
python runtime: 14 seconds


## TODO:
- Mark Tasks as -- COMPLETE when finished
- Add descriptions to each of the tasks specifically for the problem
- Think of best way to represent state
- Zero out using i and j pointers on triangular matrix, swap when hit diag
- Use a list of edges or a dictionary of nodes and bitstrings


## Tasks:
1. Read input --COMPLETE
2. Simplify --COMPLETE
3. Run Approximation --COMPLETE
4. Solve (branch and bound) --COMPLETE


## Simplifications:
1. exclude with zero edges -- COMPLETE
2. include neighbors if degree 1 --COMPLETE
3. remove required_edges and min_required if possible
4. move the including within the exclude_node() to somplifications
5.




