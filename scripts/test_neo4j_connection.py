import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

driver = GraphDatabase.driver(
    os.environ["NEO4J_URI"],
    auth=(
        os.environ["NEO4J_USER"],
        os.environ["NEO4J_PASSWORD"],
    ),
)

with driver.session(database=os.getenv("NEO4J_DATABASE", "neo4j")) as session:
    result = session.run("RETURN 1 AS connected")
    print(result.single()["connected"])

driver.close()