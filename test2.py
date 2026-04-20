import copy
import time
import sys

# Increase recursion depth for deep search trees

class State:
    def __init__(self, nodes, edges_left, min_required):
        self.nodes = nodes[:]             
        #self.n = len(nodes)
        self.curr_size = 0 # just a normal int
        self.considered = 0 # 200 bits long
        self.zeroed = 0 # bitstring
        self.edges_left = edges_left # int
        self.mask = (1 << len(nodes)) - 1 # 200 bits long
        self.min_required = min_required
        self.num_branches = 0

    def manual_copy(self):
        new_state = State(self.nodes, self.edges_left, self.min_required)
        new_state.curr_size = self.curr_size
        new_state.considered = self.considered
        new_state.zeroed = self.zeroed
        new_state.num_branches = self.num_branches
        return new_state


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
        #val = state.nodes[curr].bit_count()
        val = ((state.nodes[curr] & ~state.considered) & state.mask).bit_count()
        if val > best_val:
            best_val = val
            best_idx = curr

    return best_idx

def include_node(state, idx, required_edges):

    # Check if idx is already added to considered
    if (state.considered >> idx) & 1:
        return

    # Bitstring of neighbors to node being included
    neighbors = state.nodes[idx] & state.mask
    state.edges_left -= neighbors.bit_count()

    # Go through each of the neighbors so they can be updated
    while neighbors:
        
        # Get index of LSB (a neighbor)
        curr = (neighbors & -neighbors).bit_length() - 1

        # Remove LSB (the neighbor) from remaining
        neighbors &= neighbors - 1

        # Remove node being included from the current neighbor (LSB)
        state.nodes[curr] &= ~(1 << idx)
        if (required_edges[curr] >> idx) & 1:
            state.min_required -= 1

        # If that neighbor becomes empty, mark it in zeroed
        if state.nodes[curr] == 0:
            state.zeroed |= (1 << curr)

    # Update the state after all neighbors have the included node removed
    state.nodes[idx] = 0
    state.zeroed |= (1 << idx)
    state.curr_size = state.curr_size + 1
    state.considered = state.considered | (1 << idx)


def exclude_node(state, idx, required_edges):
    state.considered |= (1 << idx)
    # Optimization: To cover edges of an excluded node, all its neighbors must be included
    neighbors = state.nodes[idx] & state.mask
    while neighbors:
        curr = (neighbors & -neighbors).bit_length() - 1
        neighbors &= neighbors - 1
        include_node(state, curr, required_edges)

def approximate(state, required_edges):
    # Runs in place on the state
    while True:
        if state.edges_left == 0:
            return

        idx = next_index(state)
        if idx == -1:
            return

        include_node(state, idx, required_edges)
    

def simplify(state, required_edges):

    changes = True
    while changes:
        changes = False
        not_considered = ~(state.considered) & state.mask
        while not_considered:
            curr = (not_considered & -not_considered).bit_length() - 1
            not_considered &= not_considered - 1

            curr_node = state.nodes[curr] & state.mask


            # Remove nodes with degree zero
            if curr_node == 0 and not ((state.zeroed >> curr) & 1):
                state.considered |= (1 << curr)
                state.zeroed |= (1 << curr)
                changes = True

            # Include when there is a path
            elif curr_node.bit_count() == 1:
                neighbor_idx = curr_node.bit_length() - 1
                include_node(state, neighbor_idx, required_edges)
                changes = True


def solve(state, best_state, required_edges):
    state.num_branches += 1

    # Return if solved, update if better than best_state
    if state.edges_left == 0:
        if state.curr_size < best_state.curr_size:
            best_state.curr_size = state.curr_size
        return

    # Check if its even possible
    # (Simplified pruning using the matching-based lower bound)
    if state.curr_size + state.min_required >= best_state.curr_size:
        return
    
    idx = next_index(state)    
    if idx == -1:
        return
    
    # Bound
    max_edges = (state.nodes[idx] & state.mask).bit_count()
    if max_edges == 0:
        return

    # Include
    state_copy = state.manual_copy()
    include_node(state_copy, idx, required_edges)
    simplify(state_copy, required_edges)
    solve(state_copy, best_state, required_edges)

    # Exclude
    state_copy2 = state.manual_copy()
    exclude_node(state_copy2, idx, required_edges)
    simplify(state_copy2, required_edges)
    solve(state_copy2, best_state, required_edges)
          

if __name__ == "__main__":
    line1 = sys.stdin.readline().split()
    if not line1: exit()
    n, m = map(int, line1)

    nodes = [0] * n
    matched = [False] * n
    required_edges = [0] * n
    min_required = 0
    edge_count = 0

    for _ in range(m):
        u, v = map(int, sys.stdin.readline().split())
        if not (nodes[u] & (1 << v)):
            nodes[u] |= (1 << v)
            nodes[v] |= (1 << u)
            edge_count += 1
            if not matched[u] and not matched[v]:
                matched[u] = matched[v] = True
                required_edges[u] |= (1 << v)
                required_edges[v] |= (1 << u)
                min_required += 1

    # Make our two states that we need
    state = State(nodes, edge_count, min_required)
    best_state = State(nodes[:], edge_count, min_required)
    best_state.curr_size = n

    approx_state = state.manual_copy()
    simplify(approx_state, required_edges)
    approximate(approx_state, required_edges)
    best_state.curr_size = approx_state.curr_size

    print("APPROX:", best_state.curr_size)
    start = time.time()
    simplify(state, required_edges)
    solve(state, best_state, required_edges)
    end = time.time()
    print("MIN:", best_state.curr_size)
    print("TIME:", end - start)
    print(best_state.curr_size)
