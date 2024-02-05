from py2neo import Graph, NodeMatcher, RelationshipMatcher

# Connect to Neo4j
graph = Graph("bolt://localhost:7687", auth=None)

# Create a NodeMatcher and RelationshipMatcher
node_matcher = NodeMatcher(graph)
rel_matcher = RelationshipMatcher(graph)

# Search for relationships connected to a specific street
relationships = rel_matcher.match(r_type="ROAD_SEGMENT", name="Avenida de la Reina Mercedes")
for rel in relationships:
    start_node = rel.start_node
    end_node = rel.end_node
    # Print the internal Neo4j ID and the location property of the node
    print(start_node.identity, start_node.get('location', None))
    print(end_node.identity, end_node.get('location', None))

# Get specific nodes by their OSM ID
start_node = graph.nodes.get(1716)  # Ensure the ID corresponds to an existing node
end_node = graph.nodes.get(5260)  # Ensure the ID corresponds to an existing node

# Print ID and location
if start_node and end_node:
    print(start_node.identity, start_node.get('location', None))
    print(end_node.identity, end_node.get('location', None))
else:
    print("One of the nodes does not exist in the database.")






