import sys
import time

# Increase recursion depth for deep search trees
sys.setrecursionlimit(2000)

class Solver:
    def __init__(self, n, edges):
        self.n = n
        self.adj = [set() for _ in range(n)]
        for u, v in edges:
            if u != v:
                self.adj[u].add(v)
                self.adj[v].add(u)
        self.best_size = n

    def get_max_matching_bound(self, active_nodes, current_adj):
        """Standard lower bound: size of any maximal matching."""
        match_size = 0
        visited = set()
        for u in active_nodes:
            if u not in visited:
                for v in current_adj[u]:
                    if v in active_nodes and v not in visited:
                        visited.add(u)
                        visited.add(v)
                        match_size += 1
                        break
        return match_size

    def solve(self):
        # Find all connected components to solve them independently
        total_mvc = 0
        visited_global = [False] * self.n
        
        for i in range(self.n):
            if not visited_global[i] and self.adj[i]:
                component_nodes = []
                stack = [i]
                visited_global[i] = True
                while stack:
                    u = stack.pop()
                    component_nodes.append(u)
                    for v in self.adj[u]:
                        if not visited_global[v]:
                            visited_global[v] = True
                            stack.append(v)
                
                # Solve MVC for this specific component
                self.best_size = len(component_nodes)
                comp_adj = {node: self.adj[node].copy() for node in component_nodes}
                self._branch_and_bound(set(component_nodes), comp_adj, 0)
                total_mvc += self.best_size
                
        return total_mvc

    def _branch_and_bound(self, nodes, adj, current_count):
        # Prune if we can't possibly beat the best found size
        if current_count + self.get_max_matching_bound(nodes, adj) >= self.best_size:
            return

        # If no edges left, we found a cover
        remaining_nodes = [v for v in nodes if adj[v]]
        if not remaining_nodes:
            self.best_size = min(self.best_size, current_count)
            return

        # 1. Degree-1 Optimization: Force the neighbor of a degree-1 node
        for v in remaining_nodes:
            if len(adj[v]) == 1:
                neighbor = next(iter(adj[v]))
                # Must pick the neighbor
                self._include_node(neighbor, nodes, adj, current_count)
                return

        # 2. Branching: Pick vertex with the highest degree
        v = max(remaining_nodes, key=lambda x: len(adj[x]))

        # OPTION A: Include v in the vertex cover
        orig_adj_v = adj[v].copy()
        saved_adj = {neighbor: adj[neighbor].copy() for neighbor in orig_adj_v}
        
        # Remove v and all its edges
        for neighbor in orig_adj_v:
            adj[neighbor].remove(v)
        adj[v] = set()
        
        self._branch_and_bound(nodes, adj, current_count + 1)
        
        # Backtrack Option A
        for neighbor in orig_adj_v:
            adj[neighbor] = saved_adj[neighbor]
        adj[v] = orig_adj_v

        # OPTION B: Exclude v (This forces all neighbors of v into the cover)
        neighbors_v = list(adj[v])
        if current_count + len(neighbors_v) < self.best_size:
            # Snapshot for backtracking
            snapshot = {}
            for n_v in neighbors_v:
                snapshot[n_v] = adj[n_v].copy()
                for neighbor_of_n in adj[n_v]:
                    if neighbor_of_n not in snapshot:
                        snapshot[neighbor_of_n] = adj[neighbor_of_n].copy()
            
            # Include all neighbors
            added_count = 0
            for n_v in neighbors_v:
                if adj[n_v]: # If not already covered
                    self._remove_node_logic(n_v, adj)
                    added_count += 1
            
            self._branch_and_bound(nodes, adj, current_count + added_count)
            
            # Backtrack Option B
            for node_id, edges in snapshot.items():
                adj[node_id] = edges

    def _remove_node_logic(self, v, adj):
        """Helper to effectively remove a node from the graph by clearing incident edges."""
        for neighbor in adj[v]:
            adj[neighbor].remove(v)
        adj[v] = set()

    def _include_node(self, v, nodes, adj, current_count):
        """Forces a node into the cover and continues."""
        orig_adj_v = adj[v].copy()
        saved_adj = {neighbor: adj[neighbor].copy() for neighbor in orig_adj_v}
        self._remove_node_logic(v, adj)
        self._branch_and_bound(nodes, adj, current_count + 1)
        # Backtrack
        for neighbor in orig_adj_v:
            adj[neighbor] = saved_adj[neighbor]
        adj[v] = orig_adj_v

def main():
    input_data = sys.stdin.read().split()
    if not input_data: return
    
    N = int(input_data[0])
    M = int(input_data[1])
    
    edges = []
    idx = 2
    for _ in range(M):
        u = int(input_data[idx])
        v = int(input_data[idx+1])
        edges.append((u, v))
        idx += 2
        
    solver = Solver(N, edges)
    print(solver.solve())

if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print(f"Time: {end-start}")
