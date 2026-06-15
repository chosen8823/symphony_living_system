import heapq

from layers.kuramoto import KuramotoEngine


class CognitivePathfinder:
    """A* pathfinder over the cognitive state space.

    Nodes are (layer_name, depth, coherence_bucket) where
    coherence_bucket = int(coherence * 10).

    Heuristic = |target_coherence - current_coherence|
    Cost       = entropy delta between frames
    """

    def __init__(self, kuramoto: KuramotoEngine):
        self.kuramoto = kuramoto

    def find_path(
        self, current_state: dict, target_coherence: float = 0.8
    ) -> list[str]:
        """Returns ordered list of layer names to traverse to reach target coherence."""
        start_nodes = []
        for name, state in current_state.items():
            coherence = state.get("coherence", 0.5)
            entropy = state.get("entropy", 0.5)
            bucket = int(coherence * 10)
            start_nodes.append((name, state.get("depth", 1), bucket, coherence, entropy))

        if not start_nodes:
            return []

        # pick node with lowest coherence as start
        start_nodes.sort(key=lambda n: n[3])
        start = start_nodes[0]

        # A* search
        # state tuple: (layer_name, depth, coherence_bucket)
        open_set: list[tuple[float, int, tuple[str, int, int], list[str]]] = []
        start_key = (start[0], start[1], start[2])
        heapq.heappush(open_set, (0.0, 0, start_key, [start[0]]))
        visited: set[tuple[str, int, int]] = set()
        counter = 1

        target_bucket = int(target_coherence * 10)

        while open_set:
            cost, _, current, path = heapq.heappop(open_set)
            if current in visited:
                continue
            visited.add(current)

            cur_name, cur_depth, cur_bucket = current
            if cur_bucket >= target_bucket:
                return path

            # generate neighbors: other layers with incrementally higher coherence
            for name, state in current_state.items():
                coh = state.get("coherence", 0.5)
                ent = state.get("entropy", 0.5)
                nb = int(coh * 10)
                depth = state.get("depth", 1)
                neighbor = (name, depth, nb)
                if neighbor in visited:
                    continue

                edge_cost = abs(ent - current_state.get(cur_name, {}).get("entropy", 0.5))
                heuristic = abs(target_coherence - coh)
                f = cost + edge_cost + heuristic
                heapq.heappush(open_set, (f, counter, neighbor, path + [name]))
                counter += 1

            # also simulate a kuramoto step as a virtual neighbor
            r = self.kuramoto.order_parameter()
            virtual_bucket = min(int(r * 10) + 1, 10)
            virtual = (cur_name, cur_depth, virtual_bucket)
            if virtual not in visited:
                heuristic = abs(target_coherence - r)
                heapq.heappush(
                    open_set, (cost + 0.1 + heuristic, counter, virtual, path + [cur_name])
                )
                counter += 1

        # no path found -- return all layers sorted by coherence descending
        return [
            n[0]
            for n in sorted(start_nodes, key=lambda n: n[3], reverse=True)
        ]
