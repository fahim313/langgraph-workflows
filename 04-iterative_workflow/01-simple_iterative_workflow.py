from langgraph.graph import StateGraph,START,END 
from typing import TypedDict 


# Step 1: Define the State 
class CounterState(TypedDict):
    count: int 
    

# Step 2: Define Node 
def increment(state:CounterState):
    count = state['count']
    return{
        "count":count+1
    }  
    
# Step 2: Router/Decision Function 
def check_count(state:CounterState):
    count= state['count']
    if count<5:
        return "continue"
    
    else:
        return "stop"      

# Create Graph 
graph= StateGraph(CounterState)    

# Add Node 
graph.add_node("increment",increment)

# Connect Edges 
graph.add_edge(START,'increment') 

# conditional 
graph.add_conditional_edges(
    "increment",
    check_count,
    {
        "continue":"increment",
        "stop":END
    }
)

# compile
workflow = graph.compile()

# Execute 
initial_state ={
    "count":0
}

final_state = workflow.invoke(initial_state)
print(final_state)