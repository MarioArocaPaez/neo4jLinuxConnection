from py2neo import Graph
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')

# Conectar a Neo4j
graph = Graph("bolt://localhost:7687", auth=None)

# Obtener datos de Neo4j utilizando una consulta Cypher
cypher_query = """
MATCH (n)-[r]->(m)
RETURN n, r, m
LIMIT 1000
"""
data = graph.run(cypher_query)

# Crear un grafo de networkx
G = nx.MultiDiGraph()

# Añadir nodos y aristas al grafo de networkx
for record in data:
    # Utiliza el ID interno de Neo4j si 'name' no está disponible
    n_id = record['n']['name'] if 'name' in record['n'] else record['n'].identity
    m_id = record['m']['name'] if 'name' in record['m'] else record['m'].identity

    G.add_node(n_id, **dict(record['n']))
    G.add_node(m_id, **dict(record['m']))
    G.add_edge(n_id, m_id, **dict(record['r']))

# Dibujar el grafo
pos = nx.spring_layout(G)  # Usar spring layout para una distribución atractiva
nx.draw(G, pos, with_labels=True, node_color='skyblue', edge_color='gray')

# Mostrar el grafo
plt.savefig('graph.png')  # Guarda la figura en un archivo llamado 'graph.png'


