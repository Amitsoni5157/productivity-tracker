# FocusAI - System Architecture Diagram

Below is the Figma-style system architecture diagram representing our full-stack system flow:

![System Architecture Flowchart](file:///C:/Users/HP-LAPTOP/.gemini/antigravity-ide/brain/666970e4-e708-4e02-9706-e692528be754/architecture_flow_diagram_1784343162216.png)

---

## Component Key:
1. **Frontend (Next.js)**: Receives user logs and settings, calls the API server, and displays rich metrics cards and markdown advice.
2. **Backend (FastAPI)**: Validates requests, interacts with the Supabase client, and triggers the AI workflow agent.
3. **AI Agent (LangGraph)**: Evaluates schedules, runs conditional search node logic via DuckDuckGo, compiles reports, and triggers storage.
4. **Database (Supabase)**: Stores relational user data, and uses `pgvector` to save log embeddings for future semantic searching.
