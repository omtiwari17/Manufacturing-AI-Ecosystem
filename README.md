# Manufacturing AI Creator
### Integrated GenAI + Agentic AI + DevOps Ecosystem

A single production-grade app that combines multi-agent AI, multimodal generation, and Kubernetes deployment built as the capstone integration for the Datagami Skill Based Course.

---

## What it does

1. **User describes a manufacturing requirement**
2. **Three CrewAI agents** run sequentially Requirements Analyst → Process Engineer → QA Specialist and produce a structured manufacturing spec
3. **Spec auto-pipes into the Multimodal Creator** Gemini writes a professional narrative, Imagen 3 on Vertex AI generates a product visual
4. **Everything is stored in ChromaDB** for retrieval
5. **The whole app runs on AWS EKS** via a GitHub Actions CI/CD pipeline with zero-downtime rolling updates

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agentic AI | CrewAI, Gemini 1.5 Flash |
| Generative AI | Gemini 1.5 Flash (narrative), Imagen 3 via Vertex AI (image) |
| Vector DB | ChromaDB (embedded) |
| Frontend | Streamlit |
| Containerisation | Docker |
| Orchestration | Kubernetes (AWS EKS, `multi-agent-cluster`, `ap-south-1`) |
| CI/CD | GitHub Actions |
| Image Registry | Docker Hub (`tiwariom/manufacturing-ai-creator`) |

---

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Enter your Gemini API key, GCP Project ID, and (optionally) a Service Account JSON in the sidebar. The app works without the SA JSON image generation will be skipped but everything else runs.

---

## GitHub Secrets required

Add these in **Settings → Secrets → Actions**:

| Secret | Value |
|---|---|
| `DOCKER_USERNAME` | `tiwariom` |
| `DOCKER_PASSWORD` | Docker Hub access token |
| `AWS_ACCESS_KEY_ID` | AWS IAM key |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret |

---

## Repository structure

```
Manufacturing-AI-Ecosystem/
├── app.py                        # Main Streamlit app
├── requirements.txt
├── Dockerfile
├── .streamlit/
│   └── config.toml
├── k8s/
│   ├── deployment.yaml           # K8s Deployment (2 replicas, rolling update)
│   └── service.yaml              # K8s LoadBalancer Service
└── .github/
    └── workflows/
        └── ci-cd.yml             # GitHub Actions CI/CD
```

---

## Group Members

| Sr No | Name | Enrollment Number |
|---|---|---|
| 01 | Om Tiwari | EN22CS301669 |
| 02 | Paridhi Shirwalkar | EN22CS301684 |
| 03 | Nitesh Chourasiya | EN22CS301660 |
| 04 | Mradul Jain | EN22CS301616 |