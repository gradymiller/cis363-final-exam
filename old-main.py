import time
import sys

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


def next_index(state, aps):
    best_idx = -1
    best_deg = -1

    # nodes not yet decided
    undecided_mask = ~(state.considered) & state.mask

    flag = False
    if undecided_mask & aps:
        undecided_mask &= aps
        flag = True

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

    return best_idx, flag

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
    neighbors = state.nodes[idx] & state.mask & ~state.considered

    while neighbors:
        curr = (neighbors & -neighbors).bit_length() - 1
        neighbors &= neighbors - 1
        include_node(state, curr)

def approximate(state):

    best_guess = state.curr_size
    while True:
        if state.zeroed == state.mask:
            return state.curr_size

        idx, flag = next_index(state, aps)
        if idx == -1:
            break

        include_node(state, idx)
    return state.curr_size
    

def get_aps(state):
    n = len(state.nodes)
    adj = state.nodes

    disc = [-1] * n
    low = [-1] * n
    parent = [-1] * n
    children_count = [0] * n

    visited = 0
    ap = 0
    time = 0

    for start in range(n):
        if visited & (1 << start):
            continue

        stack = [(start, adj[start], 0)]

        while stack:
            u, neighbors, state_flag = stack.pop()

            if state_flag == 0:

                # mark visited and initialize DFS time
                if not (visited & (1 << u)):
                    visited |= (1 << u)
                    time += 1
                    disc[u] = low[u] = time

                # process neighbors
                if neighbors:
                    v_bit = neighbors & -neighbors
                    v = v_bit.bit_length() - 1
                    neighbors &= neighbors - 1

                    # reprocess current node later
                    stack.append((u, neighbors, 0))

                    if not (visited & (1 << v)):
                        parent[v] = u
                        children_count[u] += 1
                        stack.append((v, adj[v], 0))

                    elif v != parent[u]:
                        low[u] = min(low[u], disc[v])

                else:
                    stack.append((u, 0, 1))

            else:
                p = parent[u]

                if p != -1:
                    low[p] = min(low[p], low[u])

                    # articulation condition (non-root)
                    if parent[p] != -1 and low[u] >= disc[p]:
                        ap |= (1 << p)

                else:
                    # root case
                    if children_count[u] > 1:
                        ap |= (1 << u)

    return ap


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

    active_mask = ~state.considered & state.mask

    for i in range(n):
        if (visited >> i) & 1 or not ((active_mask >> i) & 1):
            continue

        stack = [i]
        nodes = []
        visited |= (1 << i)

        while stack:
            v = stack.pop()
            nodes.append(v)

            neighbors = state.nodes[v] & active_mask

            while neighbors:
                curr = (neighbors & -neighbors).bit_length() - 1
                neighbors &= neighbors - 1

                if ((visited >> curr) & 1) == 0:
                    visited |= (1 << curr)
                    stack.append(curr)

        component = []
        edges_left = 0

        component_mask = 0
        for node in nodes:
            component_mask |= (1 << node)

        for node in nodes:
            bits = 0
            for j, node2 in enumerate(nodes):
                if (state.nodes[node] & component_mask) & (1 << node2):
                    bits |= (1 << j)
                    edges_left += 1

            component.append(bits)

        components.append(component)
        edges_lefts.append(edges_left // 2)

    component_states = []
    for i in range(len(components)):
        new_state = State(components[i], edges_lefts[i])
        component_states.append(new_state)

    return component_states


def solve(state, best_guess, aps):
    state.num_branches += 1

    simplify(state)

    # Return if solved, update if better than best_state
    if state.edges_left == 0:
        if state.curr_size < best_guess:
            best_guess = state.curr_size
        return best_guess

    idx, flag = next_index(state, aps)
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

    #if state.num_branches < 20:
    if flag:
        aps &= ~(1 << idx)

    avg_degree = state.edges_left // ~state.considered.bit_count()

    if not aps and state.num_branches < 10 and avg_degree < 3 and ~state.considered.bit_count() > 20: 
        aps = get_aps(state)

    state_copy = state.copy()

    # INCLUDE
    include_node(state_copy, idx)
    if aps & (1 << idx):
        include_solution = solve_components(state_copy, aps)
    else:
        include_solution = solve(state_copy, best_guess, aps)

    if include_solution < best_guess:
        best_guess = include_solution
    
    # EXCLUDE
    exclude_node(state, idx)
    if aps & (1 << idx):
        exclude_solution = solve_components(state, aps)
    else:
        exclude_solution = solve(state, best_guess, aps)

    if exclude_solution < best_guess:
        best_guess = exclude_solution

    return best_guess
         
def solve_components(state, aps):
    total = state.curr_size
    component_states = get_components(state)
    for c in component_states:
        print(f"{state.num_branches}: {c.nodes}")
    
    for c_state in component_states:
        c_copy = c_state.copy()
        c_best_guess = approximate(c_copy)
        total += solve(c_state, c_best_guess, aps)
    
    return total


if __name__ == "__main__":
    data = sys.stdin.read().split()
    n = int(data[0])
    m = int(data[1])

    nodes = [0] * n
    matched = set()
    #required_edges = [0] * n
    #min_required = 0

    idx = 2
    for _ in range(m):
        u = int(data[idx])
        v = int(data[idx+1])
        if (nodes[u] & (1 << v)):
            m -= 1
            continue
        idx += 2

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
    avg_degree = state.edges_left // ~state.considered.bit_count()
    if avg_degree < 5:
        aps = get_aps(state)
    else:
        aps = 0

    simplify(best_state)
    best_guess = approximate(best_state)

    #print("APPROX:", best_guess)
    start = time.time()
    simplify(state)
    best = solve(state, best_guess, aps)
    end = time.time()
    #print("TIME:", end - start)
    #print("BRANCHES:", state.num_branches)
    print(best)
