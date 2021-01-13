### nlp2graph 

Welcome! This is a project I worked on last year for Insight Data Science that uses nlp to translate english text to a graph database query languages. 

This repo does a few things;

#### 1: Application component: 
Our app will use Flask to take English text from user input and use an NLP model to translate that to CYPHER, a graph database query language. The app uses hexagonal architecture to decouple business logic from vendor specific components. This makes life easier for upgrades and changes, as we will see as the project progresses.  


#### 2: NLP component: 
We will translate the user input to cypher using an RNN based seq2seq model and a older tensorflow data pipeline. We will then upgrade the pipeline and model with more modern approaches. 


#### 3: Graph database componenet: 
Sets up a working graph database instance, then passes the output of the NLP model to the database and returns an answer. 



Special thanks to Octavian Ai for their work on the CLEVR Graph and the english 2 cypher dataset. 

