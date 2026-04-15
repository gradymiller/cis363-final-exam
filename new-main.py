import copy

class State:
    def __init__(self, nodes):
        self.nodes = nodes[:]             
        #self.n = len(nodes)
        self.curr_size = 0 # just a normal int
        self.considered = 0 # 200 bits long
        self.zeroed = 0
        self.mask = (1 << len(nodes)) - 1 # 200 bits long


def next_index(state):
    best_idx = -1
    best_val = -1

    # nodes not yet decided
    undecided_mask = ~(state.considered) & state.mask

    while undecided_mask:

        # Get index of least significant bit of undecided mask
        curr = (undecided_mask & -undecided_mask).bit_length() - 1

        # Remove the least significant bit
        undecided_mask &= undecided_mask - 1

        # Keep if better
        val = state.nodes[curr].bit_count()
        if val > best_val:
            best_val = val
            best_idx = curr

    return best_idx

def include_node(state, idx):

    # remove idx from all neighbors
    curr_mask = state.nodes[idx]

    # Go through the bits that the included one was connected to
    # [1] Jump to the least significant bit
    # [2] Remove that one from the neighbors (curr_mask)
    # [3] Remove that included node from each neighbor (curr)
    # [4] Update the state
    while curr_mask:
        curr = (curr_mask & -curr_mask).bit_length() - 1 # [1]
        curr_mask &= curr_mask - 1 # [2]
        state.nodes[curr] &= ~(1 << idx) # [3]
        if state.nodes[curr] == 0:
            state.zeroed |= (1 << curr)

    # [4]
    state.nodes[idx] = 0
    state.zeroed |= (1 << idx)
    state.curr_size = state.curr_size + 1
    state.considered = state.considered | (1 << idx)


def approximate(state):
    # Runs in place on the state
    while True:
        if state.zeroed == state.mask:
            return

        idx = next_index(state)
        if idx == -1:
            return

        include_node(state, idx)
    

def solve(state, best_state):
    if state.curr_size >= best_state.curr_size:
        return

    idx = next_index(state)    
    if idx == -1:
        return

   exclude_state = state 

    # Include
    include_node(state, idx)

    # Exclude
    



if __name__ == "__main__":
    n, m = map(int, input().split())

    nodes = [0] * n

    for _ in range(m):
        u, v = map(int, input().split())
        nodes[u] |= (1 << v)
        nodes[v] |= (1 << u)

    # Make our two states that we need
    state = State(nodes)
    best_state = State(nodes)
    
    approximate(best_state)
    print(best_state.curr_size)

    #solver(state, best_guess)
