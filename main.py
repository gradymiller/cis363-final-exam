import time
import sys
sys.setrecursionlimit(2000)


class State:
    def __init__(self, nodes, best_size):
        self.nodes = nodes
        self.best_size = best_size

    def next_index(self, remaining):
        best_idx = -1
        best_val = -1
        tmp_remaining = remaining

        while tmp_remaining:
            curr = (tmp_remaining & -tmp_remaining).bit_length() - 1
            tmp_remaining &= tmp_remaining - 1

            val = (self.nodes[curr] & remaining).bit_count()
            if val > best_val:
                best_val = val
                best_idx = curr

        return best_idx

    def matching(self, remaining):   
        matched = 0        
        min_required = 0   
        tmp_remaining = remaining

        while tmp_remaining:   
            curr = (tmp_remaining & -tmp_remaining).bit_length() - 1
            tmp_remaining &= tmp_remaining - 1
                           
            if (matched >> curr) & 1:
                continue   
                           
            neighbors = self.nodes[curr] & remaining & ~matched
                           
            if neighbors:  
                curr_neighbor = (neighbors & -neighbors).bit_length() - 1
                matched |= (1 << curr)
                matched |= (1 << curr_neighbor)
                min_required += 1
                           
        return min_required         

    def simplify(self, remaining):
        changes = True
        tmp_remaining = remaining
        added = 0

        while changes:
            changes = False
            scan = tmp_remaining
            while scan:
                curr = (scan & -scan).bit_length() - 1
                scan &= scan - 1

                curr_deg = (self.nodes[curr] & tmp_remaining).bit_count()

                # Remove nodes with no edges
                if curr_deg == 0:
                    tmp_remaining &= ~(1 << curr)
                    changes = True

                # Include when there is a path
                elif curr_deg == 1:
                    neighbors = self.nodes[curr] & tmp_remaining
                    tmp_remaining &= ~(1 << (neighbors.bit_length() - 1))
                    tmp_remaining &= ~(1 << curr)
                    added += 1
                    changes = True
                    break

        return tmp_remaining, added

    def solve(self, remaining, curr_size):

        if curr_size >= self.best_size:
            return

        # Handle the degree <= 1 nodes
        remaining, added = self.simplify(remaining)
        curr_size += added

        # Bound
        if curr_size + self.matching(remaining) >= self.best_size:
            return 

        # Check if solved and better than current best
        if not remaining:
            self.best_size = min(self.best_size, curr_size)

        # Get highest degree index
        idx = self.next_index(remaining)
        if idx == -1:
            self.best_size = min(self.best_size, curr_size)
            return

        # Include
        self.solve(remaining & ~(1 << idx), curr_size + 1)

        # Exclude, and include all neighbors of idx
        neighbors = self.nodes[idx] & remaining
        self.solve(remaining & ~(1 << idx) & ~neighbors, curr_size + neighbors.bit_count())
         

def approximate(nodes, best_size, remaining, curr_size):
    tmp_remaining = remaining
    tmp_curr_size = curr_size

    while tmp_remaining:
        u = (tmp_remaining & -tmp_remaining).bit_length() - 1

        neighbors = nodes[u] & tmp_remaining
        if not neighbors:
            tmp_remaining &= ~(1 << u)
            tmp_curr_size += 1
        else:
            v = (neighbors & -neighbors).bit_length() - 1
            tmp_remaining &= ~(1 << u)
            tmp_remaining &= ~(1 << v)
            tmp_curr_size += 2

    return min(best_size, tmp_curr_size)

if __name__ == "__main__":
    data = sys.stdin.read().split()
    n = int(data[0])
    m = int(data[1])
    nodes = [0] * n

    i = 2
    for _ in range(m):
        u = int(data[i])
        v = int(data[i + 1])
        if (nodes[u] & (1 << v)):
            M -= 1
            continue
        nodes[u] |= (1 << v)
        nodes[v] |= (1 << u)
        i += 2

    initial = (1 << n) - 1 
    best_size = n
    best_size = approximate(nodes, best_size, initial, 0)

    state = State(nodes, best_size)
    start = time.time()
    state.solve(initial, 0)
    end = time.time()
    #print("Time:", end - start)
    print(state.best_size)
