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


def approximate(remaining, curr_size):
    global BEST_SIZE
    tmp_remaining = remaining
    tmp_curr_size = curr_size

    while tmp_remaining:
        u = (tmp_remaining & -tmp_remaining).bit_length() - 1

        neighbors = NODES[u] & tmp_remaining
        if not neighbors:
            tmp_remaining &= ~(1 << u)
            tmp_curr_size += 1
        else:
            v = (neighbors & -neighbors).bit_length() - 1
            tmp_remaining &= ~(1 << u)
            tmp_remaining &= ~(1 << v)
            tmp_curr_size += 2
    BEST_SIZE = min(BEST_SIZE, tmp_curr_size)
    

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


def greedy_matching(remaining):
    global NODES
    matched = 0
    min_required = 0
    tmp_remaining = remaining
    candidates = remaining

    while candidates:
        best = -1
        best_deg = len(NODES)
        scan = candidates

        while scan:
            curr = (scan & -scan).bit_length() - 1
            scan &= scan - 1

            if (matched >> curr) & 1:
                continue

            deg = NODES[curr] & tmp_remaining

            if deg == 1:
                best = curr
                best_deg = 1
                break

            if deg < best_deg:
                best = curr
                best_deg = deg

        if best == -1:
            break

        neighbors = NODES[best] & tmp_remaining & ~matched

        if neighbors:
            u = (neighbors & -neighbors).bit_length() - 1
            matched |= (1 << u)
            matched |= (1 << best)
            min_required += 1

        candidates &= ~(1 << best)

    return min_required



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


def solve(remaining, curr_size):
    global BEST_SIZE
    global NODES

    if curr_size >= BEST_SIZE:
        return

    # Handle the degree <= 1 nodes
    remaining, added = simplify(remaining)
    curr_size += added

    # Bound
    if curr_size + greedy_matching(remaining) >= BEST_SIZE:
        return 

    # Check if solved and better than current best
    if not remaining:
        BEST_SIZE = min(BEST_SIZE, curr_size)
        return

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
         

if __name__ == "__main__":
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
    MEMO = {}


    def next_index(remaining):
        nonlocal NODES
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


    def approximate(remaining, curr_size):
        nonlocal BEST_SIZE
        tmp_remaining = remaining
        tmp_curr_size = curr_size

        while tmp_remaining:
            u = (tmp_remaining & -tmp_remaining).bit_length() - 1

            neighbors = NODES[u] & tmp_remaining
            if not neighbors:
                tmp_remaining &= ~(1 << u)
                tmp_curr_size += 1
            else:
                v = (neighbors & -neighbors).bit_length() - 1
                tmp_remaining &= ~(1 << u)
                tmp_remaining &= ~(1 << v)
                tmp_curr_size += 2
        BEST_SIZE = min(BEST_SIZE, tmp_curr_size)
        

    def matching(remaining):   
        nonlocal NODES
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


    def simplify(remaining):
        nonlocal BEST_SIZE
        nonlocal NODES
        changes = True
        tmp_remaining = remaining
        added = 0

        while changes:
            changes = False
            scan = tmp_remaining
            while scan:
                curr = (scan & -scan).bit_length() - 1
                scan &= scan - 1
                
                neighbors = NODES[curr] & tmp_remaining
                curr_deg = (neighbors).bit_count()

                # Remove nodes with no edges
                if curr_deg == 0:
                    tmp_remaining &= ~(1 << curr)
                    changes = True

                # Include when there is a path
                elif curr_deg == 1:
                    tmp_remaining &= ~(1 << (neighbors.bit_length() - 1))
                    tmp_remaining &= ~(1 << curr)
                    added += 1
                    changes = True
                    break

                # Include both neighbord of degree 2 vertex if they are also neighbors
                elif curr_deg == 2:
                    neighbor1 = (neighbors & -neighbors).bit_length() - 1
                    neighbors &= neighbors - 1

                    neighbor2 = (neighbors & -neighbors).bit_length() - 1
                    
                    if NODES[neighbor1] & (1 << neighbor2):
                        tmp_remaining &= ~((1 << neighbor1) | (1 << neighbor2))
                        tmp_remaining &= ~(1 << curr)
                        added += 2
                        changes = True
                        break

        return tmp_remaining, added


    def solve(remaining, curr_size):
        nonlocal BEST_SIZE, MEMO
        nonlocal NODES
        nonlocal N

        if curr_size >= BEST_SIZE:
            return

        if remaining in MEMO and MEMO[remaining] <= cur_size:
            return
       
        count_remaining = remaining.bit_count()

        if count_remaining <= (N-10) and count_remaining >= 15:
            MEMO[remaining] = curr_size

        # Handle the degree <= 1 nodes
        remaining, added = simplify(remaining)
        curr_size += added

        # Check if solved and better than current best
        if not remaining:
            BEST_SIZE = min(BEST_SIZE, curr_size)
            return
        
        # Bound
        if curr_size + matching(remaining) >= BEST_SIZE:
            return 

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
             
    approximate(initial, 0)

    #start = time.time()

    solve(initial, 0)
    #end = time.time()
    #print("Time:", end - start)
    print(BEST_SIZE)

if __name__ == "__main__":
    solver()
