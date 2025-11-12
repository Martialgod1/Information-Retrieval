import argparse
from collections import defaultdict


def pagerank(graph, damping=0.85, max_iter=100, tol=1e-6):
    nodes = sorted(set(graph.keys()) | {v for vs in graph.values() for v in vs})
    if not nodes:
        return {}
    N = len(nodes)
    idx = {n: i for i, n in enumerate(nodes)}
    outdeg = {n: len(graph.get(n, [])) for n in nodes}
    pr = {n: 1.0 / N for n in nodes}
    for _ in range(max_iter):
        new_pr = {n: (1 - damping) / N for n in nodes}
        for u in nodes:
            if outdeg[u] == 0:
                share = damping * (pr[u] / N)
                for v in nodes:
                    new_pr[v] += share
            else:
                share = damping * (pr[u] / outdeg[u])
                for v in graph.get(u, []):
                    new_pr[v] += share
        diff = sum(abs(new_pr[n] - pr[n]) for n in nodes)
        pr = new_pr
        if diff < tol:
            break
    return pr


def hits(graph, max_iter=100, tol=1e-6):
    nodes = sorted(set(graph.keys()) | {v for vs in graph.values() for v in vs})
    if not nodes:
        return {}, {}
    # Build in-links
    in_links = defaultdict(set)
    for u, vs in graph.items():
        for v in vs:
            in_links[v].add(u)
    auth = {n: 1.0 for n in nodes}
    hub = {n: 1.0 for n in nodes}
    for _ in range(max_iter):
        # Update authority
        new_auth = {n: sum(hub.get(u, 0.0) for u in in_links.get(n, [])) for n in nodes}
        # Normalize
        norm_a = sum(v * v for v in new_auth.values()) ** 0.5 or 1.0
        for n in nodes:
            new_auth[n] /= norm_a
        # Update hub
        new_hub = {n: sum(new_auth.get(v, 0.0) for v in graph.get(n, [])) for n in nodes}
        norm_h = sum(v * v for v in new_hub.values()) ** 0.5 or 1.0
        for n in nodes:
            new_hub[n] /= norm_h
        # Check convergence
        diff = sum(abs(new_auth[n] - auth[n]) for n in nodes) + sum(abs(new_hub[n] - hub[n]) for n in nodes)
        auth, hub = new_auth, new_hub
        if diff < tol:
            break
    return auth, hub


def toy_graph():
    return {
        "A": {"B", "C"},
        "B": {"C"},
        "C": {"A"},
        "D": {"C"},
    }


def main():
    parser = argparse.ArgumentParser(description="Link analysis: PageRank and HITS")
    parser.add_argument("--toy", action="store_true", help="Run on a toy graph")
    args = parser.parse_args()

    if args.toy:
        graph = toy_graph()
    else:
        # Example stub: you could load a graph from a file here
        graph = toy_graph()

    pr = pagerank(graph)
    print("PageRank:")
    for n, v in sorted(pr.items(), key=lambda x: x[1], reverse=True):
        print(f"{n}: {v:.4f}")

    auth, hub = hits(graph)
    print("\nHITS (Authority, Hub):")
    for n in sorted(set(graph.keys()) | {v for vs in graph.values() for v in vs}):
        print(f"{n}: A={auth.get(n,0):.4f} H={hub.get(n,0):.4f}")


if __name__ == "__main__":
    main()


