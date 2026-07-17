#  Ye file LangGraph agent ka flowchart aur nodes logic run karegi.
from typing import TypedDict, List, Dict, Any
from pydantic import BaseModel, Field  # for type-hinting and data validation
from langchain_groq import ChatGroq # For Groq LLM
from langchain_core.prompts import ChatPromptTemplate # For prompts
from langchain_community.tools import DuckDuckGoSearchRun # For search
from langgraph.graph import StateGraph, END # For building the graph

from config import settings
from embeddings import get_embedding
from db_services import insert_daily_log

# 1. State Schema Definition
class AgentState(TypedDict):
    raw_log: str            # Original user log input
    profession: str         # User's profession
    profile_id: str         # Supabase User Profile UUID
    analysis: Dict[str, Any]# Productive & wasted hours, score
    search_queries: List[str] # Web search queries for productivity advice
    search_results: str     # Combined results of web search
    final_report: str       # AI markdown report

# 2. Pydantic Model for Structured LLM Output

class LogAnalysisSchema(BaseModel):
    productive_hours: float = Field(description="Total productive hours spent during the day.")
    wasted_hours: float = Field(description="Total wasted or distracted hours spent during the day.")
    rating: float = Field(description="Overall productivity score from 0 to 100.")
    search_queries: List[str] = Field(
        description="List of 1-2 Google/DuckDuckGo search queries to find tips for the user's specific distractions. Leave empty if no significant time wasting."
    )

# Initialize LLM with Groq
llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=settings.GROQ_API_KEY)
# Bind structured output schema to LLM
structured_llm = llm.with_structured_output(LogAnalysisSchema)

# Initialize Search Tool
search_tool = DuckDuckGoSearchRun()

# --- 3. Node 1: Analyzer Node ---
def analyzer_node(state: AgentState) -> Dict[str, Any]:
    print("--- NODE: ANALYZER ---")
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are an expert productivity analyst. Review the user's log based on their profession. "
            "Determine how much time was spent productively (work, studying, meetings, writing code) "
            "versus how much time was wasted/distracted (scrolling social media, excessive gaming, procrastination). "
            "Calculate productive_hours, wasted_hours, and a rating score (0 to 100).\n"
            "If the user has wasted time, generate 1-2 search queries targeting their specific distraction (e.g., 'how to stop phone distraction')."
        )),
        ("human", "Profession: {profession}\nDaily Activity Log:\n{raw_log}")
    ])

    # Run LLM to get structured JSON
    chain = prompt | structured_llm
    result = chain.invoke({"profession": state["profession"], "raw_log": state["raw_log"]})

    return {"analysis": 
        {
            "productive_hours":result.productive_hours,
            "wasted_hours":result.wasted_hours,
            "rating":result.rating
        },
        "search_queries":result.search_queries
    }

# --- Node 2: Searcher Node ---
def searcher_node(state: AgentState) -> Dict[str, any]:
     print("--- NODE: SEARCHER ---")
     queries = state.get("search_queries",[])
     combined_results = []
     
     for q in queries:
        try:
            print(f"Searching for: {q}")
            res = search_tool.run(q)
            combined_results.append(f"Query: {q}\nResults: {res}\n---")
        except Exception as e:
            print(f"Search failed for {q}: {e}")
            
     return {"search_results": "\n".join(combined_results) if combined_results else "No tips found."}

# --- Node 3: Generator Node ---
def generator_node(state: AgentState) -> Dict[str, Any]:
    print("--- NODE: GENERATOR ---")
    prompt  = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a friendly, motivational AI Productivity Coach. "
            "Generate a comprehensive, beautiful Markdown report summarizing the user's day.\n"
            "Highlight:\n"
            "- A motivating summary.\n"
            "- Productive vs Wasted Time breakdown.\n"
            "- Actionable coaching tips based on the internet search results (if available).\n"
            "Keep the tone encouraging yet firm."
        )),
        ("human", (
            "Profession: {profession}\n"
            "Logs: {raw_log}\n"
            "Metrics: {analysis}\n"
            "Search Advice Context: {search_results}"
        ))
    ])

    chain = prompt  | llm
    result = chain.invoke({
        "profession": state["profession"],
        "raw_log": state["raw_log"],
        "analysis": state["analysis"],
        "search_results": state.get("search_results", "No extra search results.")
    })
    
    return {"final_report":result.content}

# --- Node 4: Saver Node --   
def saver_node(state: AgentState) -> Dict[str,Any]:
    print("--- NODE: SAVER ---")
    # 1. Text to Vector Convert karein (Semantic Search ke liye)
    vector = get_embedding(state["raw_log"])

    # 2. Database service call karke row insert karein
    insert_daily_log(
        profile_id=state["profile_id"],
        raw_log=state["raw_log"],
        productive_hours=state["analysis"]["productive_hours"],
        wasted_hours=state["analysis"]["wasted_hours"],
        score=state["analysis"]["rating"],
        report_content=state["final_report"],
        embedding=vector
    )
    print("Saved report to database successfully!")
    return {}


## --- 4. Conditional Edge Router ---
    # Agar search queries generate hui hain to search node pe jao, varna direct report generation pe
def router(state: AgentState) -> str:
    if state.get("search_queries"):
        return "searcher"
    return "generator" 

# --- 5. Graph Pipeline Assembly ---
workflow = StateGraph(AgentState)     

# Nodes register karein

workflow.add_node("analyzer",analyzer_node)
workflow.add_node("searcher",searcher_node)
workflow.add_node("generator",generator_node)
workflow.add_node("saver",saver_node)

# Flow defined karein (Edges)
workflow.set_entry_point("analyzer")
workflow.add_conditional_edges(
    "analyzer",
    router,
    {
        "searcher": "searcher",
        "generator": "generator"
    }
)
workflow.add_edge("searcher", "generator")
workflow.add_edge("generator", "saver")
workflow.add_edge("saver", END)

# Compile graph
app_agent = workflow.compile()