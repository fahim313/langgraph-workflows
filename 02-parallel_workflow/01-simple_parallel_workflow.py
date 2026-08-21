from langgraph.graph import StateGraph,START,END
from typing import TypedDict 


# Step 1: Define state 
class StudentState(TypedDict):
    math:float
    physics:float 
    chemistry:float 
    
    total:float 
    average:float 
    highest_mark:float 
    summary:float 
    
    
# Step 2: Define Nodes 

# Node 1: Calculate Total 
def calculate_total(state:StudentState):
    total = state['math']+state['physics']+state['chemistry']
    
    return{'total':total}

# Node 2: Calculate Average
def calculate_average(state:StudentState):
    average=(
        state['math']+
        state['physics']+
        state['chemistry']
    )/3
    return{'average':round(average,2)}

# Node 3: Find Highest Mark 
def find_highest_mark(state:StudentState):
    highest_mark = max(
        state['math'],
        state['physics'],
        state['chemistry']
    )
    return{'highest_mark':highest_mark}

# Node 4: Create summary 
def create_summary(state: StudentState):
    summary = f"""
    Total Marks: {state['total']}
    Average Marks: {state['average']}
    Highest Mark: {state['highest_mark']}
    """

    return {'summary': summary}

# Step 3: Create Graph
graph = StateGraph(StudentState)
    
# Step 4: Add Nodes 
graph.add_node('calculate_total', calculate_total)
graph.add_node('calculate_average', calculate_average)
graph.add_node('find_highest_mark',find_highest_mark)
graph.add_node('create_summary',create_summary)


# Step 5: Connect Edges 

# start three independent calculations in parallal 
graph.add_edge(START,'calculate_total')
graph.add_edge(START,'calculate_average')
graph.add_edge(START,'find_highest_mark')


# All three calculations go to the summary node
graph.add_edge('calculate_total', 'create_summary')
graph.add_edge('calculate_average','create_summary')
graph.add_edge('find_highest_mark','create_summary')

# End the workflow 
graph.add_edge('create_summary',END)


# Step 6: Compile 
workflow = graph.compile()

# Step 7: Execute 
inital_state = {
    'math':85,
    'physics':78,
    'chemistry':92
}

final_state = workflow.invoke(inital_state)

print(final_state['summary'])        