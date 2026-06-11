from fastapi import FastAPI
from pydantic import BaseModel
from neo4j import GraphDatabase

app = FastAPI()

URI = "neo4j+s://515d24ed.databases.neo4j.io"
USER = "neo4j"
PASSWORD = "JGBnjaV31qOamltdNCsEszJlEni-oF7TmlrTW2R2FhY"

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
