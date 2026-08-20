from langgraph.graph import StateGraph,START,END
from typing import TypedDict 
from dotenv import load_dotenv
from langchain_groq import ChatGroq 

load_dotenv() 

# model 
model = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

# step 1: Define the State 
class BlogState(TypedDict):
    title: str
    outline: str 
    content: str 

# step 2: Create Node  
# ---------------------
# Node 1: Create Outline 
def create_outline(state:BlogState)->BlogState:
    
    title = state['title']
    
    prompt = f"""
Generate a detailed outline for a blog on the topic: {title}

Important formatting rules:
- Use plain text only.
- Do not use Markdown.
- Do not use # symbols.
- Do not use * or ** symbols.
- Do not use --- separators.
- Do not use tables.
- Use simple numbered sections and bullet points only.
"""
    
    outline = model.invoke(prompt).content
    
    state['outline'] = outline 
    
    return state 

# Node2: Create Blog 
def create_blog(state:BlogState)->BlogState:
    title = state['title']
    outline = state['outline']
    
    prompt =f"""
    Write a detailed blog on the title: {title}

Use the following outline:
{outline}

Important:
- Write in plain text only.
- Do not use Markdown formatting.
- Do not use # headings.
- Do not use **bold** or *italic*.
- Do not use tables.
- Do not use --- separators.
    """
    content = model.invoke(prompt).content
    
    state['content']=content
    return state 

# Step3: create Graph 
graph = StateGraph(BlogState) 

# step 4:  Add the Nodes 
graph.add_node('create_outline', create_outline)
graph.add_node('create_blog', create_blog)

# step5: connect Edges 
graph.add_edge(START,'create_outline')
graph.add_edge('create_outline','create_blog')
graph.add_edge('create_blog',END)

# step 6: compile workflow 
workflow = graph.compile() 

initial_state ={
    'title':'The Future of Remote work'
}

# step 6: Execute workflow 

final_state = workflow.invoke(initial_state)

# print(final_state)

print(final_state['outline'])

print(final_state['content'])





    