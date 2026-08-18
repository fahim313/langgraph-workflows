from langgraph.graph import StateGraph, START, END
from typing import TypedDict 
from langchain_groq import ChatGroq 
from dotenv import load_dotenv

load_dotenv()

# model 
model = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

# step 1: define the state 
class MyState(TypedDict):
    question: str 
    answer: str 


# step 2: Create the node 
def ask_llm(state: MyState) -> MyState:
    
    question = state["question"]
    response = model.invoke(question)
    
    return {
        "answer": response.content
    }

# step 3: create a graph
graph = StateGraph(MyState)
    
# step 4: add the node
graph.add_node("ask_llm", ask_llm)

# step 5: connect the edges
graph.add_edge(START, "ask_llm")
graph.add_edge("ask_llm", END)

# step 6: compile and execute
workflow = graph.compile()

result = workflow.invoke({
    "question": "What is Machine learning?"
})  

print(result) 
print(result["answer"])