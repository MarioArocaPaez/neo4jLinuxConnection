from py2neo import Graph, RelationshipMatcher
import heapq
from math import radians, cos, sin, asin, sqrt

# Function to search for nodes connected to a specific street
def find_street_nodes(graph, street_name):
    # Create a RelationshipMatcher
    rel_matcher = RelationshipMatcher(graph)

    # Search for relationships connected to the specified street
    relationships = rel_matcher.match(r_type="ROAD_SEGMENT", name=street_name)

    # Set to store unique node identities
    unique_node_ids = set()

    # Process relationships and add unique nodes to the set
    for rel in relationships:
        unique_node_ids.add(rel.start_node.identity)

    # Return the details of unique nodes
    nodes_info = []
    for node_id in unique_node_ids:
        node = graph.nodes.get(node_id)
        nodes_info.append((node.identity, node.get('location', None)))
    
    return nodes_info

def dijkstra(graph, start_id, end_id):
    # Fetch all nodes and relationships at once to avoid repeated database calls
    nodes = list(graph.nodes.match("Intersection"))
    rels = list(graph.relationships.match(r_type="ROAD_SEGMENT"))
    
    # Create a mapping from node ID to the node object for quick lookup
    node_mapping = {node.identity: node for node in nodes}
    
    # Create adjacency list representation of the graph
    adjacency_list = {node.identity: [] for node in nodes}
    for rel in rels:
        adjacency_list[rel.start_node.identity].append((rel.end_node.identity, rel['length']))
    
    # Priority queue for the Dijkstra algorithm
    queue = [(0, start_id, ())]  # Cost, node, path
    visited = set()
    distances = {node_id: float('inf') for node_id in adjacency_list}
    distances[start_id] = 0
    
    while queue:
        (cost, node_id, path) = heapq.heappop(queue)
        if node_id in visited:
            continue
        visited.add(node_id)
        path += (node_id,)
        
        if node_id == end_id:
            return cost, path
        
        for neighbor_id, edge_cost in adjacency_list[node_id]:
            if neighbor_id not in visited:
                new_cost = cost + edge_cost
                if new_cost < distances[neighbor_id]:
                    distances[neighbor_id] = new_cost
                    heapq.heappush(queue, (new_cost, neighbor_id, path))
    
    return float('inf'), ()

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

# Main code
if __name__ == "__main__":
    # Connect to Neo4j
    graph = Graph("bolt://localhost:7687", auth=None)

    # Call the function with the name of the street
    street_name = "Avenida de la Reina Mercedes"
    street_nodes = find_street_nodes(graph, street_name)

    # Print the details of the nodes returned from the function
    print(f"Nodes connected to '{street_name}':")
    for node_id, location in street_nodes:
        print(node_id, location)
        
    # Call the function with the name of the street
    street_name = "Calle Torneo"
    street_nodes = find_street_nodes(graph, street_name)
    print("\n")

    # Print the details of the nodes returned from the function
    print(f"Nodes connected to '{street_name}':")
    for node_id, location in street_nodes:
        print(node_id, location)
    print("\n")
        
    # Calculate Dijkstra shortest path
    start_node_id = 4566  
    end_node_id = 766  
    cost, path = dijkstra(graph, start_node_id, end_node_id)
    
    print("Dijkstra shortest path from node", start_node_id, "to node", end_node_id, ":")
    print("Shortest path cost:", cost)
    print("Shortest path:", path)
    print("\n")
    
    # Calculate A* shortest path
    start_node_id = 4566  
    end_node_id = 766  
    cost, path = astar(graph, start_node_id, end_node_id)
    
    print("A* shortest path from node", start_node_id, "to node", end_node_id, ":")
    print("Shortest path cost:", cost)
    print("Shortest path:", path)
    print("\n")







