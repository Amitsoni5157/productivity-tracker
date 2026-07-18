# FocusAI - Project Flow & Working Guide (Simple English)

This document provides a simple, beginner-friendly explanation of how the FocusAI project works (Workflow) and how the code modules connect (Code Flow).

---

## 1. Project Analogy: The AI Productivity Clinic

To understand the system workflow, imagine our application as a **specialized health clinic** where a patient (the user) wants to check their focus health:

1. **The Receptionist (Next.js Frontend - `frontend/app/page.tsx`)**:
   * This is the front desk of the clinic. The user fills in their details (Name, Profession) or daily schedule, writes it on a sheet of paper (logs), and submits it.
2. **The Head Doctor (FastAPI Backend - `backend/main.py`)**:
   * The Head Doctor receives the sheet of paper. First, they check the database files to verify: *"Is this patient registered in our clinic?"* (Profile validation). If yes, they hand the paper to the **Specialized AI Team** to begin analysis.
3. **The Specialized AI Team (LangGraph Agent - `backend/agent.py`)**:
   * This team consists of 4 specialists who pass a **Case Notebook (State)** to one another:
     * **Specialist 1: The Calculator (Analyzer Node)**: Evaluates the schedule using Llama-3, calculates productive and wasted hours, and generates a focus score (0-100). If distractions are found, they write a search note: *"Search focus tips on the internet"*.
     * **The Corridor Guard (Router Edge)**: Reads the notebook. If a search note exists, they send the notebook to the **Researcher**. If no distractions exist, they bypass the Researcher and send it directly to the **Report Writer**.
     * **Specialist 2: The Google Researcher (Searcher Node)**: Runs the DuckDuckGo search tool to fetch practical tips for the user's specific distraction.
     * **Specialist 3: The Motivational Writer (Generator Node)**: Reviews the metrics and internet advice to compile a beautiful, encouraging Markdown report.
     * **Specialist 4: The Archive Clerk (Saver Node)**: Translates the raw log text into a unique coordinate code (Embeddings via HuggingFace) and saves the entire record in the **Hospital Filing Cabinet (Supabase PostgreSQL)**.
4. **Final Delivery**:
   * Once archived, the AI Team returns the notebook to the Head Doctor (FastAPI), who sends the report back to the Receptionist (Next.js). The frontend stops the loading spinner and displays the results on the dashboard screen!

---

## 2. File Structure & Decoupled Responsibilities

The codebase uses a **decoupled architecture**, meaning each file is independent and does only one specific job:

```text
e:\ai_agent_in_python/
├── backend/
│   ├── config.py         # [Config Manager]: Loads API keys and environment variables (no other code initialization).
│   ├── db_client.py      # [DB Connector]: Starts the Supabase connection client.
│   ├── db_services.py    # [DB Queries]: Handles creating profiles, inserting logs, and vector searches.
│   ├── embeddings.py     # [Math Translator]: Transforms text logs into 384-dimensional float arrays (embeddings).
│   ├── agent.py          # [AI Logic - LangGraph]: Defines the AI flowchart, nodes, router edge, and Llama-3 templates.
│   └── main.py           # [API Server]: Exposes URL endpoints (/profile, /analyze) for the frontend to call.
│
├── frontend/
│   └── app/
│       ├── layout.tsx    # [Main Layout]: Handles the global HTML page layout and styling defaults.
│       └── page.tsx      # [Dashboard UI]: Handles login, input forms, state hooks, and displays metrics cards.
```

---

## 3. Step-by-Step Data Flow

### Flow A: User Profile Creation (Registration)
1. The user inputs their Name and Profession in **`page.tsx`** and clicks "Get Started".
2. The browser triggers an HTTP request to **`main.py`** at the `/profile` endpoint.
3. The server calls the query function in **`db_services.py`**.
4. Supabase inserts a new row in the `profiles` table, generates a unique **Secret ID (UUID)**, and returns it.
5. The frontend receives the response, saves the ID in the browser's persistent memory (**LocalStorage**), and swaps the setup screen for the main dashboard.

### Flow B: Daily Activity Log Processing (Analysis)
1. The user types their daily logs in **`page.tsx`** and clicks "Generate Analysis Report".
2. The frontend triggers a request to **`main.py`** at the `/analyze` endpoint.
3. The backend validates the user and triggers the LangGraph agent: `app_agent.invoke()`.
4. The LangGraph agent executes nodes in sequence:
   * **`analyzer_node`** (LLM calculations) $\rightarrow$ **`router`** (logic split) $\rightarrow$ **`searcher_node`** (DDG search) $\rightarrow$ **`generator_node`** (markdown compilation).
5. **`saver_node`** calls `embeddings.py` to create vectors and saves the report to Supabase.
6. The backend returns the final state to the frontend, which updates the React state and displays the score cards and coaching tips.
