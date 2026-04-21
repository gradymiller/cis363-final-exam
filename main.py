import time

class State:
    def __init__(self, nodes, edges_left): #, min_required):
        self.nodes = nodes[:]             
        #self.n = len(nodes)
        self.curr_size = 0 # just a normal int
        self.considered = 0 # 200 bits long
        self.zeroed = 0 # bitstring
        self.edges_left = edges_left # int
        self.mask = (1 << len(nodes)) - 1 # 200 bits long
        #self.min_required = min_required
        self.num_branches = 0

    def copy(self):
        new_state = State.__new__(State)

        new_state.nodes = self.nodes[:]
        new_state.curr_size = self.curr_size
        new_state.considered = self.considered
        new_state.zeroed = self.zeroed
        new_state.edges_left = self.edges_left
        new_state.mask = self.mask
        #new_state.min_required = self.min_required
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

def include_node(state, idx): #, required_edges):

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
        #if required_edges[curr] & (1 << idx) != 0:
            #state.min_required -= 1

        # If that neighbor becomes empty, mark it in zeroed
        if state.nodes[curr] == 0:
            state.zeroed |= (1 << curr)

    # Update the state after all neighbors have the included node removed
    state.nodes[idx] = 0
    state.zeroed |= (1 << idx)
    state.curr_size += 1
    state.considered = state.considered | (1 << idx)


def exclude_node(state, idx):
    state.considered |= (1 << idx)
    neighbors = state.nodes[idx] & state.mask

    while neighbors:
        curr = (neighbors & -neighbors).bit_length() - 1
        neighbors &= neighbors - 1
        include_node(state, curr) #, required_edges)  

def approximate(state): #, required_edges):
    # Runs in place on the state
    while True:
        if state.zeroed == state.mask:
            return

        idx = next_index(state)
        if idx == -1:
            return

        include_node(state, idx) #, required_edges)
    

def matching(state):
    matched = 0
    min_required = 0

    remaining = ~state.considered & state.mask

    while remaining:

        best = -1
        best_deg = 10**4

        scan = remaining & ~matched

        while scan:
            v = (scan & -scan).bit_length() - 1
            scan &= scan - 1
            
            deg = (state.nodes[v] & state.mask).bit_count()
            if deg > 0 and deg < best_deg:
                best = v
                best_deg = deg 

        if best == -1:
            break

        neighbors = state.nodes[best] & remaining & ~matched
        
        if neighbors: 
            u = (neighbors & -neighbors).bit_length() - 1

            matched |= (1 << u)
            matched |= (1 << best)
            min_required += 1

        remaining &= ~(1 << best)

    return min_required


def simplify(state): #, required_edges):

    changes = True
    while changes:
        changes = False
        not_considered = ~(state.considered) & state.mask
        while not_considered:
            curr = (not_considered & -not_considered).bit_length() - 1
            not_considered &= not_considered - 1

            curr_node = state.nodes[curr] & state.mask


            # Remove nodes with degree zero
            if curr_node == 0:
                exclude_node(state, curr)
                changes = True

            # Include when there is a path
            elif curr_node.bit_count() == 1:
                state.considered |= (1 << curr)
                include_node(state, curr_node.bit_length() - 1) #, required_edges)
                changes = True


def solve(state, best_state): #, required_edges):
    state.num_branches += 1

    # Return if solved, update if better than best_state
    if state.edges_left == 0:
        if state.curr_size < best_state.curr_size:
            best_state.curr_size = state.curr_size
        return

    """
    # Check if its even possible
    not_considered = ~(state.considered) & state.mask
    possible = 0
    while not_considered:
        curr = (not_considered & -not_considered).bit_length() - 1
        not_considered &= not_considered - 1

        mask = ~((1 << (curr + 1)) - 1) & state.mask

        #possible += state.nodes[curr].bit_count()
        
        possible += (state.nodes[curr] & mask).bit_count()
       
    if possible < state.edges_left:
        print(f"{state.num_branches}: possible, {state.curr_size}")
        return
    """

    idx = next_index(state)    
    if idx == -1:
        return
    
    # Bound
    max_edges = (state.nodes[idx] & state.mask).bit_count()
    if max_edges == 0:
        return
    bound = max(max_edges, matching(state))

    if state.curr_size + bound >= best_state.curr_size:
        return



    # Include
    state_copy = state.copy()
    include_node(state_copy, idx) #, required_edges)
    simplify(state_copy) #, required_edges)
    solve(state_copy, best_state) #, required_edges)

    # Exclude
    state_copy2 = state.copy()
    exclude_node(state_copy2, idx)
    simplify(state_copy2) #, required_edges)
    solve(state_copy2, best_state) #, required_edges)
         



if __name__ == "__main__":
    n, m = map(int, input().split())

    nodes = [0] * n
    matched = set()
    #required_edges = [0] * n
    #min_required = 0

    for _ in range(m):
        u, v = map(int, input().split())
        if (nodes[u] & (1 << v)):
            m -= 1
            continue

        nodes[u] |= (1 << v)
        nodes[v] |= (1 << u)
        #if u not in matched and v not in matched:
            #matched.add(u)
            #matched.add(v)
            #required_edges[u] |= (1 << v)
            #required_edges[v] |= (1 << u)
            #min_required += 1

        

    # Make our two states that we need
    state = State(nodes, m) #, min_required)
    best_state = State(nodes[:], m) #, min_required)

    simplify(best_state) #, required_edges)
    approximate(best_state) #, required_edges)
    #best_state.curr_size = n

    print("APPROX:", best_state.curr_size)
    start = time.time()
    simplify(state) #, required_edges)
    solve(state, best_state) #, required_edges)
    end = time.time()
    print("MIN:", best_state.curr_size)
    print("TIME:", end - start)
    print("BRANCHES:", state.num_branches)
    print(best_state.curr_size)
    
