import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv() # This loads the info from your .env file

uri = os.getenv("COGNODB_URI")
user = os.getenv("COGNODB_USER")
password = os.getenv("COGNODB_PASSWORD")

def test_conn():
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            result = session.run("RETURN 'Connection Successful!' AS message")
            print(result.single()["message"])
        driver.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_conn()