# FocusAI - Daily Activity Log & Agent Workflow Flowchart

This document contains a step-by-step explanation and visual diagram of the daily activity log analysis flow, including our LangGraph AI Agent's execution.

---

## 1. Flow Diagram (Sequence Chart)

```mermaid
sequenceDiagram
    autonumber
    actor User as Amit (User Browser)
    participant FE as Frontend (page.tsx)
    participant BE as Backend (main.py)
    participant AG as LangGraph Agent (agent.py)
    participant LLM as Groq API (Llama-3)
    participant DB as Supabase PostgreSQL

    User->>FE: Types daily schedule + clicks "Generate Analysis Report"
    Note over FE: handleAnalyzeLogs() starts (Line 80)
    FE->>BE: fetch() -> POST request to /analyze (Line 88)
    Note over BE: api_analyze_log() runs (Line 48)
    BE->>DB: Checks if Amit exists in profiles (Line 49)
    DB-->>BE: Profile Verified
    
    Note over BE: CALLING AGENT: app_agent.invoke() (Line 68)
    BE->>AG: Triggers LangGraph flowchart
    
    Note over AG: Node 1: analyzer_node (Line 42)
    AG->>LLM: Computes productive/wasted hours + queries (structured JSON)
    LLM-->>AG: Returns hours and focus tips search queries
    
    Note over AG: Router Checks: Any search queries? (Line 137)
    alt Yes, distraction found
        Note over AG: Node 2: searcher_node (Line 72)
        AG->>AG: Searches DuckDuckGo for focus advice
    end
    
    Note over AG: Node 3: generator_node (Line 85)
    AG->>LLM: Compiles logs, metrics & search results into markdown
    LLM-->>AG: Returns motivational Markdown report
    
    Note over AG: Node 4: saver_node (Line 116)
    AG->>AG: Converts log to 384-dim numeric vector (embeddings.py)
    AG->>DB: SQL INSERT to productivity_logs (with embedding)
    
    AG-->>BE: Returns final register state (invoke finished)
    BE-->>FE: Returns JSON payload (Line 97)
    
    Note over FE: setReport(data) is called (Line 100)
    FE->>User: Renders metrics cards and Markdown report on Dashboard
```

---

## 2. Step-by-Step Code Walkthrough

### Step 1: Frontend Submission
* **File:** [page.tsx](file:///e:/ai_agent_in_python/frontend/app/page.tsx#L80-L109)
* **Code:** `handleAnalyzeLogs`
* **Why:** Frontend sends user's textarea string, profession, and profile_id over the internet to `/analyze`.

### Step 2: Backend Check & Invoke Agent
* **File:** [main.py](file:///e:/ai_agent_in_python/backend/main.py#L48-L79)
* **Code:** `api_analyze_log`
* **Why:** Backend verifies the profile in database, prepares a fresh dictionary (register), and kicks off the AI workflow using **`app_agent.invoke(state_input)`**.

### Step 3: LangGraph Agent Steps
* **File:** [agent.py](file:///e:/ai_agent_in_python/backend/agent.py)

1. **`analyzer_node` (Line 42)**: Uses Groq to split schedule into productive and wasted hours. It also registers search keywords if distractions are present.
2. **`router` (Line 137)**: Evaluates the register. If search queries are present, it redirects to the `searcher`, otherwise directly to the `generator`.
3. **`searcher_node` (Line 72)** (Conditional): Executes DuckDuckGo API to extract focus suggestions online.
4. **`generator_node` (Line 85)**: Compiles all information and uses Groq to write the final motivational markdown coaching report.
5. **`saver_node` (Line 116)**:
   - Transforms raw log text into vector numbers via `embeddings.py` (HuggingFace cache).
   - Writes the full row entry to the `productivity_logs` database table.

### Step 4: Frontend Presentation
* **File:** [page.tsx](file:///e:/ai_agent_in_python/frontend/app/page.tsx#L100)
* **Code:** `setReport(data)`
* **Why:** React detects the state change, stops the loading spinner, and displays the final productivity cards and AI deep dive report on the user dashboard.
