import os
import time
import csv
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PWD = os.getenv("NEO4J_PASSWORD")

def load_data():
    driver = GraphDatabase.driver(URI, auth=(USER, PWD))
    
    # We use a batch size of 2000 for efficiency
    batch_size = 2000
    rows = []
    total_loaded = 0
    
    start_time = time.time()

    with driver.session() as session:
        print("Creating indexes...")
        session.run("CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:Product) REQUIRE p.id IS UNIQUE")

        print("Starting data load...")
        with open("amazon_relationships.csv", "r") as f:
            # Skip the header lines of the SNAP file
            for line in f:
                if line.startswith("#"): continue
                
                parts = line.split()
                if len(parts) == 2:
                    rows.append({"source": parts[0], "target": parts[1]})
                
                if len(rows) >= batch_size:
                    # This is a Cypher query to batch upload
                    session.run("""
                    UNWIND $batch AS row
                    MERGE (s:Product {id: row.source})
                    MERGE (t:Product {id: row.target})
                    CREATE (s)-[:CO_PURCHASED]->(t)
                    """, batch = rows)
                    
                    total_loaded += len(rows)
                    print(f"Loaded {total_loaded} relationships...")
                    rows = []
                    
                    # For this assignment, let's stop at 105,000 to keep it fast
                    if total_loaded >= 105000:
                        break

    end_time = time.time()
    duration = end_time - start_time
    
    print("--- LOAD COMPLETE ---")
    print(f"Total Relationships: {total_loaded}")
    print(f"Total Time: {duration:.2f} seconds")
    print(f"Throughput: {total_loaded / duration:.2f} rels/sec")

    driver.close()

if __name__ == "__main__":
    load_data()