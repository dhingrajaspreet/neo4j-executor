from fastapi import FastAPI
from pydantic import BaseModel
from neo4j import GraphDatabase
import os

app = FastAPI(
    servers=[
        {
            "url": "https://neo4j-executor-1.onrender.com"
        }
    ]
)

# Neo4j credentials from Render environment variables
URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(
    URI,
    auth=(USER, PASSWORD)
)


# ----------------------------
# Input model
# ----------------------------
class QueryInput(BaseModel):
    cypher_query: str


# ----------------------------
# Existing endpoint
# Writes graph into Neo4j
# ----------------------------
@app.post("/execute-cypher")
def execute(query: QueryInput):

    with driver.session() as session:
        session.run(query.cypher_query)

    return {
        "success": True,
        "message": "Cypher executed successfully"
    }


# ----------------------------
# New endpoint
# Reads graph from Neo4j
# ----------------------------
@app.get("/view-graph")
def view_graph():

    with driver.session() as session:

        result = session.run("""
            MATCH (n)
            OPTIONAL MATCH (n)-[r]->(m)
            RETURN n, r, m
        """)

        nodes = set()
        edges = []

        for record in result:

            n = record["n"]
            r = record["r"]
            m = record["m"]

            if n:
                nodes.add(list(n.labels)[0])

            if r and m:
                edges.append({
                    "source": list(n.labels)[0],
                    "target": list(m.labels)[0],
                    "label": r.type
                })

        return {
            "nodes": list(nodes),
            "edges": edges
        }


# ----------------------------
# Health check
# Optional but useful
# ----------------------------
@app.get("/")
def root():
    return {
        "status": "running"
    }
