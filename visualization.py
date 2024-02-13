from py2neo import Graph
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')

# Connect to Neo4j
graph = Graph("bolt://localhost:7687", auth=None)

# Fetch data from Neo4j using a Cypher query
cypher_query = """
MATCH (n)-[r]->(m)
RETURN n, r, m
"""
data = graph.run(cypher_query)

# Create a networkx graph
G = nx.MultiDiGraph()

# Add nodes and edges to the networkx graph
for record in data:
    # Use Neo4j's internal ID if 'name' is not available
    n_id = record['n']['name'] if 'name' in record['n'] else record['n'].identity
    m_id = record['m']['name'] if 'name' in record['m'] else record['m'].identity

    G.add_node(n_id, **dict(record['n']))
    G.add_node(m_id, **dict(record['m']))
    G.add_edge(n_id, m_id, **dict(record['r']))

# Draw the graph
pos = nx.spring_layout(G)  # Use spring layout for an attractive distribution
nx.draw(G, pos, with_labels=True, node_color='skyblue', edge_color='gray')

# Display the graph
plt.savefig('graph.png')  # Save the figure in a file named 'graph.png'



