# TODO: convert to a list of edges instead of adjacency matrix?
import numpy as np
import copy

class State:
    def __init__(self, n):
       self.matrix = np.zeros((n, n))
       self.curr_size: int = 0
       # self.included: int = 0
       self.excluded: int = 0
       self.degrees = np.empty(n)
       #self.mask: int = 0 # for included/excluded
       self.completed_mask = np.zeros((n, n))


def solver(state, best_size):

    # TODO: Add a bound here that compares current and best_size so below works

    idx = next_index(state)
    if idx == -1:
        return best_size

    exclude_state = copy.deepcopy(state)

    # include -> state(updated)
    update_degrees(state, idx)
    state.matrix[idx, :] = 0
    state.matrix[:, idx] = 0
    # state.included |= (1 << idx)
    state.curr_size += 1 
    in_sol = solver(state, best_size)

    best_size = min(best_size, in_sol)
    
    # exclude -> state
    state.excluded |= (1 << idx)
    ex_sol = solver(exclude_state, best_size)

    best_size = min(best_size, ex_sol)
    return best_size

def next_index(state: State) -> int:
    # TODO: make it so this function doesnt grab vertices that have 
    #       already been considered
    max_deg_idx = int(np.argmax(state.degrees))
    max_deg = int(np.max(state.degrees))
    return max_deg_idx if max_deg > 0 else -1

def update_degrees(state: State, index: int):
    # Grab row of adjacency matrix and find indices that need to be updated
    row = state.matrix[index]
    indices = np.nonzero(row)[0]

    # Update degrees accordingly
    state.degrees[indices] -= 1
    state.degrees[index] = 0

def approximate(state: State) -> int:
    while np.any(state.matrix):
        idx = next_index(state)
        if idx == -1:
            return state.curr_size

        # Keep track of how many uncovered edges touch each vertex
        update_degrees(state, idx)
        state.matrix[idx, :] = 0
        state.matrix[:, idx] = 0

        state.curr_size += 1

        #NOTE: Don't need this, but here for now
        # state.included |= (1 << idx)

    return state.curr_size
    # repeat until valid solution

if __name__ == "__main__":

    n, m = list(map(int, input().split()))
    matrix = np.zeros((n, n))
    degrees = np.zeros(n)

    # TODO: Use triangular later
    for i in range(m):
        row, col = list(map(int, input().split()))
        matrix[row, col] = 1
        matrix[col, row] = 1
        degrees[row] += 1
        degrees[col] += 1


    # Create initial state
    state = State(n)
    state.matrix = matrix
    state.degrees = degrees
    
    # Get approximate solution
    approx_state = copy.deepcopy(state)
    best_guess = approximate(approx_state)
    
    # Get solution
    solution = solver(state, best_guess)

    print(solution)
