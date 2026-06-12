from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from neo4j import GraphDatabase
from pyvis.network import Network
import networkx as nx
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


class QueryInput(BaseModel):
    cypher_query: str


@app.get("/")
def home():
    return {"status": "running"}


@app.post("/execute-cypher")
def execute(query: QueryInput):

    with driver.session() as session:
        session.run(query.cypher_query)

    return {
        "success": True,
        "message": "Cypher executed successfully",
        "graph_url": "https://neo4j-executor-1.onrender.com/graph"
    }


@app.get("/view-graph")
def view_graph():

    nodes = []
    edges = []

    with driver.session() as session:

        node_result = session.run("""
            MATCH (n)
            RETURN elementId(n) as id, labels(n)[0] as label
        """)

        for record in node_result:
            nodes.append({
                "id": record["id"],
                "label": record["label"]
            })

        edge_result = session.run("""
            MATCH (a)-[r]->(b)
            RETURN elementId(a) as source,
                   elementId(b) as target,
                   type(r) as label
        """)

        for record in edge_result:
            edges.append({
                "source": record["source"],
                "target": record["target"],
                "label": record["label"]
            })

    return {
        "nodes": nodes,
        "edges": edges
    }


@app.get("/graph", response_class=HTMLResponse)
def graph():

    G = nx.DiGraph()

    with driver.session() as session:

        node_result = session.run("""
            MATCH (n)
            RETURN elementId(n) as id, labels(n)[0] as label
        """)

        for record in node_result:
            G.add_node(
                record["id"],
                label=record["label"]
            )

        edge_result = session.run("""
            MATCH (a)-[r]->(b)
            RETURN elementId(a) as source,
                   elementId(b) as target,
                   type(r) as label
        """)

        for record in edge_result:
            G.add_edge(
                record["source"],
                record["target"],
                label=record["label"]
            )

    net = Network(
        height="800px",
        width="100%",
        directed=True
    )

    net.from_nx(G)
    net.save_graph("graph.html")

    with open("graph.html", "r", encoding="utf-8") as f:
        return f.read()
