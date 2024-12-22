import os
from typing import List
from rdflib import Graph, URIRef, Literal, Namespace, XSD, RDF
from langchain.chains import GraphSparqlQAChain
from langchain_community.graphs import RdfGraph
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI

from langchain import PromptTemplate

class SPARQLTool(BaseTool):
    name: str = "SPARQLTool"
    description:str = (
        "A tool for querying the RDF knowledge base about Pokemon. "
        "Input is a natural language query. Output is the result from the RDF database."
        "不需要提供rdf 語法，只需要提供自然語言問題即可，例如：'夢幻的type是什麼?'"
        "寶可夢的名字只提供使用中文來詢問"
        "不要用英文的名字來詢問"
    )
    rdf_schema: str = ""
    sparql_chain: GraphSparqlQAChain = None
    prompt: PromptTemplate = None
    
    def __init__(self):
        super().__init__()
        graph = self.create_pokemon_graph()
        graph.serialize("pokemon.rdf", format="n3")
        pokemon_rdf_graph = RdfGraph(source_file="pokemon.rdf", standard="rdf")
        pokemon_rdf_graph.load_schema()
        self.rdf_schema = pokemon_rdf_graph.schema
        # print(f"------------\nschema: {self.rdf_schema}\n------------")    
        self.sparql_chain = self.create_qa_chain(pokemon_rdf_graph)
        instruction_prompt_str = """
        <instruction>
        When you make the final query, REMOVE THESR ``` quotes and only have the query.
        若結果為空，就回答 '查無資料'
        Ensure that the information is strictly based on the data retrieved from the database. Do not mention any information that does not exist in the database.
        不要留下 ``` 引號，只留下查詢。
        不要提及資料庫中不存在的資訊，直接將資料庫中的資訊回答即可。
        </instruction>
        <schema>
            the pokemon_rdf_graph schema is {rdf_schema}
        </schema>
        <user_question>
        {user_question}
        </user_question>
        """
        
        self.prompt = PromptTemplate(
            input_variables = ["rdf_schema", "user_question"],
            template = instruction_prompt_str
        )

    def _run(self, user_question: str) -> str:
        # use PromptTemplate to generate the prompt
        prompt = self.prompt.format(user_question=user_question, rdf_schema=self.rdf_schema)
        response = self.sparql_chain.invoke(prompt, verbose=True)
        # print(f"------------\n response: {response}\n------------")    
        return response["result"]
    
    @staticmethod
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
    @staticmethod
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
        
    @staticmethod
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
        
    @property
    def graph(self):
        if self._graph is None:
            self._graph = self.create_pokemon_graph()
        return self._graph

    def create_pokemon_graph(self):
        pokemon_graph = Graph()
        # pokemon info
        self.add_pokemon_data(pokemon_graph, "皮卡丘", "001", "雷系", "", "雷丘")
        self.add_pokemon_data(pokemon_graph, "妙蛙種子", "002", "草系", "", "妙蛙花")
        self.add_pokemon_data(pokemon_graph, "小火龍", "003", "火系", "", "火恐龍")
        self.add_pokemon_data(pokemon_graph, "傑尼龜", "004", "水系", "", "卡咪龜")
        self.add_pokemon_data(pokemon_graph, "綠毛蟲", "005", "蟲系", "", "鐵甲蛹")
        self.add_pokemon_data(pokemon_graph, "雷丘", "006", "雷系", "皮卡丘", "")
        self.add_pokemon_data(pokemon_graph, "火恐龍", "007", "火系", "小火龍", "")
        self.add_pokemon_data(pokemon_graph, "卡咪龜", "008", "水系", "傑尼龜", "")
        self.add_pokemon_data(pokemon_graph, "鐵甲蛹", "009", "蟲系", "綠毛蟲", "")
        self.add_pokemon_data(pokemon_graph, "妙蛙花", "010", "草系", "妙花種子", "")
        self.add_pokemon_data(pokemon_graph, "超夢", "011", "超能力系", "", "")
        
        # status
        self.add_pokemon_status(pokemon_graph, "麻痺", "異常狀態", "可以使用解麻痺藥", "有機率無法行動")
        self.add_pokemon_status(pokemon_graph, "中毒", "異常狀態", "可以使用解毒藥", "每回合會扣血")
        self.add_pokemon_status(pokemon_graph, "睡眠", "異常狀態", "可以使用解眠藥", "無法行動")
        self.add_pokemon_status(pokemon_graph, "燒傷", "異常狀態", "可以使用燒傷藥", "每回合會扣血")
        self.add_pokemon_status(pokemon_graph, "凍結", "異常狀態", "可以使用解凍藥", "無法行動")
        
        self.add_pokemon_status(pokemon_graph, "凍結", "異常狀態", "可以送到寶可夢中心", "無法行動")
        self.add_pokemon_status(pokemon_graph, "中毒", "異常狀態", "可以送到寶可夢中心", "每回合會扣血")
        self.add_pokemon_status(pokemon_graph, "燒傷", "異常狀態", "可以送到寶可夢中心", "每回合會扣血")
        self.add_pokemon_status(pokemon_graph, "麻痺", "異常狀態", "可以送到寶可夢中心", "有機率無法行動")
        self.add_pokemon_status(pokemon_graph, "睡眠", "異常狀態", "可以送到寶可夢中心", "無法行動")
        
        # causes
        self.add_pokemon_causes(pokemon_graph, "被火屬性招式攻擊", "燒傷", "每回合會扣血", "可以使用燒傷藥")
        self.add_pokemon_causes(pokemon_graph, "被冰屬性招式攻擊", "凍結", "無法行動", "可以使用解凍藥")
        self.add_pokemon_causes(pokemon_graph, "被電屬性招式攻擊", "麻痺", "有機率無法行動", "可以使用解麻痺藥")
        self.add_pokemon_causes(pokemon_graph, "寶可夢受傷", "導致", "異常狀態", "可以送到寶可夢中心")
        self.add_pokemon_causes(pokemon_graph, "寶可夢生級至指定等級", "進化", "進化後的寶可夢", "無")
        self.add_pokemon_causes(pokemon_graph, "火系的寶可夢", "害怕水系", "受到的傷害會增加", "無")
        self.add_pokemon_causes(pokemon_graph, "水系的寶可夢", "害怕草系", "受到的傷害會增加", "無")
        self.add_pokemon_causes(pokemon_graph, "草系的寶可夢", "害怕火系", "受到的傷害會增加", "無")
        
        return pokemon_graph
    
    @staticmethod
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
if __name__ == "__main__":
    tool = SPARQLTool()
    question_list = [
        "皮卡丘的type是什麼?",
        "資料庫中有多少種寶可夢?",
        "有多少種名字是五個字的寶可夢?",
        "有什麼寶可夢不能進化?",
        "妙蛙花是妙蛙種子的進化形態嗎?",
        "妙蛙花是什麼type?",
        "妙蛙花的number是多少?",
    ]
    for question in question_list:
        result = tool._run(question)
        print(result)
        break