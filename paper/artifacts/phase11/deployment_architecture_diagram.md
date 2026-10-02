# SupplyTwinAI — Cloud Deployment Architecture Artifact

**Artifact Path:** `paper/artifacts/phase11/deployment_architecture_diagram.md`  

---

## Cloud Topology Diagram

```mermaid
flowchart TD
    subgraph Client Tier
        User[Supply Chain Manager / Admin]
        Browser[React SPA on Vercel CDN]
    end

    subgraph App Tier (Render Cloud)
        FastAPI[FastAPI Backend - render.yaml]
        LangGraph[LangGraph Multi-Agent Engine]
        GraphRAG[GraphRAG Context Engine]
    end

    subgraph Data Tier (Cloud Managed)
        Postgres[(Supabase PostgreSQL)]
        Neo4j[(Neo4j Aura Graph DB)]
    end

    subgraph External Services
        Gemini[Google Gemini API]
        Weather[Open-Meteo API]
        News[NewsAPI Service]
    end

    User --> Browser
    Browser -->|HTTPS / WSS| FastAPI
    FastAPI --> LangGraph
    FastAPI --> GraphRAG
    FastAPI -->|SQLAlchemy| Postgres
    FastAPI -->|Neo4j Bolt| Neo4j
    LangGraph --> Gemini
    LangGraph --> Weather
    LangGraph --> News
```

---

## Deployment Manifest Summary

- **Backend Host:** Render Web Service (`render.yaml`)
- **Frontend Host:** Vercel Static CDN (`frontend/vercel.json`)
- **Relational Database:** Supabase Cloud PostgreSQL 16
- **Knowledge Graph Database:** Neo4j AuraDB 5.x Cloud
- **LLM Provider:** Google Gemini API (`gemini-2.5-flash`)
