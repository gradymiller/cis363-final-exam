import time
import sys
sys.setrecursionlimit(2000)


def next_index(remaining):
    global NODES
    best_idx = -1
    best_val = -1
    tmp_remaining = remaining

    while tmp_remaining:
        curr = (tmp_remaining & -tmp_remaining).bit_length() - 1
        tmp_remaining &= tmp_remaining - 1

        val = (NODES[curr] & remaining).bit_count()
        if val > best_val:
            best_val = val
            best_idx = curr

    return best_idx

"""
def approximate(remaining, curr_size):
    global BEST_SIZE
    tmp_remaining = remaining
    tmp_curr_size = curr_size

    while True:
        if not tmp_remaining:
            BEST_SIZE = min(BEST_SIZE, tmp_curr_size)
            return

        idx = next_index(tmp_remaining)
        if idx == -1:
            BEST_SIZE = min(BEST_SIZE, tmp_curr_size)
            return

        tmp_remaining &= ~(1 << idx)
        tmp_curr_size += 1
"""
    

def matching(remaining):   
    global NODES
    matched = 0        
    min_required = 0   
    tmp_remaining = remaining

    while tmp_remaining:   
        curr = (tmp_remaining & -tmp_remaining).bit_length() - 1
        tmp_remaining &= tmp_remaining - 1
                       
        if (matched >> curr) & 1:
            continue   
                       
        neighbors = NODES[curr] & remaining & ~matched
                       
        if neighbors:  
            curr_neighbor = (neighbors & -neighbors).bit_length() - 1
            matched |= (1 << curr)
            matched |= (1 << curr_neighbor)
            min_required += 1
                       
    return min_required         

"""
def simplify(remaining):
    global BEST_SIZE
    global NODES
    changes = True
    tmp_remaining = remaining
    added = 0

    while changes:
        changes = False
        scan = tmp_remaining
        while scan:
            curr = (scan & -scan).bit_length() - 1
            scan &= scan - 1

            curr_deg = (NODES[curr] & tmp_remaining).bit_count()

            # Remove nodes with no edges
            if curr_deg == 0:
                tmp_remaining &= ~(1 << curr)
                changes = True

            # Include when there is a path
            elif curr_deg == 1:
                neighbors = NODES[curr] & tmp_remaining
                tmp_remaining &= ~(1 << (neighbors.bit_length() - 1))
                tmp_remaining &= ~(1 << curr)
                added += 1
                changes = True
                break

    return tmp_remaining, added
"""

def solve(remaining, curr_size):
    global BEST_SIZE
    global NODES

    if curr_size >= BEST_SIZE:
        return

    # Handle the degree <= 1 nodes
    #remaining, added = simplify(remaining)
    #curr_size += added

    # Bound
    if curr_size + matching(remaining) >= BEST_SIZE:
        return 

    # Check if solved and better than current best
    if not remaining:
        BEST_SIZE = min(BEST_SIZE, curr_size)

    # Get highest degree index
    idx = next_index(remaining)
    if idx == -1:
        BEST_SIZE = min(BEST_SIZE, curr_size)
        return

    # Include
    solve(remaining & ~(1 << idx), curr_size + 1)

    # Exclude, and include all neighbors of idx
    neighbors = NODES[idx] & remaining
    solve(remaining & ~(1 << idx) & ~neighbors, curr_size + neighbors.bit_count())

def main():
    global NODES
    global BEST_SIZE
    data = sys.stdin.read().split()
    N = int(data[0])
    M = int(data[1])
    NODES = [0] * N

    i = 2
    for _ in range(M):
        u = int(data[i])
        v = int(data[i + 1])
        if (NODES[u] & (1 << v)):
            M -= 1
            continue
        NODES[u] |= (1 << v)
        NODES[v] |= (1 << u)
        i += 2

    initial = (1 << N) - 1 
    BEST_SIZE = N
    
    #approximate(initial, 0)
    #start = time.time()
    solve(initial, 0)
    #end = time.time()
    #print("Time:", end - start)
    #print(BEST_SIZE)


if __name__ == "__main__":
    NODES = []
    BEST_SIZE = 0
    main()
