from fastapi import FastAPI
from pydantic import BaseModel
from neo4j import GraphDatabase
import os

app = FastAPI(
    servers=[
        {
            "url": "https://neo4j-executor.onrender.com"
        }
    ]
)

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(
    URI,
    auth=(USER, PASSWORD)
)

class QueryInput(BaseModel):
    cypher_query: str

@app.post("/execute-cypher")
def execute(query: QueryInput):

    with driver.session() as session:
        session.run(query.cypher_query)

    return {
        "success": True,
        "message": "Cypher executed successfully"
    }
