from langgraph.graph import StateGraph, START, END
from typing import TypedDict


# STEP 1: Define the State 
class BMIState(TypedDict):
    weight_kg: float
    height_m: float
    bmi: float
    category: str 
    

#STEP 2:  Create Nodes 

# Node 1 : Calculate BMI 

def calculate_bmi(state:BMIState) ->BMIState:
    
    # Get weight and height from state 
    weight = state['weight_kg']  
    height = state['height_m']
    
    # Calculate BMI 
    bmi = weight/(height**2)
    
    return {'bmi': round(bmi, 2)} 

# Node 2: Label BMI category 
def label_bmi(state:BMIState)->BMIState:
    
    # get bmi from state
    bmi = state['bmi']
    
    # determine bmi category 
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"

    return {'category': category}

# STEP 3: Create Graph and Add Nodes

# Create StateGraph using BMIState
graph = StateGraph(BMIState)

# Add calculate_bmi node to graph
graph.add_node('calculate_bmi', calculate_bmi)

# Add label_bmi node to graph
graph.add_node('label_bmi', label_bmi)


# STEP 4 : Connect Nodes and define workflow 

graph.add_edge(START,'calculate_bmi') 

# Connect calculate_bmi to label_bmi
graph.add_edge('calculate_bmi', 'label_bmi')    
          
graph.add_edge('label_bmi',END)                   
                   
# STEP 5: Complie and excute 

#complie 
workflow = graph.compile()

initail_sate={
    'weight_kg':80,
    'height_m':1.73
}

# Execute the workflow

final_state = workflow.invoke(initail_sate)
print(final_state)

# STEP 6: Visualize the Graph
# Generate graph 
# graph_image = workflow.get_graph().draw_mermaid_png()

# # Save the graph image
# with open("bmi_workflow.png", "wb") as f:
#     f.write(graph_image)
