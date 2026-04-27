#include <iostream>
#include <vector>
#include <bitset>
#include <bit>
#include <algorithm>
#include <utility>


int next_index(const std::vector<std::bitset<200>>& nodes, const std::bitset<200>& remaining) {
	int best_idx = -1;
	int best_val = -1;
	std::bitset<200> tmp_remaining = remaining;

	size_t curr;
	int val;
	while (tmp_remaining.any()) {
		curr = tmp_remaining._Find_first();
		tmp_remaining.reset(curr);

		val = (nodes[curr] & remaining).count();
		if (val > best_val) {
			best_val = val;
			best_idx = curr;
		}
	}
	return best_idx;
}

void approximate(const std::vector<std::bitset<200>>& nodes, int& best_size, const std::bitset<200>& remaining, const int& curr_size) {
	std::bitset<200> tmp_remaining = remaining;
	int tmp_curr_size = curr_size;

	int u;
	int v;
	std::bitset<200> neighbors;
	while (tmp_remaining.any()) {
		u = tmp_remaining._Find_first();

		neighbors = nodes[u] & tmp_remaining;
		if (neighbors.none()) {
			tmp_remaining.reset(u);
			tmp_curr_size++;
		} else {
			v = neighbors._Find_first();
			tmp_remaining.reset(u);
			tmp_remaining.reset(v);
			tmp_curr_size += 2;
		}
			
	}
	best_size = std::min(best_size, tmp_curr_size);
}

int matching(const std::vector<std::bitset<200>>& nodes, const std::bitset<200>& remaining) {
	std::bitset<200> matched;
	int min_required = 0;
	std::bitset<200> tmp_remaining = remaining;

	int curr;
	int curr_neighbor;
	std::bitset<200> neighbors;
	while (tmp_remaining.any()) {
		curr = tmp_remaining._Find_first();
		tmp_remaining.reset(curr);

		if (matched.test(curr)) {
			continue;
		}

		neighbors = nodes[curr] & remaining & ~matched;

		if (neighbors.any()) {
			curr_neighbor = neighbors._Find_first();
			matched.set(curr);
			matched.set(curr_neighbor);
			min_required += 1;
		}
	}
	return min_required;
}


int greedy_matching(const std::vector<std::bitset<200>>& nodes, const std::bitset<200>& remaining) {
	std::bitset<200> matched = 0;
	int min_required = 0;
	std::bitset<200> tmp_remaining = remaining;
	std::bitset<200> candidates = tmp_remaining;

	while (candidates.any()) {
		int best = -1;
		int deg;
		int best_deg = nodes.size();
		std::bitset<200> scan = candidates;

		while (scan.any()) {
			size_t curr = scan._Find_first();
			scan.reset(curr);

			if (matched.test(curr)) continue;

			deg = (nodes[curr] & tmp_remaining).count();

			if (deg == 1) {
				best = curr;
				best_deg = 1;
				break;
			}

			if (deg < best_deg) {
				best = curr;
				best_deg = deg;
			}
		}

		if (best == -1) break;

		candidates.reset(best);

		std::bitset<200> neighbors = nodes[best] & tmp_remaining & ~matched;

		if (neighbors.any()) {
			int u = neighbors._Find_first();
			matched.set(u);
			matched.set(best);
			min_required += 1;

			candidates.reset(u);
			tmp_remaining.reset(best);
			tmp_remaining.reset(u);
		} else {
			tmp_remaining.reset(best);
		}
	}
	return min_required;
}

std::pair<std::bitset<200>, int> simplify(const std::vector<std::bitset<200>>& nodes, const std::bitset<200>& remaining) {
	bool changes = true;
	std::bitset<200> tmp_remaining = remaining;
	int added = 0;

	while (changes) {
		changes = false;
		std::bitset<200> scan = tmp_remaining;
		
		int curr;
		int curr_deg;
		while (scan.any()) {
			curr = scan._Find_first();
			scan.reset(curr);

			curr_deg = (nodes[curr] & tmp_remaining).count();

			if (curr_deg == 0) {
				tmp_remaining.reset(curr);
			} else if (curr_deg == 1) {
				std::bitset<200> neighbors = nodes[curr] & tmp_remaining;
				tmp_remaining.reset(neighbors._Find_first());
				tmp_remaining.reset(curr);
				added++;
				changes = true;
				break;
			}
		}
	}
	return std::pair(tmp_remaining, added);
}

void solve(const std::vector<std::bitset<200>>& nodes, int& best_size, std::bitset<200> remaining, int curr_size) {
	if (curr_size >= best_size) return;

	int added;
	auto p = simplify(nodes, remaining);
	remaining = p.first;
	added = p.second;

	curr_size += added;

	if (curr_size + matching(nodes, remaining) >= best_size) return;

	if (remaining.none()) {
		best_size = std::min(best_size, curr_size);
		return;
	}

	int idx = next_index(nodes, remaining);
	if (idx == -1) {
		best_size = std::min(best_size, curr_size);
		return;
	}

	solve(nodes, best_size, remaining.reset(idx), curr_size + 1);

	std::bitset<200> neighbors = nodes[idx] & remaining;
	solve(nodes, best_size, remaining.reset(idx) & ~neighbors, curr_size + neighbors.count());
}

int main() {
	int n, m;
	std::cin >> n >> m;
	std::vector<std::bitset<200>> nodes(n);

	int u;
	int v;
	for (int i = 0; i < m; i++) {
		std::cin >>	u >> v;
		nodes[u].set(v);
		nodes[v].set(u);
	}
	
	std::bitset<200> initial;
	for (int i = 0; i < n; i++) initial.set(i);

	int best_size = n;
	approximate(nodes, best_size, initial, 0);

	solve(nodes, best_size, initial, 0);
	std::cout << best_size;
	
	return 0;
}
