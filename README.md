# Pokemon LLM RDF

**Overview**  
- Builds an RDF dataset for Pokémon (names, numbers, types, evolution) using **rdflib**.  
- Uses **LangChain** + OpenAI to auto-generate SPARQL queries for Q&A.  

**Requirements**  
- Python 3.10 
- `rdflib`, `langchain`, `langchain_community`, `langchain_openai`  

**Installation**  
```bash
pip install -r requirements.txt
```
**Usage**
Set OPENAI_API_KEY (e.g., export OPENAI_API_KEY="your_key").
Run the main script:
```bash
python pokemon_llm_rdf.py
```
It will create pokemo.rdf (N3 format), load it, build a GraphSparqlQAChain, and print the LLM-generated answer.
Editing

Add/change Pokémon data in create_pokemon_graph().
Adjust query in main() for different questions.

**Notes**

- If you see deprecation warnings for chain.run(), switch to chain.invoke().
- Ensure prompts avoid extra Markdown in SPARQL output.
- Use carefully if allow_dangerous_requests=True.

**Demo**
![image]("demo/demo001.png")
![image]("demo/demo002.png")
![image]("demo/demo003.png")
![image]("demo/demo004.png")
![image]("demo/demo005.png")