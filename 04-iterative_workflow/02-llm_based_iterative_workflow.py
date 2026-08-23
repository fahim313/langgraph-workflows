from langgraph.graph import StateGraph,START,END 
from typing import TypedDict,Literal,Annotated
from langchain_groq import ChatGroq 
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint 
from langchain_core.messages import SystemMessage,HumanMessage 
from pydantic import BaseModel,Field 
from dotenv import load_dotenv
import operator


load_dotenv()

# Step 1:  Models 

# Generator -->Groq 
generator_llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.7
)

# Evaluator-->Gemini 
evaluator_llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)

# Optimizer-->Hugging Face 
hf_endpoint = HuggingFaceEndpoint(
     repo_id="google/gemma-3-4b-it",
    task="text-generation",
    max_new_tokens=100,
)

optimizer_llm = ChatHuggingFace(
    llm=hf_endpoint
)

# Step 2: Structured Output

class LinkedInEvaluation(BaseModel):

    evaluation: Literal[
        "approved",
        "needs_improvement"
    ] = Field(
        description="Final evaluation result"
    )

    feedback: str = Field(
        description="Detailed feedback for the LinkedIn post"
    )


structured_evaluator_llm = evaluator_llm.with_structured_output(
    LinkedInEvaluation
)  


# Step 3: Define the state 
class LinkedInState(TypedDict):

    topic: str

    post: str

    evaluation: Literal[
        "approved",
        "needs_improvement"
    ]

    feedback: str

    iteration: int

    max_iteration: int

    post_history: Annotated[
        list[str],
        operator.add
    ]

    feedback_history: Annotated[
        list[str],
        operator.add
    ]
    
# Generate linkedin post 

def generate_post(state: LinkedInState):

    print("\nGenerating LinkedIn post...")

    messages = [

        SystemMessage(
            content="""
You are an expert LinkedIn content creator.

Your job is to write engaging, professional,
and authentic LinkedIn posts.
"""
        ),

        HumanMessage(
            content=f"""
Write a LinkedIn post about:

"{state['topic']}"

Rules:

- Write in simple English.
- Make it engaging and professional.
- Start with a strong hook.
- Share a useful insight or lesson.
- Make it relatable.
- Avoid fake motivational quotes.
- Avoid excessive emojis.
- Avoid corporate buzzwords.
- Keep it under 1500 characters.
- Do not use question-answer format.
"""
        )
    ]

    response = generator_llm.invoke(messages)

    post = response.content

    return {
        "post": post,
        "post_history": [post]
    }
    
# Evaluate the post 

def evaluate_post(state: LinkedInState):

    print("\nEvaluating LinkedIn post...")

    messages = [

        SystemMessage(
            content="""
You are a strict LinkedIn content evaluator.

Evaluate posts based on:

1. Hook
2. Clarity
3. Value
4. Authenticity
5. Readability
6. Engagement potential
7. Professional tone
8. Overall LinkedIn quality
"""
        ),

        HumanMessage(
            content=f"""
Evaluate the following LinkedIn post.

Topic:
"{state['topic']}"

Post:
"{state['post']}"

Approve the post only if it is good enough
to publish on LinkedIn.

Needs improvement if:

- The opening hook is weak.
- The post provides little value.
- It feels generic or AI-generated.
- It is too repetitive.
- It uses unnecessary buzzwords.
- It lacks a clear message.
- It is not engaging.

Respond ONLY in structured format:

evaluation:
"approved" or "needs_improvement"

feedback:
Explain the strengths and weaknesses
and what should be improved.
"""
        )
    ]

    response = structured_evaluator_llm.invoke(messages)

    return {

        "evaluation": response.evaluation,

        "feedback": response.feedback,

        "feedback_history": [
            response.feedback
        ]
    } 
    
# Optimize the post 

def optimize_post(state: LinkedInState):

    print("\nImproving LinkedIn post...")

    messages = [

        SystemMessage(
            content="""
You are an expert LinkedIn copywriter.

Improve the LinkedIn post based on
the evaluator's feedback.

Make the post more natural,
valuable, engaging, and professional.
"""
        ),

        HumanMessage(
            content=f"""
Improve the following LinkedIn post.

Topic:
"{state['topic']}"

Current Post:
"{state['post']}"

Evaluator Feedback:
"{state['feedback']}"

Rewrite the entire post.

Rules:

- Keep it under 1500 characters.
- Start with a strong hook.
- Provide real value.
- Keep it authentic.
- Use simple English.
- Avoid generic motivational language.
- Avoid excessive emojis.
- Avoid corporate buzzwords.
- Do not explain what you changed.
- Return ONLY the improved LinkedIn post.
"""
        )
    ]

    response = optimizer_llm.invoke(messages)

    post = response.content

    iteration = state["iteration"] + 1

    return {

        "post": post,

        "iteration": iteration,

        "post_history": [post]
    } 
    
# Route/decision function 
def route_evaluation(state: LinkedInState):

    if (
        state["evaluation"] == "approved"
        or
        state["iteration"] >= state["max_iteration"]
    ):

        return "approved"

    else:

        return "needs_improvement"
    
# create Graph 
graph = StateGraph(LinkedInState) 

# Add Nodes 

graph.add_node("generate",generate_post)
graph.add_node("evaluate",evaluate_post)
graph.add_node("optimize",optimize_post)

# Connect Edge 
graph.add_edge(START,"generate")
graph.add_edge("generate","evaluate")
graph.add_conditional_edges(
    "evaluate",
    route_evaluation,
    {
        "approved":END,
        "needs_improvement":"optimize"
    }
)
graph.add_edge("optimize","evaluate")

# compile 
workflow = graph.compile()

# user input 
topic = input(
    "Enter LinkedIn post topic: "
)
# Execute 
initial_state = {

    "topic": topic,

    "iteration": 1,

    "max_iteration": 5
}
result = workflow.invoke(
    initial_state
)

print("FINAL LINKEDIN POST")

print(result["post"])