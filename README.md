# graph-db-benchmark
# Graph Database Cloud Benchmarking Suite

## 1. Objective
This project benchmarks **CognoDB Cloud** against three major managed graph database platforms: **Neo4j Aura**, **Memgraph Cloud**, and **ArangoDB Oasis**. The goal is to provide a reproducible, honest comparison of data ingestion speeds and traversal latencies.

## 2. Methodology & Fairness
To ensure a "same resources" comparison as required by the assignment:
- **Hardware:** All databases were deployed on their respective **Free Tiers** (approx. 0.5 vCPU / 256MB - 512MB RAM).
- **Dataset:** Amazon Product Co-purchasing network (SNAP) consisting of **106,000 relationships**.
- **Location:** All cloud instances were provisioned in the same geographic region where possible to minimize network variance.
- **Warm-up:** Each query was executed 10 times to warm the cache before recording the next 100 iterations for stable results.

## 3. Results Matrix

| Category | Metric | CognoDB | Memgraph | Neo4j Aura | ArangoDB |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Data Loading** | Total Load Time (s) | 26.10s | 28.45s | **12.41s** | 35.12s |
| **Data Loading** | Throughput (rel/s) | 4,060 | 3,725 | **8,543** | 3,018 |
| **Traversals** | 1-Hop (p50) | 254.35ms | **161.91ms** | N/A* | N/A* |
| **Traversals** | 2-Hop (p50) | 253.12ms | **156.61ms** | N/A* | N/A* |
| **Lookups** | Point Lookup (p50) | 252.79ms | **156.73ms** | N/A* | N/A* |

*\*Note: Connectivity/Auth timeouts were encountered during high-concurrency read tests on Neo4j and ArangoDB.*

## 4. Engineering Analysis
- **In-Memory Performance:** **Memgraph Cloud** delivered the lowest read latencies (~160ms). As an in-memory database, this confirms its efficiency for traversal-heavy workloads but notes a higher dependency on RAM limits.
- **Consistency:** **CognoDB** showed remarkable consistency between 1-hop and 2-hop traversals, maintaining a stable ~250ms latency. This suggests an optimized neighbor-loading architecture.
- **Ingestion Speed:** **Neo4j Aura** was the leader in bulk ingestion speed, loading the dataset nearly 2x faster than other platforms.
- **Honest Caveats:** During the automated benchmarking phase, Neo4j Aura and ArangoDB Oasis encountered SSL/Handshake timeouts. While data was successfully loaded, the automated read-benchmarks failed to connect during the final run. This highlights the sensitivity of managed cloud drivers to specific environment configurations.

## 5. How to Reproduce
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Configure your `.env` file with your cloud credentials (URI, User, Password).
4. Run the master script: `python final_benchmark.py`

## 6. Repository Structure
- `load_[db].py`: Scripts for data ingestion and index creation.
- `final_benchmark.py`: The master harness for measuring latencies.
- `amazon_relationships.csv`: The source dataset.
