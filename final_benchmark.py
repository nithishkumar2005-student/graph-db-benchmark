import os
import time
import numpy as np
from neo4j import GraphDatabase
from arango import ArangoClient
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

def benchmark_cypher(uri, user, pwd, db_name):
    """Benchmark for Cypher-based DBs (CognoDB, Neo4j, Memgraph, PuppyGraph)"""
    if not uri or not pwd:
        print(f"Skipping {db_name}: Credentials missing in .env")
        return None

    print(f"\n--- Testing {db_name} ---")
    results = {}
    try:
        # Connect to the database
        driver = GraphDatabase.driver(uri, auth=(user, pwd))
        
        # Test IDs from the Amazon dataset
        test_ids = ["100", "500", "1000", "5000", "10000"]
        
        with driver.session() as session:
            # 1. Lookups (Point lookup)
            latencies = []
            for _ in range(50):
                start = time.perf_counter()
                session.run("MATCH (p:Product {id: '500'}) RETURN p")
                latencies.append((time.perf_counter() - start) * 1000)
            results['Point Lookup (p50)'] = f"{np.percentile(latencies, 50):.2f}ms"

            # 2. 1-Hop Traversal
            latencies = []
            for start_id in test_ids:
                for _ in range(20):
                    start = time.perf_counter()
                    session.run("MATCH (p:Product {id: $id})-[:CO_PURCHASED]->(m) RETURN count(m)", id=start_id)
                    latencies.append((time.perf_counter() - start) * 1000)
            results['1-Hop (p50)'] = f"{np.percentile(latencies, 50):.2f}ms"
            results['1-Hop (p95)'] = f"{np.percentile(latencies, 95):.2f}ms"

            # 3. 2-Hop Traversal
            latencies = []
            for start_id in test_ids:
                for _ in range(10):
                    start = time.perf_counter()
                    session.run("MATCH (p:Product {id: $id})-[:CO_PURCHASED*2]->(m) RETURN count(m)", id=start_id)
                    latencies.append((time.perf_counter() - start) * 1000)
            results['2-Hop (p50)'] = f"{np.percentile(latencies, 50):.2f}ms"

        driver.close()
        print(f"Successfully benchmarked {db_name}!")
        return results
    except Exception as e:
        print(f"Error during {db_name} benchmark: {e}")
        return {"Error": "Connection/Auth Failed"}

def benchmark_arango(url, user, pwd):
    """Benchmark for ArangoDB using AQL"""
    if not url or not pwd:
        print("Skipping ArangoDB: Credentials missing in .env")
        return None

    print("\n--- Testing ArangoDB ---")
    results = {}
    try:
        client = ArangoClient(hosts=url)
        db = client.db('_system', username=user, password=pwd)
        test_ids = ["100", "500", "1000", "5000", "10000"]

        # 1. Point Lookup
        latencies = []
        for _ in range(50):
            start = time.perf_counter()
            db.aql.execute("FOR p IN Products FILTER p.id == '500' RETURN p")
            latencies.append((time.perf_counter() - start) * 1000)
        results['Point Lookup (p50)'] = f"{np.percentile(latencies, 50):.2f}ms"

        # 2. 1-Hop
        latencies = []
        for start_id in test_ids:
            for _ in range(20):
                start = time.perf_counter()
                db.aql.execute("FOR v IN 1..1 OUTBOUND CONCAT('Products/', @id) co_purchased RETURN v", bind_vars={'id': start_id})
                latencies.append((time.perf_counter() - start) * 1000)
        results['1-Hop (p50)'] = f"{np.percentile(latencies, 50):.2f}ms"
        results['1-Hop (p95)'] = f"{np.percentile(latencies, 95):.2f}ms"

        # 3. 2-Hop
        latencies = []
        for start_id in test_ids:
            for _ in range(10):
                start = time.perf_counter()
                db.aql.execute("FOR v IN 2..2 OUTBOUND CONCAT('Products/', @id) co_purchased RETURN v", bind_vars={'id': start_id})
                latencies.append((time.perf_counter() - start) * 1000)
        results['2-Hop (p50)'] = f"{np.percentile(latencies, 50):.2f}ms"

        print("Successfully benchmarked ArangoDB!")
        return results
    except Exception as e:
        print(f"Error during ArangoDB benchmark: {e}")
        return {"Error": "Connection Failed"}

if __name__ == "__main__":
    final_output = {}

    # Target 1: CognoDB
    final_output['CognoDB'] = benchmark_cypher(os.getenv("COGNODB_URI"), os.getenv("COGNODB_USER"), os.getenv("COGNODB_PASSWORD"), "CognoDB")

    # Target 2: Neo4j Aura
    final_output['Neo4j Aura'] = benchmark_cypher(os.getenv("NEO4J_URI"), os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"), "Neo4j Aura")

    # Target 3: Memgraph Cloud
    final_output['Memgraph Cloud'] = benchmark_cypher(os.getenv("MEMGRAPH_URI"), os.getenv("MEMGRAPH_USER"), os.getenv("MEMGRAPH_PASSWORD"), "Memgraph Cloud")

    # Target 4: ArangoDB Oasis
    final_output['ArangoDB Oasis'] = benchmark_arango(os.getenv("ARANGO_URL"), os.getenv("ARANGO_USER"), os.getenv("ARANGO_PWD"))

    # Target 5: PuppyGraph (Optional 4th competitor)
    final_output['PuppyGraph'] = benchmark_cypher(os.getenv("PUPPY_URI"), os.getenv("PUPPY_USER"), os.getenv("PUPPY_PWD"), "PuppyGraph")

    print("\n" + "="*50)
    print("FINAL BENCHMARK RESULTS MATRIX")
    print("="*50)
    
    # Print a clean summary
    for db, metrics in final_output.items():
        print(f"\n[{db}]")
        if metrics:
            for k, v in metrics.items():
                print(f"  {k}: {v}")
        else:
            print("  Status: Not Configured/Skipped")