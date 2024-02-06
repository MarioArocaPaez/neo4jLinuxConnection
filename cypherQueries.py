# See nodes with ids
'''
MATCH (n)
WHERE id(n) IN [
    4566, 2227, 2393, 2260, 2235, 2230, 2234, 1076, 2336, 2442, 9149, 6867, 2335, 8915, 8916, 
    4633, 265, 4629, 4630, 1541, 264, 9010, 263, 262, 261, 260, 259, 258, 257, 9467, 9458, 
    4710, 166, 154, 146, 144, 142, 8212, 2, 6466, 7811, 9608, 244, 243, 6454, 6860, 6858, 
    6859, 6861, 6855, 6856, 6857, 6853, 6854, 241, 233, 8555, 214, 229, 230, 231, 6719, 766
]
RETURN n
'''
# City names
'''
MATCH ()-[r:ROAD_SEGMENT]->()
RETURN DISTINCT r.name
'''
# See the whole graph:
'''
MATCH (n)
OPTIONAL MATCH (n)-[r]->(m)
RETURN n, r, m;
'''
# View all nodes with the Greeting lable:
'''
MATCH (n:Greeting) RETURN n;
'''
# Nodes have a message, view the messages by inspecting the properties:
'''
MATCH (n:Greeting) RETURN n.message;
'''
# Delete the Greeting nodes:
'''
MATCH (n:Greeting) DELETE n;
'''