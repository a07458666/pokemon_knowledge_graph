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
    POKEMON_INFO = Namespace("http://pokemon.org/pokemon_info#")
    subject = URIRef(f"http://pokemon.org/pokemon_info#{name}")
    graph.add((subject, RDF.type, POKEMON_INFO.Pokemon))
    graph.add((subject, POKEMON_INFO.name, Literal(name)))
    graph.add((subject, POKEMON_INFO.number, Literal(number, datatype=XSD.string)))
    graph.add((subject, POKEMON_INFO.type, Literal(type)))
    if evolve_from != "":
        graph.add((subject, POKEMON_INFO.evolve_from, Literal(evolve_from)))
    if evolve_to != "":
        graph.add((subject, POKEMON_INFO.evolve_to, Literal(evolve_to)))
        
# 新增異常狀態 ex: 睡眠、中毒
def add_pokemon_status(graph,
    name: str,
    category: str,
    recommendedSolution: str,
    description: str):
    POKEMON_STATUS = Namespace("http://pokemon.org/pokemon_status#")
    subject = URIRef(f"http://pokemon.org/pokemon_status#{name}")
    graph.add((subject, RDF.type, POKEMON_STATUS.Pokemon))
    graph.add((subject, POKEMON_STATUS.name, Literal(name)))
    graph.add((subject, POKEMON_STATUS.category, Literal(category)))
    graph.add((subject, POKEMON_STATUS.recommendedSolution, Literal(recommendedSolution)))
    graph.add((subject, POKEMON_STATUS.description, Literal(description)))
    
def add_pokemon_causes(graph,
    reason: str,
    reation: str,
    result: str,
    recommendedSolution: str):
    POKEMON_CAUSES = Namespace("http://pokemon.org/pokemon_causes#")
    subject = URIRef(f"http://pokemon.org/pokemon_causes#{reason}")
    graph.add((subject, RDF.type, POKEMON_CAUSES.Pokemon))
    graph.add((subject, POKEMON_CAUSES.reason, Literal(reason)))
    graph.add((subject, POKEMON_CAUSES.reation, Literal(reation)))
    graph.add((subject, POKEMON_CAUSES.result, Literal(result)))
    graph.add((subject, POKEMON_CAUSES.recommendedSolution, Literal(recommendedSolution)))
    

def create_pokemon_graph():
    pokemon_graph = Graph()
    # pokemon info
    add_pokemon_data(pokemon_graph, "皮卡丘", "001", "雷系", "", "雷丘")
    add_pokemon_data(pokemon_graph, "妙蛙種子", "002", "草系", "", "妙蛙花")
    add_pokemon_data(pokemon_graph, "小火龍", "003", "火系", "", "火恐龍")
    add_pokemon_data(pokemon_graph, "傑尼龜", "004", "水系", "", "卡咪龜")
    add_pokemon_data(pokemon_graph, "綠毛蟲", "005", "蟲系", "", "鐵甲蛹")
    add_pokemon_data(pokemon_graph, "雷丘", "006", "雷系", "皮卡丘", "")
    add_pokemon_data(pokemon_graph, "火恐龍", "007", "火系", "小火龍", "")
    add_pokemon_data(pokemon_graph, "卡咪龜", "008", "水系", "傑尼龜", "")
    add_pokemon_data(pokemon_graph, "鐵甲蛹", "009", "蟲系", "綠毛蟲", "")
    add_pokemon_data(pokemon_graph, "妙蛙花", "010", "草系", "妙花種子", "")
    add_pokemon_data(pokemon_graph, "超夢", "011", "超能力系", "", "")
    
    # status
    add_pokemon_status(pokemon_graph, "麻痺", "異常狀態", "可以使用解麻痺藥", "有機率無法行動")
    add_pokemon_status(pokemon_graph, "中毒", "異常狀態", "可以使用解毒藥", "每回合會扣血")
    add_pokemon_status(pokemon_graph, "睡眠", "異常狀態", "可以使用解眠藥", "無法行動")
    add_pokemon_status(pokemon_graph, "燒傷", "異常狀態", "可以使用燒傷藥", "每回合會扣血")
    add_pokemon_status(pokemon_graph, "凍結", "異常狀態", "可以使用解凍藥", "無法行動")
    
    add_pokemon_status(pokemon_graph, "凍結", "異常狀態", "可以送到寶可夢中心", "無法行動")
    add_pokemon_status(pokemon_graph, "中毒", "異常狀態", "可以送到寶可夢中心", "每回合會扣血")
    add_pokemon_status(pokemon_graph, "燒傷", "異常狀態", "可以送到寶可夢中心", "每回合會扣血")
    add_pokemon_status(pokemon_graph, "麻痺", "異常狀態", "可以送到寶可夢中心", "有機率無法行動")
    add_pokemon_status(pokemon_graph, "睡眠", "異常狀態", "可以送到寶可夢中心", "無法行動")
    
    # causes
    add_pokemon_causes(pokemon_graph, "被火屬性招式攻擊", "燒傷", "每回合會扣血", "可以使用燒傷藥")
    add_pokemon_causes(pokemon_graph, "被冰屬性招式攻擊", "凍結", "無法行動", "可以使用解凍藥")
    add_pokemon_causes(pokemon_graph, "被電屬性招式攻擊", "麻痺", "有機率無法行動", "可以使用解麻痺藥")
    add_pokemon_causes(pokemon_graph, "寶可夢受傷", "導致", "異常狀態", "可以送到寶可夢中心")
    add_pokemon_causes(pokemon_graph, "寶可夢生級至指定等級", "進化", "進化後的寶可夢", "無")
    add_pokemon_causes(pokemon_graph, "火系的寶可夢", "害怕水系", "受到的傷害會增加", "無")
    
    add_pokemon_status

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
    print(f"------------\nschema: {pokemon_rdf_graph.schema}\n------------")
    
    chain = create_qa_chain(pokemon_rdf_graph)
    instruction = """
    <ADDITIONAL INSTRUCTION>
    When you make the final query, REMOVE THESR ``` quotes and only have the query.
    Ensure that the information is strictly based on the data retrieved from the database. Do not mention any information that does not exist in the database.
    不要留下 ``` 引號，只留下查詢
    若結果為空，就回答 '查無資料'
    </ADDITIONAL INSTRUCTION>
    <schema>
        the pokemon_rdf_graph schema is {pokemon_rdf_graph.schema}
    </schema>
    """
    # query = "QUERY: 妙蛙草的number是多少？"
    # query = "QUERY: 皮卡丘的type是什麼？"
    # query = "QUERY: 妙蛙草的type是什麼？"
    # query = "QUERY: 資料庫中有多少種寶可夢？"
    # query = "QUERY: 有多少種名字是五個字的寶可夢？"
    # query = "QUERY: 有什麼寶可夢不能進化？"
    # query = "QUERY: 有哪幾種寶可夢能進化？"
    # query = "QUERY: 在Database中，妙蛙花的是從什麼寶可夢進化的？"
    # query = "QUERY: 在Database中，皮卡丘的是從什麼寶可夢進化的？"
    # query = "QUERY: 有哪些是異常狀態(status=異常狀態)？"
    # query = "QUERY: 我的皮卡丘中毒了，應該怎麼辦？" # fail.....
    # query = "QUERY: '中毒'應該怎麼辦？"
    query = "QUERY: 我的火恐龍被水屬性招式攻擊，會發生什麼事？"
    prompt = instruction + query
    print(prompt)
    response = chain.invoke(prompt, verbose=True)
    print(response["result"])

if __name__ == "__main__":
    main()
