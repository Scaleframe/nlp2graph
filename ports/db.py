from .vendor.db.execute import Neo4jSession, nuke, load_yaml, run_query as run_session
import neo4j
import traceback

def setup_db(graph_path):
    args = {
        "neo_url": 'bolt://localhost:7687',
        'neo_user': 'neo4j',
        'neo_password': 'clegr-secrets'
    }

    with Neo4jSession(args) as session:        
        nuke(session)

        load_yaml(session, graph_path)
        return session

session = setup_db('/home/ubuntu/code/graphchat/data/gqa.yaml')

def run_query(session, query_cypher):
    all_answers = []
    try:
        result = run_session(session, query_cypher)
    except Exception: 
        print("Drat, that translation failed to execute in Neo4j!")
        traceback.print_exc()
        return "Drat, that failed to execute in Neo4J!"
    else:
        for i in result:
            for j in i.values():
                all_answers.append(str(j))
    return all_answers
