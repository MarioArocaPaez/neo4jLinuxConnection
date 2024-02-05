from py2neo import Graph, NodeMatcher, RelationshipMatcher

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







