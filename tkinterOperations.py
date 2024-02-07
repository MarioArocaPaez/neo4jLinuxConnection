import tkinter as tk
from tkinter import Spinbox, ttk
import heapq
from py2neo import Graph, NodeMatcher, RelationshipMatcher
from math import radians, cos, sin, asin, sqrt
import matplotlib.pyplot as plt

# Function to search for nodes connected to a specific street
def find_street_nodes(graph, street_name):
    rel_matcher = RelationshipMatcher(graph)
    relationships = rel_matcher.match(r_type="ROAD_SEGMENT", name=street_name)

    # Initialize a set for unique node identities and a list for nodes information
    unique_node_ids = set()
    nodes_info = []

    node_cache = {}

    for rel in relationships:
        # Check if start_node is already processed
        if rel.start_node.identity not in node_cache:
            # If not in cache, fetch and store it
            start_node_info = (rel.start_node.identity, rel.start_node.get('location', None))
            node_cache[rel.start_node.identity] = start_node_info
            nodes_info.append(start_node_info)
        else:
            # If in cache, directly append from cache
            nodes_info.append(node_cache[rel.start_node.identity])
            
    return nodes_info

def dijkstra(graph, start_id, end_id):
    # Fetch all nodes and relationships to build the graph structure
    nodes = list(graph.nodes.match("Intersection"))
    rels = list(graph.relationships.match(r_type="ROAD_SEGMENT"))
    
    # Create adjacency list representation of the graph
    adjacency_list = {node.identity: [] for node in nodes}
    for rel in rels:
        adjacency_list[rel.start_node.identity].append((rel.end_node.identity, rel['length']))
    
    # Initialize data structures for Dijkstra's algorithm
    queue = [(0, start_id)]  # Priority queue: (distance, node_id)
    distances = {node_id: float('inf') for node_id in adjacency_list}
    distances[start_id] = 0
    predecessors = {node_id: None for node_id in adjacency_list}
    
    while queue:
        current_distance, current_node = heapq.heappop(queue)
        
        if current_node == end_id:
            break  # Stop if the target node has been reached
        
        for neighbor, weight in adjacency_list[current_node]:
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                predecessors[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor))
                
    # Reconstruct the shortest path from end_id to start_id
    path = []
    current_node = end_id
    while current_node is not None:
        path.insert(0, current_node)
        current_node = predecessors[current_node]
        
    if path[0] == start_id:  # Ensure the path is valid
        return distances[end_id], path
    else:
        return float('inf'), []

# Haversine formula to calculate the distance between two points on the Earth's surface
def haversine(lat1, lon1, lat2, lon2):
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of Earth in kilometers. Use 3956 for miles
    return c * r

# A* algorithm implementation
def astar(graph, start_id, end_id):
    start_node = graph.nodes.get(start_id)
    end_node = graph.nodes.get(end_id)
    
    # Extract latitude and longitude from the start and end nodes
    start_lat, start_lon = start_node['location'].latitude, start_node['location'].longitude
    end_lat, end_lon = end_node['location'].latitude, end_node['location'].longitude

    # Priority queue for A* algorithm
    open_set = [(0 + haversine(start_lat, start_lon, end_lat, end_lon), 0, start_id, [])]  # (f_score, g_score, node_id, path)
    
    # Visited and cost dictionaries
    visited = set()
    g_score = {start_id: 0}

    while open_set:
        _, current_g, current, path = heapq.heappop(open_set)
        
        if current in visited:
            continue

        visited.add(current)
        path = path + [current]

        if current == end_id:
            return current_g, path

        neighbors = graph.relationships.match(nodes=[graph.nodes.get(current)], r_type="ROAD_SEGMENT")
        for rel in neighbors:
            neighbor = rel.end_node
            temp_g_score = current_g + rel['length']
            
            if neighbor.identity in visited and temp_g_score >= g_score.get(neighbor.identity, float('inf')):
                continue

            if temp_g_score < g_score.get(neighbor.identity, float('inf')):
                g_score[neighbor.identity] = temp_g_score
                f_score = temp_g_score + haversine(neighbor['location'].latitude, neighbor['location'].longitude, end_lat, end_lon)
                heapq.heappush(open_set, (f_score, temp_g_score, neighbor.identity, path))

    return float('inf'), []

def get_street_suggestions(graph, partial_street_name):
    rel_matcher = RelationshipMatcher(graph)
    # Search for relationships with a name that begins with the partial text
    relationships = rel_matcher.match(r_type="ROAD_SEGMENT")
    streets = set()
    for rel in relationships:
        name = rel.get('name', '')
        # Check if name is a list and take the first element, or ignore if it's NaN or an empty list
        if isinstance(name, list):
            name = name[0] if name else ''
        if isinstance(name, str) and name and name.lower().startswith(partial_street_name.lower()):
            streets.add(name)
    return list(streets)

