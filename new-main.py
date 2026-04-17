import copy
import time

class State:
    def __init__(self, nodes, edges_left):
        self.nodes = nodes[:]             
        #self.n = len(nodes)
        self.curr_size = 0 # just a normal int
        self.considered = 0 # 200 bits long
        self.zeroed = 0 # bitstring
        self.edges_left = edges_left # int
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

    # Bitstring of neighbors to node being included
    neighbors = state.nodes[idx]
    state.edges_left -= neighbors.bit_count()

    # Go through each of the neighbors so they can be updated
    while neighbors:
        
        # Get index of LSB (a neighbor)
        curr = (neighbors & -neighbors).bit_length() - 1

        # Remove LSB (the neighbor) from remaining
        neighbors &= neighbors - 1

        # Remove node being included from the current neighbor (LSB)
        state.nodes[curr] &= ~(1 << idx)

        # If that neighbor becomes empty, mark it in zeroed
        if state.nodes[curr] == 0:
            state.zeroed |= (1 << curr)

    # Update the state after all neighbors have the included node removed
    state.nodes[idx] = 0
    state.zeroed |= (1 << idx)
    state.curr_size = state.curr_size + 1
    state.considered = state.considered | (1 << idx)


def exclude_node(state, idx):
    state.considered |= (1 << idx)

def approximate(state):
    # Runs in place on the state
    while True:
        if state.zeroed == state.mask:
            return

        idx = next_index(state)
        if idx == -1:
            return

        include_node(state, idx)
    

def simplify(state):

    changes = True
    while changes:
        changes = False
        not_considered = ~(state.considered) & state.mask
        while not_considered:
            curr = (not_considered & -not_considered).bit_length() - 1
            not_considered &= not_considered - 1

            curr_node = state.nodes[curr]


            # Remove nodes with degree zero
            if curr_node == 0:
                exclude_node(state, curr)
                changes = True

            # Include when there is a path
            elif curr_node.bit_count() == 1:
                include_node(state, curr_node.bit_length() - 1)
                changes = True


    


def solve(state, best_state):

    # Return if solved, update if better than best_state
    if state.zeroed == state.mask:
        if state.curr_size < best_state.curr_size:
            best_state.nodes = state.nodes[:]
            best_state.curr_size = state.curr_size
            best_state.considered = state.considered
            best_state.zeroed = state.zeroed
            best_state.edges_left = state.edges_left
        return

    # Check if its even possible
    not_considered = ~(state.considered) & state.mask
    possible = 0
    while not_considered:
        curr = (not_considered & -not_considered).bit_length() - 1
        not_considered &= not_considered - 1

        possible += state.nodes[curr].bit_count()
        #possible += (state.nodes[curr] >> curr).bit_count()
        
    if possible < state.edges_left:
        return
    


    idx = next_index(state)    
    if idx == -1:
        return

    
    # Bound
    max_edges = state.nodes[idx].bit_count()
    if max_edges == 0:
        return
    bound =  (state.edges_left + max_edges - 1) // max_edges
    if state.curr_size + bound >= best_state.curr_size:
        return


    state_copy = copy.deepcopy(state)

    # Include
    include_node(state, idx)
    simplify(state)
    solve(state, best_state)

    # Exclude
    exclude_node(state_copy, idx)
    simplify(state_copy)
    solve(state_copy, best_state)
         



if __name__ == "__main__":
    n, m = map(int, input().split())

    nodes = [0] * n
    matched = set()

    for _ in range(m):
        u, v = map(int, input().split())
        nodes[u] |= (1 << v)
        nodes[v] |= (1 << u)
        

    # Make our two states that we need
    state = State(nodes, m)
    best_state = copy.deepcopy(state)
    best_state.curr_size = n

    approximate(best_state)
    start = time.time()
    simplify(state)
    solve(state, best_state)
    end = time.time()
    print("MIN:", best_state.curr_size)
    print("TIME:", end - start)
    
