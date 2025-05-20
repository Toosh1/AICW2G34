import csv
from collections import defaultdict

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

FILE_PATH = 'src/data/csv/Complete_Train_Routes_and_Stations.csv'

def load_routes_from_csv(file_path) -> tuple:
    """
    Loads routes and stations from a CSV file into the routes structure.
    """
    # Convert to a list of route objects
    objs = []
    # Define the structure to hold routes
    routes_list = defaultdict(lambda: {"description": "", "stations": []})

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            route_num = row['Route Number']
            if not routes_list[route_num]["description"]:
                routes_list[route_num]["description"] = row['Route Description']
            routes_list[route_num]["stations"].append(row['Station'])
    
    for route_number, data in routes_list.items():
        objs.append({
            "route_number": route_number,
            "description": data["description"],
            "stations": data["stations"]
        })
    return routes_list, objs

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

def clean_route(route: list) -> list:
    cleaned_route = []
    
    # Clean the route to remove unnecessary details
    for station, route_info in route:
        route = route_info.split(" (")[0] 
        cleaned_route.append((station, route))
    
    # Set the first route to be the same as the second route
    if len(cleaned_route) > 1:
        _, second_route = cleaned_route[1]
        cleaned_route[0] = (cleaned_route[0][0], second_route)
    
    # Group the stations by route
    grouped_routes = []
    current_route = []
    
    for station, route in cleaned_route:
        if current_route and current_route[-1][1] != route:
            grouped_routes.append(current_route)
            current_route = []
        current_route.append((station, route))
    
    if current_route:
        grouped_routes.append(current_route)    
    
    return cleaned_route

def print_route(optimal_path: list[tuple]):
    current_route = None
    
    for station, route in optimal_path:
        if current_route != route:
            print(f"\n--- Route {route} ---")
            current_route = route
        print(f"→ {station}")

def main(start_station, end_station):
    global routes, route_objects, graph, route_map
    
    paths = find_all_paths_with_routes(graph, route_map, start_station, end_station, max_depth=8)

    if not paths:
        return []
    
    optimal_path = min(paths, key=count_route_changes)
    optimal_path = clean_route(optimal_path)
    change_count = count_route_changes(optimal_path)

    return optimal_path

routes, route_objects = load_routes_from_csv(FILE_PATH)
graph, route_map = build_station_graph_with_routes(route_objects)

if __name__ == "__main__":
    # Example usage
    start_station = "MAIDSTONE EAST"
    end_station = "NORWICH"
    route = main(start_station, end_station)
    print_route(route)