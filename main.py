# TODO: convert to a list of edges instead of adjacency matrix?
import numpy as np


class State:
    def __init__(self, n):
       self.matrix = np.zeros((n, n))
       self.curr_size: int = 0
       self.included: int = 0
       self.excluded: int = 0
       #self.mask: int = 0 # for included/excluded
       self.completed_mask = np.zeros((n, n))


def solver(state, best_size):

    # TODO: Add a bound here that compares current and best_size so below works
    idx = next_index(state)
    if idx == -1:
        return

    exclude_state = state

    # include -> state(updated)
    state.matrix[idx, :] = 0
    state.matrix[:, idx] = 0
    state.included |= (1 << idx)
    state.curr_size += 1 
    solver(state, best_size)

    best_size = min(best_size, state.curr_size)
    
    # exclude -> state
    state.excluded |= (1 << idx)
    solver(exclude_state, best_size)

    best_size = min(best_size, exclude_state.curr_size)
    return

def next_index(state) -> int:
    max_vals = 0
    index = -1
    for idx in range(state.matrix.shape[0]):
        if (state.included & (1 << idx) == 0) and (state.excluded & (1 << idx) == 0):
            vals = np.count_nonzero(matrix[idx])
            if vals > max_vals:
                max_vals = vals
                index = idx

    return index

def approximate(state: State) -> int:
    while np.any(state.matrix):

        idx = next_index(state)
        if idx == -1:
            return state.curr_size

        state.matrix[idx, :] = 0
        state.matrix[:, idx] = 0

        state.curr_size += 1

        #NOTE: Don't need this, but here for now
        state.included |= (1 << idx)

    return state.curr_size


    # repeat until valid solution



if __name__ == "__main__":

    n, m = list(map(int, input().split()))
    
    matrix = np.zeros((n, n))

    # TODO: Use triangular later
    for _ in range(m):
        row, col = list(map(int, input().split()))
        matrix[row, col] = 1
        matrix[col, row] = 1
    
    # Create initial state
    state = State(n)
    state.matrix = matrix

    # Get solution
    best_guess = approximate(state)
    solver(state, best_guess)

    print(state.curr_size)
