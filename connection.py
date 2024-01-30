# Import the GraphDatabase class from the neo4j module
from neo4j import GraphDatabase

# Define a class called HelloWorldExample
class HelloWorldExample:

    # The constructor of the class. It's called when you create an instance of the class.
    def __init__(self, uri):
        # Initialize a connection to the Neo4j database. 
        # 'auth=None' indicates that no authentication is required.
        self.driver = GraphDatabase.driver(uri, auth=None)

    # A method to close the database connection
    def close(self):
        # Close the Neo4j driver/connection
        self.driver.close()

    # A method to print a greeting message
    def print_greeting(self, message):
        # Start a session with the database
        with self.driver.session() as session:
            # Execute a write transaction using the _create_and_return_greeting method
            greeting = session.execute_write(self._create_and_return_greeting, message)
            # Print the result of the transaction
            print(greeting)

    # A static method that defines a transaction function
    @staticmethod
    def _create_and_return_greeting(tx, message):
        # Run a Cypher query to create a node with the label 'Greeting', set its message,
        # and return the message along with the node's id.
        result = tx.run("CREATE (a:Greeting) "
                        "SET a.message = $message "
                        "RETURN a.message + ', from node ' + id(a)", message=message)
        # Return the first (and in this case, only) record of the result
        return result.single()[0]

# The entry point of the script
if __name__ == "__main__":
    # Create an instance of the HelloWorldExample class, connecting to the database at bolt://localhost:7687
    greeter = HelloWorldExample("bolt://localhost:7687")
    # Call the print_greeting method with the message "hello, world"
    greeter.print_greeting("hello, world")
    # Close the database connection
    greeter.close()