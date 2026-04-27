import cProfile
import pstats
import glob
import io
import sys

import profiled as solver


def run_all():
    pr = cProfile.Profile()
    pr.enable()

    for path in glob.glob("test-cases/*.txt"):
        with open(path) as f:
            data = f.read().split()

        sys.stdin = io.StringIO(" ".join(data))

        solver.main()

    pr.disable()

    return pr


if __name__ == "__main__":
    pr = run_all()

    # Aggregate stats
    s = pstats.Stats(pr)
    s.strip_dirs()
    s.sort_stats("tottime")

    print("\n=== FUNCTION DATA ===")
    s.print_stats(10)
