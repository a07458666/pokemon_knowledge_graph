import os
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from sparql_tool import SPARQLTool 

def create_react_agent() -> "AgentExecutor":
    """
    Create a ReAct agent that can use SPARQLTool to query Pokemon RDF knowledge base.
    """
    # 1) 建立工具清單
    sparql_tool = SPARQLTool()
    tools = [sparql_tool]

    # 2) 準備 LLM (OpenAI ChatGPT)
    llm = ChatOpenAI(
        temperature=0,
    )

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )
    return agent

if __name__ == "__main__":
    agent = create_react_agent()

    # 用戶問題
    queries = [
        # "皮卡丘的type是什麼？",
        # "資料庫中有多少種寶可夢？",
        # "我的火恐龍被水屬性招式攻擊會怎麼樣？",
        # "我的皮卡丘被冰屬性招式攻擊可能會怎麼樣？",
        "我的皮卡丘被冰屬性招式攻擊可能會導致什麼異常狀態？",
    ]
    for q in queries:
        print(f"\nUser question: {q}")
        answer = agent.run(q)  # 直接呼叫 agent.run(使用者問題)
        print(f"Final Answer: {answer}\n")
        break