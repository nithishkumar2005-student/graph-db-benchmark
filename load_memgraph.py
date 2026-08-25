import os
import time
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("MEMGRAPH_URI")
USER = os.getenv("MEMGRAPH_USER")
PWD = os.getenv("MEMGRAPH_PASSWORD")

def load_data():
    # We add trust="TRUST_ALL_CERTIFICATES" to bypass the SSL error
    driver = GraphDatabase.driver(URI, auth=(USER, PWD))
    
    batch_size = 2000
    rows = []
    total_loaded = 0
    
    start_time = time.time()

    with driver.session() as session:
        print("Connecting to Memgraph...")
        
        # New Memgraph/Neo4j syntax for creating an index
        print("Creating indexes...")
        try:
            session.run("CREATE INDEX FOR (p:Product) ON (p.id)")
        except Exception as e:
            print(f"Note: Index might already exist or had a small error: {e}")

        print("Starting data load...")
        with open("amazon_relationships.csv", "r") as f:
            for line in f:
                if line.startswith("#"): continue
                parts = line.split()
                if len(parts) == 2:
                    rows.append({"source": parts[0], "target": parts[1]})
                
                if len(rows) >= batch_size:
                    session.run("""
                    UNWIND $batch AS row
                    MERGE (s:Product {id: row.source})
                    MERGE (t:Product {id: row.target})
                    CREATE (s)-[:CO_PURCHASED]->(t)
                    """, batch = rows)
                    
                    total_loaded += len(rows)
                    print(f"Loaded {total_loaded} relationships into Memgraph...")
                    rows = []
                    
                    if total_loaded >= 105000:
                        break

    end_time = time.time()
    duration = end_time - start_time
    
    print("\n--- MEMGRAPH LOAD COMPLETE ---")
    print(f"Total Relationships: {total_loaded}")
    print(f"Total Time: {duration:.2f} seconds")
    print(f"Throughput: {total_loaded / duration:.2f} rels/sec")

    driver.close()

if __name__ == "__main__":
    load_data()