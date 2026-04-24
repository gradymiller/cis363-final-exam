#include <iostream>
#include <vector>
#include <bitset>
#include <bit>
#include <algorithm>

// GLOBAL VARS
int N;
int M;
std::vector NODES;
int BEST_SIZE;


int next_index(remaining) {
	int best_idx = -1;
	int best_val = -1;
	std::bitset<N> tmp_remaining = remaining;

	int curr;
	int val;
	while (tmp_remaining):
		curr = std::countr_zero(tmp_remaining);
		tmp_remaining &= (tmp_remaining - 1);

		val = std::popcount(NODES[curr] & remaining);
		if (val > best_val):
			best_val = val;
			best_idx = curr;

	return best_idx;
}

void approximate(remaining, curr_size){
	std::bitset<N> tmp_remaining = remaining;
	int tmp_curr_size = curr_sizes;

	int u;
	int v;
	std::bitset<N> neighbors;
	while (tmp_remaining) {
		u = std::countr_zero(tmp_remaining);

		neighbors = NODES[u] & tmp_remaining;
		if (!neighbors) {
			tmp_remaining.reset(u);
			tmp_curr_size++;
		} else {
			v = std::countr_zero(neighbors);
			tmp_remaining.reset(u);
			tmp_remaining.reset(v);
			tmp_curr_size += 2;
		}
			
	}
	BEST_SIZE = std::min(BEST_SIZE, tmp_curr_size);
}

int matching(remaining) {
	std:bitset<N> matched;
	int min_required;
	std::bitset<N> tmp_remaining = remaining;

	int curr;
	int curr_neighbor;
	std::bitset<N> neighbors;
	while (tmp_remaining) {
		curr = std::countr_zero(tmp_remaining);
		tmp_remaining &= (remaining - 1);

		if (matched.test(curr)) {
			continue;
		}

		neighbors = NODES[curr] & remaining & ~matched;

		if (neighbors) {
			curr_neighbor = std::countr_zero(neighbors);
			matched.set(curr);
			matched.set(curr_neighbor);
			min_required += 1;
		}
	}
	return min_required;
}


int main() {
	// Read in data
	
	std::bitset<N> initial;
	initial.set();

	BEST_SIZE = N;
	approximate(initial, 0);

	solve(initial, 0);
	std::cout << BEST_SIZE;
}
