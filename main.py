import numpy as np


class State:
    def __init__(self, n):
       self.matrix = np.zeros((n, n)) # adjacency matrix
       self.curr_size: int = 0 # number of included vertices
       self.included: int = 0 # bitstring
       #self.mask: int = 0 # for included/excluded
       self.completed_mask = np.zeros((n, n)) # all zeros, when done


def solver(state, best_size):
    # include -> state(updated)
    # exclude -> state
    # best_size = min(include, exclude, best_size)
    pass

def next_index(state) -> int:
    max_vals = 0
    index = -1
    for idx in range(state.matrix.shape[0]):
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

    # Use triangular later
    for _ in range(m):
        row, col = list(map(int, input().split()))
        matrix[row, col] = 1
        matrix[col, row] = 1
    
    state = State(n)
    state.matrix = matrix

    best_guess = approximate(state)

    #solver(state, best_guess)
    print(best_guess)
