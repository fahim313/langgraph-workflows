from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()


# MODEL
model = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)


# Step 1: Define State
class LoanState(TypedDict):
    application: str
    salary: int
    decision: str


# Step 2: Preparation Node
# LLM analyze user application and extract salary 
def evaluate_loan_requirement(state: LoanState):

    print("Evaluating loan application...")

    application = state["application"]

    prompt = f"""
    Analyze the following loan application.

    Extract the applicant's monthly salary.

    Application:
    {application}

    Return only the salary as a number.
    """

    response = model.invoke(prompt)

    salary = int(
        response.content.strip().replace(",", "")
    )

    return {
        "salary": salary
    }


# Step 3: Router / Decision Function
def check_loan_decision(state: LoanState):

    salary = state["salary"]

    print("Extracted salary:", salary)

    if salary < 25000:
        return "reject"

    elif salary < 50000:
        return "review"

    else:
        return "approve"


# Step 4: Define Nodes

def approve_loan(state: LoanState):
    return {
        "decision": "Loan Approved"
    }


def review_loan(state: LoanState):
    return {
        "decision": "Manual Review Required"
    }


def reject_loan(state: LoanState):
    return {
        "decision": "Loan Rejected"
    }


# Step 5: Create Graph
graph = StateGraph(LoanState)


# Step 6: Add Nodes

graph.add_node(
    "evaluate_loan_requirement",
    evaluate_loan_requirement
)

graph.add_node("approve", approve_loan)
graph.add_node("review", review_loan)
graph.add_node("reject", reject_loan)


# Step 7: Connect START → Preparation Node

graph.add_edge(
    START,
    "evaluate_loan_requirement"
)


# Step 8: Preparation Node → Router → Selected Node

graph.add_conditional_edges(
    "evaluate_loan_requirement",
    check_loan_decision,
    {
        "approve": "approve",
        "review": "review",
        "reject": "reject"
    }
)


# Step 9: Selected Node → END

graph.add_edge("approve", END)
graph.add_edge("review", END)
graph.add_edge("reject", END)


# Step 10: Compile

workflow = graph.compile()


# Step 11: User Input

application = input(
    "Enter your loan application: "
)


# Step 12: Execute

initial_state = {
    "application": application
}

final_state = workflow.invoke(initial_state)


print(final_state)