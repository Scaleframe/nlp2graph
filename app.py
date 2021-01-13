import time
import subprocess
from flask import Flask, request, render_template
from ports.vendor.e2c.predict import translate
from ports.vendor.e2c.args import get_args
import argparse


subprocess.run("docker stop $(docker ps | awk '/neo4j/ {print $1}') >/dev/null 2>&1", shell=True)
subprocess.run('/home/ubuntu/code/nlp2graph/ports/vendors/db/start-neo4j-database.sh', shell=True)

num_of_tries = 0
max_num_of_tries = 120

while True:
    try:
        from ports.db import setup_db, run_query
    except Exception:
        num_of_tries += 1
        if num_of_tries >= max_num_of_tries:
            raise ValueError('The neo4j is not up yet')
        print('Not running')
        time.sleep(.5)
        continue
    break
from ports.vendor.db.execute import Neo4jSession, nuke, load_yaml, run_query as run_session


app = Flask(__name__)


def add_args(parser):
    parser.add_argument("--graph-path",   type=str, default="./data/gqa-single.yaml")
    parser.add_argument("--neo-url",      type=str, default="bolt://localhost:7687")
    parser.add_argument("--neo-user",     type=str, default="neo4j")
    parser.add_argument("--neo-password", type=str, default="clegr-secrets")

args = get_args(add_args)

CACHED_Q = {}
cached_questions = [
"Which stations does Pink Woog pass through?",
"Which lines is Flip Bridge on?",
"What music plays at Niwham?",
"How many stations with disabled access does Green Soosh pass through?",
]

for idx, question in enumerate(cached_questions):
    query_cypher = translate(args, question)

    CACHED_Q.setdefault(question, {}).update(query_cypher=query_cypher)

    args_query = {
        "neo_url": 'bolt://localhost:7687',
        'neo_user': 'neo4j',
        'neo_password': 'clegr-secrets'
    }

    with Neo4jSession(args_query) as session:        
        nuke(session)

        load_yaml(session, '/home/ubuntu/code/graphchat/data/gqa-single.yaml')
    
        cypher_answer = run_query(session, query_cypher)
        CACHED_Q.setdefault(question, {}).update(cypher_answer=cypher_answer)

    if idx == 0:
        CACHED_Q.setdefault(question, {}).update(sleep_for=10)
    else:
        CACHED_Q.setdefault(question, {}).update(sleep_for=3)


@app.route('/get-query', methods=['GET', 'POST'])
def get_query():
    args_query = {}
    if request.method == 'GET':
        return render_template('translate_graph.html')
    elif request.method == 'POST':
        form = request.form
        user_string = form.get('user_string', '')
        if not user_string:
            return render_template('translate_graph.html')
        
        try:
            cached_content = CACHED_Q[user_string]
        except KeyError:
            pass
        else:
            time.sleep(cached_content['sleep_for'])  # dummy sleep
            query_cypher = cached_content['query_cypher']
            cypher_answer = cached_content['cypher_answer']
            return render_template('translate_graph.html',  query=query_cypher, answer=cypher_answer)    


        query_cypher = translate(args, user_string)

        CACHED_Q.setdefault(user_string, {}).update(query_cypher=query_cypher)

        args_query = {
            "neo_url": 'bolt://localhost:7687',
            'neo_user': 'neo4j',
            'neo_password': 'clegr-secrets'
        }

        with Neo4jSession(args_query) as session:        
            nuke(session)

            load_yaml(session, '/home/ubuntu/code/graphchat/data/gqa-single.yaml')
        
            cypher_answer = run_query(session, query_cypher)
            CACHED_Q.setdefault(user_string, {}).update(cypher_answer=cypher_answer)
        CACHED_Q.setdefault(user_string, {}).update(sleep_for=3)
        return render_template('translate_graph.html',  query=query_cypher, answer=cypher_answer)


if __name__ == '__main__':
    pass





