import time

class State:
    def __init__(self, nodes, edges_left):
        self.nodes = nodes[:]             
        self.curr_size = 0
        self.considered = 0
        self.zeroed = 0
        self.edges_left = edges_left
        self.mask = (1 << len(nodes)) - 1
        #self.min_required = )
        self.num_branches = 0
        self.degrees = [i.bit_count() for i in nodes]

    def copy(self):
        new_state = State.__new__(State)

        new_state.nodes = self.nodes[:]
        new_state.curr_size = self.curr_size
        new_state.considered = self.considered
        new_state.zeroed = self.zeroed
        new_state.edges_left = self.edges_left
        new_state.mask = self.mask
        # new_state.min_required = self.min_required
        new_state.num_branches = self.num_branches
        new_state.degrees = self.degrees[:]
        return new_state


def next_index(state):
    best_idx = -1
    best_deg = -1

    # nodes not yet decided
    undecided_mask = ~(state.considered) & state.mask

    while undecided_mask:

        # Get index of least significant bit of undecided mask
        curr = (undecided_mask & -undecided_mask).bit_length() - 1

        # Remove the least significant bit
        undecided_mask &= undecided_mask - 1

        # Keep if better
        val = state.degrees[curr]
        if val > best_deg:
            best_deg = val
            best_idx = curr
    """
    for i, deg in enumerate(state.degrees):
        if deg > best_deg:
            best_deg = deg
            best_idx = i
    """ 

    return best_idx

def include_node(state, idx):

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
        state.degrees[curr] -= 1
        #if required_edges[curr] & (1 << idx) != 0:
            #state.min_required -= 1

        # If that neighbor becomes empty, mark it in zeroed
        if state.nodes[curr] == 0:
            state.zeroed |= (1 << curr)

    # Update the state after all neighbors have the included node removed
    state.nodes[idx] = 0
    state.degrees[idx] = 0
    state.zeroed |= (1 << idx)
    state.curr_size += 1
    state.considered = state.considered | (1 << idx)


def exclude_node(state, idx):
    state.considered |= (1 << idx)
    neighbors = state.nodes[idx] & state.mask

    while neighbors:
        curr = (neighbors & -neighbors).bit_length() - 1
        neighbors &= neighbors - 1
        include_node(state, curr)

def approximate(state):

    best_guess = state.curr_size
    while True:
        if state.zeroed == state.mask:
            return state.curr_size

        idx = next_index(state)
        if idx == -1:
            break

        include_node(state, idx)
    return state.curr_size
    

def matching(state):   
    matched = 0        
    min_required = 0   
                       
    remaining = ~state.considered & state.mask
                       
    while remaining:   
        curr = (remaining & -remaining).bit_length() - 1
        remaining &= remaining - 1
                       
        if (matched >> curr) & 1:
            continue   
                       
        neighbors = state.nodes[curr] & remaining & ~matched
                       
        if neighbors:  
            curr_neighbor = (neighbors & -neighbors).bit_length() - 1
                       
            matched |= (1 << curr)
            matched |= (1 << curr_neighbor)
            min_required += 1
                       
    return min_required         


def greedy_matching(state):
    matched = 0
    min_required = 0

    remaining = ~state.considered & state.mask
    candidates = remaining

    while candidates:

        best = -1
        best_deg = 10**9

        scan = candidates

        while scan:
            curr = (scan & -scan).bit_length() - 1
            scan &= scan - 1

            if (matched >> curr) & 1:
                continue

            deg = state.degrees[curr]

            if deg == 1:
                best = curr
                best_deg = 1
                break

            if deg < best_deg:
                best = curr
                best_deg = deg

        if best == -1:
            break

        neighbors = state.nodes[best] & remaining & ~matched

        if neighbors:
            u = (neighbors & -neighbors).bit_length() - 1

            matched |= (1 << u)
            matched |= (1 << best)
            min_required += 1

        candidates &= ~(1 << best)

    return min_required 

def simplify(state):

    changes = True
    while changes:
        changes = False
        not_considered = ~(state.considered) & state.mask
        while not_considered:
            curr = (not_considered & -not_considered).bit_length() - 1
            not_considered &= not_considered - 1

            curr_deg = state.degrees[curr]
            curr_node = state.nodes[curr] & state.mask

            # Remove nodes with degree zero
            # And include neighbors of nodes with degree 1
            if curr_deg <= 1 :
                exclude_node(state, curr)
                changes = True


def get_components(state):
    components = []
    edges_lefts = []
    visited = 0
    n = len(state.nodes)
    
    for i in range(n):
        if (visited >> i) & 1 or ((state.considered & state.mask) >> i) & 1:
            continue

        stack = [i]
        nodes = []

        visited |= (1 << i)

        while stack:
            v = stack.pop()
            nodes.append(v)

            neighbors = state.nodes[v]

            while neighbors:
                curr = (neighbors & -neighbors).bit_length() - 1
                neighbors &= neighbors - 1

                if ((visited >> curr) & 1) == 0:
                    visited |= (1 << curr)
                    stack.append(curr)

        component = []
        edges_left = 0
        for node in nodes: 
            bits = 0
            for i, node2 in enumerate(nodes):
                if (1 << node2) & state.nodes[node]:
                    bits |= (1 << i)
                    edges_left += 1

            component.append(bits)
        components.append(component)
        edges_lefts.append(edges_left // 2)

    if len(components) <= 1:
        return

    component_states = []
    for i in range(len(components)):
        state = State(components[i], edges_lefts[i])
        component_states.append(state)

    return component_states


def solve(state, best_guess):
    state.num_branches += 1

    simplify(state)

    # Return if solved, update if better than best_state
    if state.edges_left == 0:
        if state.curr_size < best_guess:
            best_guess = state.curr_size
        return best_guess

    idx = next_index(state)    
    if idx == -1:
        return best_guess
    
    # Bound
    max_edges = (state.nodes[idx] & state.mask).bit_count()
    if max_edges == 0:
        return best_guess

    max_edge_bound = (state.edges_left + max_edges - 1) // max_edges     
    matching_bound = matching(state)
    #greedy_matching_bound = greedy_matching(state)

    bound = max(max_edge_bound, matching_bound)
    #print(f"{max_edge_bound}, {matching_bound}, {greedy_matching_bound}")

    if state.curr_size + bound >= best_guess:
        return best_guess
    
    remaining_vertices = (~state.considered & state.mask).bit_count()
    component_states = None
   
    if remaining_vertices >= 20 and state.edges_left <= remaining_vertices * 3:
        component_states = get_components(state)

    # print(len(component_states))
    if component_states:
        best = state.curr_size
        for c_state in component_states:
            c_copy = c_state.copy()
            c_best_guess = approximate(c_copy)
            best += solve(c_state, c_best_guess)
        if best < best_guess:
            best_guess = best

    else:    
        # add vertex on one end of edge
        state_copy = state.copy()
        include_node(state_copy, idx)
        solution = solve(state_copy, best_guess)
        if solution < best_guess:
            best_guess = solution
        
        # add vertex on other edge
        exclude_node(state, idx)
        solution = solve(state, best_guess)
        if solution < best_guess:
            best_guess = solution

    return best_guess
         

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
    state = State(nodes, m)
    best_state = State(nodes[:], m)

    simplify(best_state)
    best_guess = approximate(best_state)

    # print("APPROX:", best_guess)
    start = time.time()
    simplify(state)
    best = solve(state, best_guess)
    end = time.time()
    # print("MIN:", best_guess)
    print("TIME:", end - start)
    # print("BRANCHES:", state.num_branches)
    print(best)
