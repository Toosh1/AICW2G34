import csv
from collections import defaultdict, deque

# Define the structure to hold routes
routes = defaultdict(lambda: {"description": "", "stations": []})

# London terminals treated as interchangeable with Underground connections
LONDON_TERMINALS = {
    "LONDON VICTORIA",
    "LONDON BRIDGE",
    "LONDON LIVERPOOL STREET",
    "LONDON EUSTON",
    "LONDON KINGS CROSS",
    "LONDON PADDINGTON",
    "LONDON WATERLOO",
    "LONDON CHARING CROSS",
    "LONDON ST PANCRAS INTL",
    "LONDON MARYLEBONE",
    "LONDON BLACKFRIARS",
    "LONDON FENCHURCH STREET",
    "LONDON CANNON STREET"
}

# Load the CSV file
with open('src/data/csv/Complete_Train_Routes_and_Stations.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        route_num = row['Route Number']
        if not routes[route_num]["description"]:
            routes[route_num]["description"] = row['Route Description']
        routes[route_num]["stations"].append(row['Station'])

# Convert to a list of route objects
route_objects = []
for route_number, data in routes.items():
    route_objects.append({
        "route_number": route_number,
        "description": data["description"],
        "stations": data["stations"]
    })

def build_station_graph_with_routes(route_objects):
    """
    Builds a graph with stations as nodes and edges for route connections.
    Adds connections between London terminals for Underground routing.
    """
    graph = defaultdict(set)
    route_map = defaultdict(list)

    for route in route_objects:
        stations = [s.strip().upper() for s in route["stations"]]
        route_num = route["route_number"]
        route_desc = route["description"]

        for i in range(len(stations) - 1):
            a, b = stations[i], stations[i + 1]
            graph[a].add(b)
            graph[b].add(a)
            route_info = f"{route_num} ({route_desc})"
            route_map[(a, b)].append(route_info)
            route_map[(b, a)].append(route_info)

    # Connect all London terminals with "Underground Route"
    london_list = list(LONDON_TERMINALS)
    for i in range(len(london_list)):
        for j in range(i + 1, len(london_list)):
            a = london_list[i]
            b = london_list[j]
            graph[a].add(b)
            graph[b].add(a)
            route_map[(a, b)].append("Underground Route")
            route_map[(b, a)].append("Underground Route")

    return graph, route_map

def find_all_paths_with_routes(graph, route_map, start, end, max_depth=10):
    """
    Uses DFS to find all paths between two stations, up to a depth.
    """
    start = start.strip().upper()
    end = end.strip().upper()
    all_paths = []

    def dfs(path, routes, visited):
        current = path[-1]
        if len(path) > max_depth:
            return
        if current == end:
            all_paths.append(list(zip(path, [""] + routes)))
            return
        for neighbor in graph[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                route_used = route_map[(current, neighbor)][0]
                dfs(path + [neighbor], routes + [route_used], visited)
                visited.remove(neighbor)

    dfs([start], [], set([start]))
    return all_paths

def count_route_changes(path_with_routes):
    """
    Counts how many times the route changes.
    """
    routes = [route for _, route in path_with_routes if route]
    if not routes:
        return 0
    changes = 0
    last = routes[0]
    for current in routes[1:]:
        if current != last:
            changes += 1
        last = current
    return changes

def main(start_station, end_station):
    graph, route_map = build_station_graph_with_routes(route_objects)
    paths = find_all_paths_with_routes(graph, route_map, start_station, end_station, max_depth=8)

    if paths:
        optimal_path = min(paths, key=count_route_changes)
        change_count = count_route_changes(optimal_path)

        print(f"Best path from {start_station} to {end_station} with {change_count} route change(s):\n")

        seen_routes = set()
        prev_station = None
        station_list = []

        for station, route in optimal_path:
            station_upper = station.upper()
            station_list.append(station)

            if route:
                # Print Underground Route cleanly
                if (prev_station and
                    prev_station.upper() in LONDON_TERMINALS and
                    station_upper in LONDON_TERMINALS and
                    prev_station.upper() != station_upper and
                    route == "Underground Route"):
                    print(f"→ {station} (Underground Route)")
                else:
                    if route not in seen_routes and route != "Underground Route":
                        try:
                            route_num, desc = route.split(" ", 1)
                        except ValueError:
                            route_num, desc = route, ""
                        print(f"\n--- Route {route_num}: {desc.strip('()')} ---")
                        seen_routes.add(route)
                    print(f"→ {station}")
            else:
                print(station)

            prev_station = station

        return " -> ".join(station_list)
    else:
        print(f"No path found from {start_station} to {end_station}.")
        return ""


