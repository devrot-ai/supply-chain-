from __future__ import annotations

import heapq
from collections import defaultdict

import pandas as pd



def best_route_by_distance(routes_df: pd.DataFrame) -> dict[str, str | float]:
    route = routes_df.sort_values("distance_km", ascending=True).iloc[0]
    return {
        "source": str(route["source"]),
        "destination": str(route["destination"]),
        "distance_km": float(route["distance_km"]),
        "avg_time_hr": float(route["avg_time_hr"]),
    }



def build_graph(routes_df: pd.DataFrame, weight_column: str = "avg_time_hr") -> dict[str, list[tuple[str, float]]]:
    graph: dict[str, list[tuple[str, float]]] = defaultdict(list)
    for _, row in routes_df.iterrows():
        graph[str(row["source"])].append((str(row["destination"]), float(row[weight_column])))
    return graph



def dijkstra(graph: dict[str, list[tuple[str, float]]], start: str) -> dict[str, float]:
    queue: list[tuple[float, str]] = [(0.0, start)]
    distances = {node: float("inf") for node in graph}
    distances[start] = 0.0

    while queue:
        dist, node = heapq.heappop(queue)
        if dist > distances.get(node, float("inf")):
            continue

        for neighbor, weight in graph.get(node, []):
            new_dist = dist + weight
            if new_dist < distances.get(neighbor, float("inf")):
                distances[neighbor] = new_dist
                heapq.heappush(queue, (new_dist, neighbor))

    return distances



def fastest_route_between(routes_df: pd.DataFrame, source: str, destination: str) -> dict[str, str | float | list[str]]:
    graph = build_graph(routes_df, weight_column="avg_time_hr")
    queue: list[tuple[float, str]] = [(0.0, source)]
    distances = {source: 0.0}
    previous: dict[str, str | None] = {source: None}

    while queue:
        current_dist, node = heapq.heappop(queue)
        if node == destination:
            break
        if current_dist > distances.get(node, float("inf")):
            continue

        for neighbor, weight in graph.get(node, []):
            next_dist = current_dist + weight
            if next_dist < distances.get(neighbor, float("inf")):
                distances[neighbor] = next_dist
                previous[neighbor] = node
                heapq.heappush(queue, (next_dist, neighbor))

    if destination not in distances:
        return {
            "path": [],
            "total_time_hr": float("inf"),
            "source": source,
            "destination": destination,
        }

    path = []
    cursor: str | None = destination
    while cursor is not None:
        path.append(cursor)
        cursor = previous.get(cursor)
    path.reverse()

    direct = routes_df[(routes_df["source"] == source) & (routes_df["destination"] == destination)]
    direct_time = float("inf")
    if not direct.empty:
        direct_time = float(direct["avg_time_hr"].min())

    return {
        "path": path,
        "total_time_hr": round(float(distances[destination]), 2),
        "direct_time_hr": round(direct_time, 2) if direct_time != float("inf") else float("inf"),
        "source": source,
        "destination": destination,
    }
