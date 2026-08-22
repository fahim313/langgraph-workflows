from langgraph.graph import StateGraph,START,END 
from typing import TypedDict


# Step 1: Define state 
class LoanState(TypedDict):
    salary: int 
    decision:str 
    
# Step 2: Define Router/ Decision Function 
def check_loan_decision(state:LoanState):
    salary = state['salary']
    
    if salary<25000:
        return "reject"
    elif salary<50000:
        return "review"
    else:
        return "approve"
    
# Step 3: Define Nodes 

def approve_loan(state:LoanState):
    return{
        "decision":"Loan Approved"
    }    

def review_loan(state:LoanState):
    return{
        "decision":"Manual Review Required"
    }   

def reject_loan(state:LoanState):
    return{
        "decision":"Loan Rejected"
    }  
    
# Step 4: Create Graph 

graph =StateGraph(LoanState)

# Step 5: Add Nodes 
graph.add_node("approve", approve_loan)
graph.add_node("review", review_loan)
graph.add_node("reject", reject_loan) 

# Step 6: Connect conditional Edges 
# START → Decision Router → Selected Node 

graph.add_conditional_edges(
    START,
    check_loan_decision,
    {
        "approve":"approve",
        "review": "review",
        "reject": "reject"
    }
) 

# Step 7: End 
graph.add_edge("approve", END)
graph.add_edge("review", END)
graph.add_edge("reject", END) 

# Step 8: Compile 
workflow = graph.compile()
           
# Step 10: Execute 

# user input 
salary = int(input("Enter your monthly salary:"))

intial_state ={
    "salary":salary
}

final_state = workflow.invoke(intial_state)    
print(final_state)    