from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from pydantic import BaseModel, Field
import operator



load_dotenv()


#  Model
model = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

# Define structured Output Schema
class ReviewSchema(BaseModel):
    feedback: str = Field(
        description="Detailed feedback about the review"
    )

    score: float = Field(
        description="Score out of 10",
        ge=0,
        le=10
    )


structured_model = model.with_structured_output(ReviewSchema)


# STEP 1: Define State
class ReviewState(TypedDict):
    review: str

    product_feedback: str
    sentiment_feedback: str
    customer_feedback: str

    final_summary: str

    scores: Annotated[list[float], operator.add]

    average_score: float


# STEP 2: Define Nodes


# Node 1: Evaluate Product Quality
def evaluate_product(state: ReviewState):

    prompt = f"""
Analyze the product quality based on this customer review.

Give:
- Detailed feedback
- Score out of 10

Review:
{state['review']}
"""

    output = structured_model.invoke(prompt)

    return {
        'product_feedback': output.feedback,
        'scores': [output.score]
    }


# Node 2: Analyze Sentiment
def analyze_sentiment(state: ReviewState):

    prompt = f"""
Analyze the sentiment of this customer review.

Evaluate:
- Positive aspects
- Negative aspects
- Overall customer sentiment

Give:
- Detailed feedback
- Score out of 10

Review:
{state['review']}
"""

    output = structured_model.invoke(prompt)

    return {
        'sentiment_feedback': output.feedback,
        'scores': [output.score]
    }


# Node 3: Evaluate Customer Experience
def evaluate_customer_experience(state: ReviewState):

    prompt = f"""
Analyze the customer experience described in this review.

Focus on:
- Customer satisfaction
- Problems faced by the customer
- Overall experience

Give:
- Detailed feedback
- Score out of 10

Review:
{state['review']}
"""

    output = structured_model.invoke(prompt)

    return {
        'customer_feedback': output.feedback,
        'scores': [output.score]
    }


# Node 4: Generate Final Summary
def generate_final_summary(state: ReviewState):

    prompt = f"""
Create a short final summary of this customer review.

Product Quality:
{state['product_feedback']}

Sentiment:
{state['sentiment_feedback']}

Customer Experience:
{state['customer_feedback']}

Give the final summary in a clear and concise way.
"""

    final_summary = model.invoke(prompt).content

    average_score = (
        sum(state['scores'])
        / len(state['scores'])
    )

    return {
        'final_summary': final_summary,
        'average_score': average_score
    }


# STEP 3: Create Graph
graph = StateGraph(ReviewState)


# STEP 4: Add Nodes
graph.add_node('evaluate_product', evaluate_product)
graph.add_node('analyze_sentiment', analyze_sentiment)
graph.add_node(
    'evaluate_customer_experience',
    evaluate_customer_experience
)
graph.add_node(
    'generate_final_summary',
    generate_final_summary
)


# STEP 5: Connect Edges

# Three independent nodes run in parallel
graph.add_edge(START, 'evaluate_product')
graph.add_edge(START, 'analyze_sentiment')
graph.add_edge(START, 'evaluate_customer_experience')

# Send all results to final summary
graph.add_edge(
    'evaluate_product',
    'generate_final_summary'
)

graph.add_edge(
    'analyze_sentiment',
    'generate_final_summary'
)

graph.add_edge(
    'evaluate_customer_experience',
    'generate_final_summary'
)

# End
graph.add_edge('generate_final_summary', END)


# STEP 6: Compile
workflow = graph.compile()


# STEP 7: Execute

initial_state = {
    'review': """
I bought this laptop three months ago and I am very happy
with its performance. The battery lasts around 7 hours,
which is good for my daily work. The keyboard is comfortable
and the display quality is excellent.

However, the laptop becomes slightly hot when I run heavy
applications. The speakers are also not very loud.

Overall, I think this is a good laptop for students and
developers, especially considering its price.
"""
}


final_state = workflow.invoke(initial_state)


# Final Result
print("Final Summary:")
print(final_state['final_summary'])

print("\nAverage Score:")
print(round(final_state['average_score'], 2))