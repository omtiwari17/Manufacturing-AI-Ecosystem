# Manufacturing AI Ecosystem 🏭

A unified manufacturing intelligence platform integrating multimodal GenAI for concept design, Agentic AI for supplier research, and a fully automated DevOps pipeline to AWS EKS.

---

## 🎯 What it does

**Tab 1 — Multimodal GenAI Creator**
Enter a manufacturing concept to instantly generate a structured technical narrative (powered by Groq's lightning-fast Llama 3) alongside an AI-generated visual prototype (powered by Flux via Pollinations.ai). 

**Tab 2 — Agentic Sourcing System**
A two-agent CrewAI pipeline (Researcher + Writer) that takes a sourcing query, finds and scores real-world suppliers, and produces a ranked markdown report alongside a structured JSON artifact.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit |
| **LLM Engine** | Google Gemini 2.5 Flash, Groq Llama 3.3 70B |
| **Image Generation** | Flux (via Pollinations.ai) |
| **Agent Framework** | CrewAI |
| **Containerization** | Docker |
| **Orchestration** | Kubernetes (AWS EKS) |
| **CI/CD** | GitHub Actions |

---

## 📁 Project Structure

```
Manufacturing-AI-Ecosystem/
├── frontend/
│   └── app.py
├── backend/
│   ├── agents.py
│   ├── tasks.py
│   ├── orchestrator.py
│   ├── schemas.py
│   └── storage.py
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
├── .github/
│   └── workflows/
│       └── deploy.yml
├── artifacts/
├── Dockerfile
├── requirements.txt
└── eks-setup.ps1
```

---

## 💻 Running Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/omtiwari17/Manufacturing-AI-Ecosystem.git
   cd Manufacturing-AI-Ecosystem
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the application:**
   ```bash
   python -m streamlit run frontend/app.py
   ```

4. **Add your API Keys:**
   When the UI loads in your browser, enter your keys in the sidebar:
   * **Gemini API Key:** Required for Tab 1 (Get it free at [aistudio.google.com](https://aistudio.google.com))
   * **Groq API Key:** Required for Tab 1 & Tab 2 (Get it free at [console.groq.com](https://console.groq.com))

---

## 🚀 AWS EKS Deployment

This application is configured for fully automated, zero-downtime deployments to Amazon Elastic Kubernetes Service (EKS).

### 1. Provision the Cluster (One-Time Setup)
Ensure you have the AWS CLI installed and configured (`aws configure`). Then, run the provisioning script to build the cluster and configure the necessary IAM roles:
```powershell
.\eks-setup.ps1
```

### 2. Configure GitHub Secrets
Add the following repository secrets in GitHub (`Settings -> Secrets and variables -> Actions`):
* `DOCKER_USERNAME` *(Your Docker Hub username)*
* `DOCKER_PASSWORD` *(Your Docker Hub Personal Access Token)*
* `AWS_ACCESS_KEY_ID` *(From AWS IAM)*
* `AWS_SECRET_ACCESS_KEY` *(From AWS IAM)*
* `AWS_REGION` *(e.g., ap-south-1)*

### 3. Trigger Deployment
Any code pushed to the `main` branch will automatically trigger the GitHub Actions pipeline. The pipeline will build a new Docker image, push it to Docker Hub, and execute a rolling update on the EKS cluster.
```bash
git add .
git commit -m "Deploying unified ecosystem"
git push origin main
```

---

## 👥 Group Members

| Sr No | Name | Enrollment Number |
|---|---|---|
| 01 | Om Tiwari | EN22CS301669 |
| 02 | Paridhi Shirwalkar | EN22CS301684 |
| 03 | Nitesh Chourasiya | EN22CS301660 |
| 04 | Mradul Jain | EN22CS301616 |
