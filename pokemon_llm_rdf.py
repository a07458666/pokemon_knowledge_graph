from rdflib import Graph, Namespace, RDF, Literal, URIRef, XSD

from langchain.chains import GraphSparqlQAChain
from langchain_community.graphs import RdfGraph
from langchain_openai import ChatOpenAI

from langchain import PromptTemplate

def add_pokemon_data(graph,
    name: str,
    number: str,
    type: str,
    evolve_from: str = "",
    evolve_to: str = ""):
    POKEMON = Namespace("http://example.org/pokemon")
    subject = URIRef(f"http://example.org/pokemon_{number}")
    graph.add((subject, RDF.type, POKEMON.Pokemon))
    graph.add((subject, POKEMON.name, Literal(name)))
    graph.add((subject, POKEMON.number, Literal(number, datatype=XSD.string)))
    graph.add((subject, POKEMON.type, Literal(type)))
    if evolve_from != "":
        graph.add((subject, POKEMON.evolve_from, Literal(evolve_from)))
    if evolve_to != "":
        graph.add((subject, POKEMON.evolve_to, Literal(evolve_to)))
          
def create_pokemon_graph():
    pokemon_graph = Graph()
    add_pokemon_data(pokemon_graph, "皮卡丘", "001", "雷系", "", "雷丘")
    add_pokemon_data(pokemon_graph, "妙蛙草", "002", "草系", "", "妙蛙花")
    add_pokemon_data(pokemon_graph, "小火龍", "003", "火系", "", "火恐龍")
    add_pokemon_data(pokemon_graph, "傑尼龜", "004", "水系", "", "卡咪龜")
    add_pokemon_data(pokemon_graph, "綠毛蟲", "005", "蟲系", "", "鐵甲蛹")
    add_pokemon_data(pokemon_graph, "雷丘", "006", "雷系", "皮卡丘")
    add_pokemon_data(pokemon_graph, "火恐龍", "007", "火系", "小火龍")
    add_pokemon_data(pokemon_graph, "卡咪龜", "008", "水系", "傑尼龜")
    add_pokemon_data(pokemon_graph, "鐵甲蛹", "009", "蟲系", "綠毛蟲")
    add_pokemon_data(pokemon_graph, "妙蛙花", "010", "草系", "妙蛙草")
    add_pokemon_data(pokemon_graph, "超夢", "011", "超能力系")
    return pokemon_graph
    
def load_rdf_graph(path):
    return RdfGraph(source_file=path, standard="rdf")
    
def create_qa_chain(graph):
    return GraphSparqlQAChain.from_llm(
        llm=ChatOpenAI(temperature=0),
        graph=graph,
        verbose=True,
        allow_dangerous_requests=True,
        return_sparql_query=True,
        return_intermediate_steps=True,
        return_direct=True,
    )
def main():
    pokemon_graph = create_pokemon_graph()
    pokemon_graph.serialize("pokemo.rdf", format="n3")
    # print("已產生 pokemo.rdf")
    
    pokemon_rdf_graph = load_rdf_graph("pokemo.rdf")
    pokemon_rdf_graph.load_schema()
    # print(pokemon_rdf_graph.schema)
    
    chain = create_qa_chain(pokemon_rdf_graph)
    instruction = """
    ADDITIONAL INSTRUCTION: When you make the final query, remove these ``` quotes and only have the query.
    Ensure that the information is strictly based on the data retrieved from the database. Do not mention any information that does not exist in the database.
    """
    query = "QUERY: 妙蛙草的number是多少？"
    # query = "QUERY: 皮卡丘的type是什麼？"
    # query = "QUERY: 妙蛙草的type是什麼？"
    # query = "QUERY: 資料庫中有多少種寶可夢？"
    # query = "QUERY: 有多少種名字是三個字的寶可夢？"
    # query = "QUERY: 有什麼寶可夢不能進化？"
    # query = "QUERY: 有哪幾種寶可夢能進化？"
    prompt = instruction + query
    print(prompt)
    response = chain.invoke(prompt)
    print(response["result"])
    
    
if __name__ == "__main__":
    main()
