import time

class State:
    def __init__(self, nodes, edges_left):
        self.nodes = nodes[:]             
        self.curr_size = 0
        self.considered = 0
        self.zeroed = 0
        self.edges_left = edges_left
        self.mask = (1 << len(nodes)) - 1
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
        new_state.num_branches = self.num_branches
        new_state.degrees = self.degrees[:]
        return new_state


def next_index(state):
    best_idx = -1
    best_deg = -1
    undecided_mask = ~(state.considered) & state.mask

    while undecided_mask:
        curr = (undecided_mask & -undecided_mask).bit_length() - 1
        undecided_mask &= undecided_mask - 1
        val = state.degrees[curr]
        if val > best_deg:
            best_deg = val
            best_idx = curr

    return best_idx


def include_node(state, idx):
    if (state.considered >> idx) & 1:
        return

    neighbors = state.nodes[idx] & state.mask
    state.edges_left -= neighbors.bit_count()

    while neighbors:
        curr = (neighbors & -neighbors).bit_length() - 1
        neighbors &= neighbors - 1

        state.nodes[curr] &= ~(1 << idx)
        state.degrees[curr] -= 1

        if state.nodes[curr] == 0:
            state.zeroed |= (1 << curr)

    state.nodes[idx] = 0
    state.degrees[idx] = 0
    state.zeroed |= (1 << idx)
    state.curr_size += 1
    state.considered |= (1 << idx)


def exclude_node(state, idx):
    state.considered |= (1 << idx)
    neighbors = state.nodes[idx] & state.mask

    while neighbors:
        curr = (neighbors & -neighbors).bit_length() - 1
        neighbors &= neighbors - 1
        include_node(state, curr)


def approximate(state):
    while True:
        if state.zeroed == state.mask:
            return state.curr_size

        idx = next_index(state)
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

                if not (visited & (1 << u)):
                    visited |= (1 << u)
                    time += 1
                    disc[u] = low[u] = time

                if neighbors:
                    v_bit = neighbors & -neighbors
                    v = v_bit.bit_length() - 1
                    neighbors &= neighbors - 1

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

                    if parent[p] != -1 and low[u] >= disc[p]:
                        ap |= (1 << p)

                else:
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

            if state.degrees[curr] <= 1:
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

                if not (visited >> curr) & 1:
                    visited |= (1 << curr)
                    stack.append(curr)

        idx_map = {node: idx for idx, node in enumerate(nodes)}
        component_mask = 0

        for node in nodes:
            component_mask |= (1 << node)

        k = len(nodes)
        component = [0] * k
        edges_left = 0

        for node in nodes:
            nbrs = state.nodes[node] & component_mask
            edges_left += nbrs.bit_count()

            bits = 0
            while nbrs:
                v = (nbrs & -nbrs).bit_length() - 1
                nbrs &= nbrs - 1
                bits |= (1 << idx_map[v])

            component[idx_map[node]] = bits

        components.append(component)
        edges_lefts.append(edges_left // 2)

    return [State(components[i], edges_lefts[i]) for i in range(len(components))]


def solve(state, best_guess, aps):
    state.num_branches += 1

    simplify(state)

    if state.edges_left == 0:
        return min(best_guess, state.curr_size)

    idx = next_index(state)
    if idx == -1:
        return best_guess

    max_edges = (state.nodes[idx] & state.mask).bit_count()
    if max_edges == 0:
        return best_guess

    bound = max(
        (state.edges_left + max_edges - 1) // max_edges,
        matching(state)
    )

    if state.curr_size + bound >= best_guess:
        return best_guess

    #if state.num_branches % 5 == 0:
        #aps = get_aps(state)

    component_states = []
    if (aps >> idx) & 1:
        component_states = get_components(state)

    if len(component_states) > 1:
        best = state.curr_size
        for c_state in component_states:
            best = solve(c_state, best, aps)
        return min(best_guess, best)

    state_copy = state.copy()
    include_node(state_copy, idx)
    best_guess = min(best_guess, solve(state_copy, best_guess, aps))

    exclude_node(state, idx)
    best_guess = min(best_guess, solve(state, best_guess, aps))

    return best_guess


if __name__ == "__main__":
    n, m = map(int, input().split())

    nodes = [0] * n

    for _ in range(m):
        u, v = map(int, input().split())

        if nodes[u] & (1 << v):
            continue

        nodes[u] |= (1 << v)
        nodes[v] |= (1 << u)

    state = State(nodes, m)
    best_state = State(nodes[:], m)

    aps = get_aps(state)

    simplify(best_state)
    best_guess = approximate(best_state)

    print("APPROX:", best_guess)

    start = time.time()
    simplify(state)
    best = solve(state, best_guess, aps)
    end = time.time()

    print("TIME:", end - start)
    print("BRANCHES:", state.num_branches)
    print(best)
