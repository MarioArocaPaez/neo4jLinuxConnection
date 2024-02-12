import neo4j
import osmnx as ox

# Configuración para una conexión local de Neo4j sin autenticación
NEO4J_URI = "bolt://localhost:7687"

# Neo4j driver with no auth
driver = neo4j.GraphDatabase.driver(NEO4J_URI, auth=None)

# Cypher queries to delete all nodes and relationships
delete_all_nodes_query = "MATCH (n) DETACH DELETE n"
delete_all_rels_query = "MATCH ()-[r]-() DELETE r"

# Execute queries to delete all nodes and relationships
with driver.session() as session:
    session.run(delete_all_rels_query)
    session.run(delete_all_nodes_query)

# Search OpenStreetMap and create an OSMNx graph
G = ox.graph_from_place("Sevilla, Andalucía, España", network_type="drive")

gdf_nodes, gdf_relationships = ox.graph_to_gdfs(G)
gdf_nodes.reset_index(inplace=True)
gdf_relationships.reset_index(inplace=True)

# Define Cypher queries to create constraints and indexes
constraint_query = "CREATE CONSTRAINT IF NOT EXISTS FOR (i:Intersection) REQUIRE i.osmid IS UNIQUE"
rel_index_query = "CREATE INDEX IF NOT EXISTS FOR ()-[r:ROAD_SEGMENT]-() ON r.osmids"
point_index_query = "CREATE POINT INDEX IF NOT EXISTS FOR (i:Intersection) ON i.location"

# Cypher query to import road network nodes GeoDataFrame
# UNWIND -> iterate over rows
# MERGE -> create or update nodes and relationships
node_query = '''
    UNWIND $rows AS row
    WITH row WHERE row.osmid IS NOT NULL
    MERGE (i:Intersection {osmid: row.osmid})
        ON CREATE SET i.location = point({latitude: row.y, longitude: row.x }),
            i.ref = row.ref,
            i.highway = row.highway,
            i.street_count = toInteger(row.street_count)
    RETURN COUNT(*) as total
'''

# Cypher query to import road network relationships GeoDataFrame
rels_query = '''
    UNWIND $rows AS road
    MATCH (u:Intersection {osmid: road.u})
    MATCH (v:Intersection {osmid: road.v})
    MERGE (u)-[r:ROAD_SEGMENT {osmid: road.osmid}]->(v)
        SET r.oneway = road.oneway,
            r.lanes = road.lanes,
            r.ref = road.ref,
            r.name = road.name,
            r.highway = road.highway,
            r.max_speed = road.maxspeed,
            r.length = toFloat(road.length)
    RETURN COUNT(*) AS total
'''

# Function to execute constraint / index queries
def create_constraints(tx):
    tx.run(constraint_query)
    tx.run(rel_index_query)
    tx.run(point_index_query)

# Function to batch GeoDataFrames
def insert_data(tx, query, rows, batch_size=10000):
    total = 0
    batch = 0
    
    while batch * batch_size < len(rows):
        results = tx.run(query, parameters={'rows': rows[batch*batch_size:(batch+1)*batch_size].to_dict('records')}).data()
        print(results)
        total += results[0]['total']
        batch += 1

# Run our constraints queries and nodes GeoDataFrame import
with driver.session() as session:
    session.execute_write(create_constraints)
    session.execute_write(insert_data, node_query, gdf_nodes.drop(columns=['geometry'])) 

# Run our relationships GeoDataFrame import
with driver.session() as session:
    session.execute_write(insert_data, rels_query, gdf_relationships.drop(columns=['geometry'])) 

driver.close()
