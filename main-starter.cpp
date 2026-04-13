#include <algorithm>
#include <iostream>
#include <vector>

/*
Starter C++ file
- This code is not at all optimized!
*/

// Global variables to maintain the graph.
size_t N, M;                              // # of vertices and edges.
std::vector< std::vector<size_t> > adjl;  // Adjacency list.
size_t best;                              // Size of best solution found (for bounding)

// ProblemState stores a partial solution to the problem
// - The next star system id to consider including/excluding
// - The set of star systems currently included in this partial solution
struct ProblemState {
  size_t next_id=0;
  std::vector<bool> include_set;

  ProblemState(
    size_t id,
    const std::vector<bool>& inc_set
  ) :
    next_id(0),
    include_set(inc_set)
  { }
};

// Test if a set of vertices represents a legal solution.
bool test_valid(const std::vector<bool>& test_set) {
  for (int v1 = 0; v1 < N; ++v1) {
    if (test_set[v1]) continue;  // Vertex is in the set; all its edges are covered.
    for (int v2 : adjl[v1]) {    // Vertex is NOT in the set, other side of edges must be!
      if (test_set[v2] == false) return false;
    }
  }
  return true;
}

// Search through all possible combinations of vertices.
// - state gives the current partial solution state that we're working on in this
//   function call (intentionally pass-by-copy here)
size_t find_min_stations(ProblemState state) {

  auto& include_set = state.include_set;

  // Determine the number of vertices in the current solution set.
  const size_t num_stations = std::count(
    include_set.begin(),
    include_set.end(),
    true
  );

  const bool valid_sol = test_valid(include_set);

  // If we've considered all IDs and don't have a valid solution, return N + 1
  // Otherwise, if we have a solution, return number of stations.
  if (state.next_id >= N && !valid_sol) {
    return N + 1; // N + 1 is a big answer that will never be used
  } else if (valid_sol) {
    return num_stations;
  }

  // Current id that we're going to try including / excluding
  const size_t cur_id = state.next_id;
  state.next_id += 1; // Update next id for recursive calls

  // Try out the next vertex as INCLUDED
  include_set[cur_id] = true;
  size_t result1 = find_min_stations(state);

  // and EXCLUDED.
  include_set[cur_id] = false;
  size_t result2 = find_min_stations(state);

  // Return the best result between including and excluding.
  return std::min(result1, result2);
}

int main()
{
  // Load in the provided graph
  std::cin >> N >> M;
  best = N+1;
  adjl.resize(N);

  size_t v1, v2;
  for (size_t i = 0; i < M; ++i) {
    std::cin >> v1 >> v2;
    adjl[v1].push_back(v2);
    adjl[v2].push_back(v1);
  }

  // Start the branch-and-bound! (with 0 as our start ID and no includes)
  size_t min_cover = find_min_stations({0, std::vector<bool>(N, false)});

  std::cout << min_cover << std::endl;

  return 0;
}