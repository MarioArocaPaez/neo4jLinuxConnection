# See the whole graph:
'''
MATCH (n)
OPTIONAL MATCH (n)-[r]->(m)
RETURN n, r, m
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