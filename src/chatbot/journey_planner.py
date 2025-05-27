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
    
    # Loop through grouped routes, find the group with underground routes
    for i in range(len(grouped_routes)):
        if any("Underground Route" in route for _, route in grouped_routes[i]):
            # Set the last station's route of the underground route group to the route after it
            if i + 1 >= len(grouped_routes):
                break
            # Get the last station from the current group
            last_station =  grouped_routes[i][-1]
            last_name, _ = last_station
            _, next_route = grouped_routes[i + 1][0]
            
            next_group = grouped_routes[i + 1]
            next_group.insert(0, (last_name, next_route))
            break
    
    return grouped_routes

def get_optimal_path(start_station, end_station):
    global routes, route_objects, graph, route_map
    paths = find_all_paths_with_routes(graph, route_map, start_station, end_station, max_depth=8)
    if not paths:
        return []
    
    cleaned_paths = [clean_route(path) for path in paths]
    optimal_path = min(cleaned_paths, key=len)
    
    return optimal_path

def format_route(optimal_path: list[tuple]) -> str:
    current_route = None
    output = []

    # Merge the list of tuples into a single list
    merged_path = []
    for sublist in optimal_path:
        merged_path.extend(sublist)
    optimal_path = merged_path

    for station, route in optimal_path:
        if current_route != route:
            output.append(f"\n--- Route {route} ---")
            current_route = route
        output.append(f"→ {station}")
    return "\n".join(output)

routes, route_objects = load_routes_from_csv(FILE_PATH)
graph, route_map = build_station_graph_with_routes(route_objects)

if __name__ == "__main__":
    # Example usage
    start_station = "MAIDSTONE EAST"
    end_station = "NORWICH"
    route = get_optimal_path(start_station, end_station)
    print(f"Route from {start_station} to {end_station}:")
    print(format_route(route))
