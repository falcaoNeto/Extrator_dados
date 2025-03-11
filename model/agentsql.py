from langchain_community.utilities.sql_database import SQLDatabase
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits.sql.prompt import SQL_FUNCTIONS_SUFFIX
from model.LLm import LLm

class Agent:
    def __init__(self):
        self.llm = LLm().llm_instance("gemini")
        self.db = SQLDatabase.from_uri("sqlite:///BD/database.db")
        
        self.custom_suffix = (
            "Responda SEMPRE em português brasileiro. Mantenha as respostas curtas e diretas.\n"
            + SQL_FUNCTIONS_SUFFIX
        )

        self.agent = create_sql_agent(
            llm=self.llm,
            db=self.db,
            agent_type="tool-calling",
            verbose=True,
            suffix=self.custom_suffix  
        )
    
    def agent_response(self, question):
        response = self.agent.invoke({"input": question})
        return response["output"]

if __name__ == "__main__":
    agnt = Agent()
    resp = agnt.agent_response("Qual é a soma total das notas fiscais?")
    print(resp)