def execute_find_street_nodes():
    street_name = street_name_var.get()
    nodes = find_street_nodes(graph, street_name)
    result_text.delete('1.0', tk.END)
    result_text.insert(tk.END, f"Nodes connected to '{street_name}':\n")
    for node_id, location in nodes:
        result_text.insert(tk.END, f"{node_id}: {location}\n")

def execute_dijkstra():
    start_node_id = int(start_node_var.get())
    end_node_id = int(end_node_var.get())
    cost, path = dijkstra(graph, start_node_id, end_node_id)
    result_text.delete('1.0', tk.END)
    result_text.insert(tk.END, f"Dijkstra shortest path from node {start_node_id} to node {end_node_id}:\n")
    result_text.insert(tk.END, f"Shortest path cost: {cost} meters\n")
    result_text.insert(tk.END, f"Shortest path: {path}\n")
    plot_route(graph, path, 'red', 'Dijkstra Path')
    plt.xlabel('Longitude', fontsize='x-large')
    plt.ylabel('Latitude', fontsize='x-large')
    plt.legend()
    plt.title('Dijkstra Shortest Path', fontsize='xx-large')
    plt.show()

def execute_astar():
    start_node_id = int(start_node_var.get())
    end_node_id = int(end_node_var.get())
    cost, path = astar(graph, start_node_id, end_node_id)
    result_text.delete('1.0', tk.END)
    result_text.insert(tk.END, f"A* shortest path from node {start_node_id} to node {end_node_id}:\n")
    result_text.insert(tk.END, f"Shortest path cost: {cost} meters\n")
    result_text.insert(tk.END, f"Shortest path: {path}\n")
    plot_route(graph, path, 'blue', 'A*')
    plt.xlabel('Longitude', fontsize='x-large')
    plt.ylabel('Latitude', fontsize='x-large')
    plt.legend()
    plt.title('A* Shortest Path', fontsize='xx-large')
    plt.show()
    
def plot_route(graph, path, color, label):
    x_coords = []
    y_coords = []
    total_distance = 0  # Initialize total distance to 0
    
    # Fetch nodes
    for node_id in path:
        node = graph.nodes.get(node_id)
        x_coords.append(node['location'].longitude)
        y_coords.append(node['location'].latitude)

    # Plot the route
    plt.plot(x_coords, y_coords, color=color, label=label, linewidth=2)
    # Starting point
    plt.scatter(x_coords[0], y_coords[0], c='yellow', edgecolor='yellow', label='Start', zorder=5)
    # Finishing point
    plt.scatter(x_coords[-1], y_coords[-1], c='lime', edgecolor='lime', label='End', zorder=5)
    # Rest of the route
    plt.scatter(x_coords[1:-1], y_coords[1:-1], c=color)

    # Fetch relationships and annotate the distance
    for i in range(1, len(path)):
        start_node = graph.nodes.get(path[i-1])
        end_node = graph.nodes.get(path[i])
        rel = graph.relationships.match((start_node, end_node), r_type="ROAD_SEGMENT").first()
        if rel:
            distance = rel['length']
            street_name = rel['name'] if 'name' in rel else ''
            total_distance += distance
            # Get the midpoint for the label
            mid_x = (x_coords[i-1] + x_coords[i]) / 2
            mid_y = (y_coords[i-1] + y_coords[i]) / 2
            # Annotate the segment with the distance
            plt.annotate(f"{street_name}\n{distance:.2f} m", (mid_x, mid_y), textcoords="offset points", xytext=(0,5), ha='center')

    # Annotate the total distance
    plt.annotate(f"Total distance: {total_distance:.2f} m", (x_coords[-1], y_coords[-1]), textcoords="offset points", xytext=(0,-15), ha='center', fontsize=9, bbox=dict(boxstyle="round,pad=0.3", edgecolor=color, facecolor='white'))


# Connection to Neo4j
graph = Graph("bolt://localhost:7687", auth=None)

# Get all the streets for the Spinbox
all_streets = get_street_suggestions(graph, '')

# Create the main window
root = tk.Tk()
root.title("Graph Operations GUI")

# Spinbox to select or enter the street name
street_name_var = tk.StringVar()
street_name_spinbox = Spinbox(root, values=all_streets, textvariable=street_name_var, wrap=True)
street_name_spinbox.pack()

# Button to search for nodes
search_button = ttk.Button(root, text="Search Node", command=execute_find_street_nodes)
search_button.pack()

# Input fields for Dijkstra and A*
start_node_var = tk.StringVar()
end_node_var = tk.StringVar()
start_node_entry = ttk.Entry(root, textvariable=start_node_var)
end_node_entry = ttk.Entry(root, textvariable=end_node_var)
start_node_entry.pack()
end_node_entry.pack()
dijkstra_button = ttk.Button(root, text="Calculate Dijkstra", command=execute_dijkstra)
dijkstra_button.pack()
astar_button = ttk.Button(root, text="Calculate A*", command=execute_astar)
astar_button.pack()

# Text area for results
result_text = tk.Text(root, height=10, width=50)
result_text.pack()

# Run the application
root.mainloop()