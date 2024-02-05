from py2neo import Graph, RelationshipMatcher
import heapq

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
    # Create a priority queue and hash map to store the cost of the shortest paths found
    queue = [(0, start_id, ())]  # Cost, node, path
    visited = set()
    
    while queue:
        (cost, node_id, path) = heapq.heappop(queue)
        # Avoid processing the same node twice
        if node_id in visited:
            continue

        visited.add(node_id)
        
        # Return the path if the end node is reached
        if node_id == end_id:
            return (cost, path + (node_id,))
        
        # Search for all neighbors of the current node
        node = graph.nodes.get(node_id)
        for rel in graph.match((node,), r_type="ROAD_SEGMENT"):
            if rel.end_node.identity not in visited:
                # Total cost is the sum of the current cost and the weight of the edge
                total_cost = cost + rel["length"]
                heapq.heappush(queue, (total_cost, rel.end_node.identity, path + (node_id,)))
    
    return (float('inf'), ())

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







