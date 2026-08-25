import os
import time
from arango import ArangoClient
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("ARANGO_URL")
USER = os.getenv("ARANGO_USER")
PWD = os.getenv("ARANGO_PWD")

def load_data():
    # Initialize the client
    client = ArangoClient(hosts=URL)

    try:
        # Connect to the default '_system' database directly
        db = client.db('_system', username=USER, password=PWD)
        print("Successfully connected to ArangoDB!")

        # Create collections if they don't exist
        if not db.has_collection('Products'):
            db.create_collection('Products')
        
        # Create edge collection
        if not db.has_collection('co_purchased'):
            db.create_collection('co_purchased', edge=True)

        products = db.collection('Products')
        edges = db.collection('co_purchased')

        # Ensure index for speed
        products.add_persistent_index(fields=['id'], unique=True)
        batch_size = 2000
        product_batch = []
        edge_batch = []
        total_loaded = 0
        seen_ids = set()

        start_time = time.time()
        print("Starting data load into ArangoDB...")

        with open("amazon_relationships.csv", "r") as f:
            for line in f:
                if line.startswith("#"): continue
                parts = line.split()
                if len(parts) == 2:
                    src, tgt = parts[0], parts[1]
                    
                    for node_id in [src, tgt]:
                        if node_id not in seen_ids:
                            product_batch.append({'_key': node_id, 'id': node_id})
                            seen_ids.add(node_id)
                    
                    edge_batch.append({
                        '_from': f'Products/{src}',
                        '_to': f'Products/{tgt}'
                    })
                
                if len(edge_batch) >= batch_size:
                    if product_batch:
                        products.import_bulk(product_batch)
                        product_batch = []
                    
                    edges.import_bulk(edge_batch)
                    total_loaded += len(edge_batch)
                    print(f"Loaded {total_loaded} relationships...")
                    edge_batch = []
                    
                    if total_loaded >= 105000:
                        break

        end_time = time.time()
        duration = end_time - start_time
        
        print("\n--- ARANGODB LOAD COMPLETE ---")
        print(f"Total Relationships: {total_loaded}")
        print(f"Total Time: {duration:.2f} seconds")
        print(f"Throughput: {total_loaded / duration:.2f} rels/sec")

    except Exception as e:
        print(f"Connection Error: {e}")
        print("Check if your password in .env matches the one in the Arango console exactly.")

if __name__ == "__main__":
    load_data()