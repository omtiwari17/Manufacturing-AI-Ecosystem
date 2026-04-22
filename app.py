import streamlit as st
import json, os, time, tempfile

st.set_page_config(
    page_title="Manufacturing AI Creator",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
.stApp { background: #0a0e14; color: #c9d1d9; }

section[data-testid="stSidebar"] {
  background: #0d1117;
  border-right: 1px solid #1f2937;
}

/* Header */
.app-header {
  background: #0d1117;
  border: 1px solid #1f2937;
  border-radius: 12px;
  padding: 26px 32px;
  margin-bottom: 28px;
  position: relative;
  overflow: hidden;
}
.app-header::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, #4f46e5, #00d4aa, #f59e0b);
}
.app-header h1 {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 1.5rem; font-weight: 600;
  color: #e6edf3; margin: 0 0 6px;
}
.app-header p { font-size: 0.85rem; color: #8b949e; margin: 0; }

/* Inputs */
.stTextInput input, .stTextArea textarea {
  background: #161b22 !important;
  border: 1px solid #30363d !important;
  color: #e6edf3 !important;
  font-family: 'IBM Plex Mono', monospace !important;
  font-size: 0.85rem !important;
  border-radius: 6px !important;
}
.stTextInput label, .stTextArea label, .stFileUploader label,
.stSelectbox label {
  color: #8b949e !important;
  font-size: 0.75rem !important;
  font-family: 'IBM Plex Mono', monospace !important;
  letter-spacing: 1px; text-transform: uppercase;
}

/* Section labels */
.sec-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.65rem; color: #4b5563;
  letter-spacing: 3px; text-transform: uppercase;
  margin: 24px 0 12px;
}

/* Step cards */
.step-card {
  background: #0d1117;
  border: 1px solid #1f2937;
  border-radius: 10px;
  padding: 20px 24px 16px 28px;
  margin-bottom: 18px;
  position: relative;
  overflow: hidden;
}
.step-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; bottom: 0; width: 3px;
}
.sc-purple::before { background: #4f46e5; }
.sc-teal::before   { background: #00d4aa; }

.step-card .sc-tag {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.62rem; color: #6b7280;
  letter-spacing: 2.5px; text-transform: uppercase;
  margin-bottom: 4px;
}
.step-card h3 {
  font-size: 1rem; font-weight: 600;
  color: #e6edf3; margin: 0 0 4px;
}
.step-card p { font-size: 0.82rem; color: #8b949e; margin: 0; }

/* Tags */
.tag {
  display: inline-block;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.68rem; padding: 2px 9px;
  border-radius: 4px; margin: 3px 3px 0 0;
  border: 1px solid;
}
.tp { color: #818cf8; border-color: #312e81; background: #1e1b4b; }
.tt { color: #34d399; border-color: #064e3b; background: #022c22; }

/* Agent log */
.agent-log {
  background: #060a0f;
  border: 1px solid #1f2937;
  border-radius: 6px;
  padding: 14px 16px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.78rem; color: #34d399;
  max-height: 220px; overflow-y: auto;
  white-space: pre-wrap; line-height: 1.7;
}

/* Spec block */
.spec-block {
  background: #060a0f;
  border: 1px solid #1f2937;
  border-radius: 6px;
  padding: 16px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.8rem; color: #c9d1d9;
  line-height: 1.7; white-space: pre-wrap;
  max-height: 320px; overflow-y: auto;
}

/* Narrative */
.narrative-block {
  background: #060a0f;
  border: 1px solid #1f2937;
  border-radius: 6px;
  padding: 20px;
  font-size: 0.9rem; color: #c9d1d9;
  line-height: 1.85;
}
</style>
""", unsafe_allow_html=True)

# ── Session state init ─────────────────────────────────────────────────────────
for k, v in {
    "cfg_saved": False,
    "gemini_key": "",
    "gcp_project": "",
    "gcp_region": "asia-south1",
    "sa_json": None,
    "last_result": None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar: API Config ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.62rem;
         color:#4b5563;letter-spacing:3px;text-transform:uppercase;
         padding-bottom:12px;border-bottom:1px solid #1f2937;margin-bottom:18px;">
      API Configuration
    </div>
    """, unsafe_allow_html=True)

    gemini_key  = st.text_input("Gemini API Key", type="password",
                                value=st.session_state.gemini_key,
                                placeholder="AIzaSy...")
    gcp_project = st.text_input("GCP Project ID",
                                value=st.session_state.gcp_project,
                                placeholder="my-project-123")
    gcp_region  = st.selectbox("GCP Region",
                               ["asia-south1", "us-central1", "us-east1", "europe-west1"],
                               index=["asia-south1","us-central1","us-east1","europe-west1"]
                               .index(st.session_state.gcp_region))
    sa_file     = st.file_uploader("Service Account JSON", type=["json"])

    if st.button("Save Config", type="primary", use_container_width=True):
        if gemini_key and gcp_project:
            st.session_state.gemini_key  = gemini_key
            st.session_state.gcp_project = gcp_project
            st.session_state.gcp_region  = gcp_region
            if sa_file:
                st.session_state.sa_json = json.loads(sa_file.read())
            st.session_state.cfg_saved = True
            st.success("Config saved ✓")
        else:
            st.error("Gemini key + GCP Project ID required.")

    if st.session_state.cfg_saved:
        st.markdown("""
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.72rem;
             color:#34d399;margin-top:12px;line-height:1.9;">
          ✓ Gemini API<br>✓ Vertex AI (GCP)<br>✓ ChromaDB embedded
        </div>
        """, unsafe_allow_html=True)
        if not st.session_state.sa_json:
            st.info("Upload Service Account JSON to enable Imagen image generation.")

    st.markdown("<br>" * 4, unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.62rem;
         color:#374151;line-height:1.8;border-top:1px solid #1f2937;padding-top:12px;">
      Group 01D6 · Datagami SBC<br>
      Om · Paridhi · Nitesh · Mradul<br>
      Mentor: Prof. Akshay Saxena
    </div>
    """, unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <h1>⚙️ Manufacturing AI Creator</h1>
  <p>Describe a manufacturing requirement — AI agents generate a full spec,
     then produce a written narrative and product visual automatically.</p>
</div>
""", unsafe_allow_html=True)

# ── Input ──────────────────────────────────────────────────────────────────────
st.markdown('<p class="sec-label">// Your requirement</p>', unsafe_allow_html=True)

col_inp, col_ex = st.columns([3, 1])
with col_inp:
    requirement = st.text_area(
        "Requirement",
        placeholder="e.g. Design a production process for 10,000 units/month of aluminium automotive brake brackets with ±0.05mm tolerance and ISO 9001 compliance...",
        height=130,
        label_visibility="collapsed",
    )

with col_ex:
    st.markdown("""
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;
         color:#6b7280;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">
      Try an example
    </div>""", unsafe_allow_html=True)
    examples = [
        "Aluminium brake brackets, 10k/month, ±0.05mm, ISO 9001",
        "Injection-moulded plastic electronics enclosures",
        "Steel gear assemblies for industrial gearboxes",
    ]
    for ex in examples:
        if st.button(ex, key=f"ex_{ex[:15]}", use_container_width=True):
            st.session_state["_prefill"] = ex
            st.rerun()

if "_prefill" in st.session_state:
    requirement = st.session_state.pop("_prefill")

if not st.session_state.cfg_saved:
    st.warning("Configure your API keys in the sidebar first.")
    st.stop()

run = st.button("⚡ Generate Spec + Narrative + Image",
                type="primary", use_container_width=True,
                disabled=not requirement.strip())

# ── Show cached result if not re-running ───────────────────────────────────────
if not run:
    if st.session_state.last_result:
        _show_results(st.session_state.last_result)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")

# ── STEP 1: Multi-Agent ────────────────────────────────────────────────────────
st.markdown("""
<div class="step-card sc-purple">
  <div class="sc-tag">// Step 01 · Agentic AI</div>
  <h3>Multi-Agent Manufacturing Spec</h3>
  <p>Three CrewAI agents running sequentially — Analyst → Process Engineer → QA Specialist</p>
  <div style="margin-top:10px;">
    <span class="tag tp">CrewAI</span>
    <span class="tag tp">Gemini 1.5 Flash</span>
    <span class="tag tp">3 Agents · Sequential</span>
  </div>
</div>
""", unsafe_allow_html=True)

log_ph = st.empty()


def _log(msg):
    log_ph.markdown(f'<div class="agent-log">{msg}</div>', unsafe_allow_html=True)


_log("→ Initialising agents...")

# ── Agent execution ────────────────────────────────────────────────────────────
import google.generativeai as genai

spec = ""
try:
    from crewai import Agent, Task, Crew, Process

    # CrewAI 0.28+ uses LiteLLM under the hood — pass model as a string,
    # set the API key via environment variable before Agent instantiation.
    os.environ["GEMINI_API_KEY"] = st.session_state.gemini_key
    llm = "gemini/gemini-2.5-flash"

    analyst = Agent(
        role="Manufacturing Requirements Analyst",
        goal="Extract key parameters, constraints, and objectives from the manufacturing requirement.",
        backstory="Expert in manufacturing systems with deep knowledge of production processes and quality standards.",
        llm=llm, verbose=False,
    )
    process_eng = Agent(
        role="Process Design Engineer",
        goal="Design a detailed manufacturing process plan based on the analysis.",
        backstory="Specialist in designing efficient manufacturing workflows, selecting machinery, and optimising sequences.",
        llm=llm, verbose=False,
    )
    qa_agent = Agent(
        role="Quality Assurance Specialist",
        goal="Define quality control checkpoints and acceptance criteria.",
        backstory="Expert in quality management, ISO standards, and statistical process control.",
        llm=llm, verbose=False,
    )

    t1 = Task(
        description=f"Analyse this requirement and extract product type, materials, volume, constraints, success criteria.\n\nRequirement: {requirement}",
        agent=analyst,
        expected_output="Structured analysis: product details, materials, volume, constraints, success criteria.",
    )
    t2 = Task(
        description="Design a step-by-step process plan: stages, equipment, time estimates, resources.",
        agent=process_eng,
        expected_output="Detailed process plan with stages, equipment, timelines, resources.",
        context=[t1],
    )
    t3 = Task(
        description="Define QC checkpoints: inspection criteria, testing methods, acceptance standards.",
        agent=qa_agent,
        expected_output="Quality control plan with checkpoints, criteria, testing methods, pass/fail standards.",
        context=[t1, t2],
    )

    _log(
        "→ Agent 1: Manufacturing Requirements Analyst ... running\n"
        "→ Agent 2: Process Design Engineer ... waiting\n"
        "→ Agent 3: QA Specialist ... waiting"
    )

    crew = Crew(
        agents=[analyst, process_eng, qa_agent],
        tasks=[t1, t2, t3],
        process=Process.sequential,
        verbose=False,
    )
    result = crew.kickoff()
    spec = str(result)

    _log(
        "✓ Agent 1: Requirements analysis complete\n"
        "✓ Agent 2: Process plan complete\n"
        "✓ Agent 3: QA plan complete\n"
        "→ Spec ready — passing to Multimodal Creator"
    )

except ImportError:
    _log("⚠ crewai not installed — using Gemini direct fallback\n→ Generating spec...")
    genai.configure(api_key=st.session_state.gemini_key)
    m = genai.GenerativeModel("gemini-2.5-flash")
    resp = m.generate_content(
        f"""You are a manufacturing expert. Generate a detailed spec with:
1. Requirements Analysis (product, materials, volume, constraints)
2. Process Plan (stages, equipment, timelines)
3. Quality Control Plan (checkpoints, criteria, standards)

Requirement: {requirement}"""
    )
    spec = resp.text
    _log("✓ Spec generated\n→ Passing to Multimodal Creator")

# ── STEP 2: Multimodal Creator ─────────────────────────────────────────────────
st.markdown("""
<div class="step-card sc-teal">
  <div class="sc-tag">// Step 02 · Generative AI</div>
  <h3>Multimodal Creator</h3>
  <p>Generating product narrative via Gemini and product visual via Imagen on Vertex AI</p>
  <div style="margin-top:10px;">
    <span class="tag tt">Gemini 2.5 Flash</span>
    <span class="tag tt">Imagen 3 · Vertex AI</span>
    <span class="tag tt">ChromaDB</span>
  </div>
</div>
""", unsafe_allow_html=True)

with st.spinner("Generating narrative..."):
    genai.configure(api_key=st.session_state.gemini_key)
    narr_model = genai.GenerativeModel("gemini-2.5-flash")
    narr_resp = narr_model.generate_content(
        f"""You are a technical writer for a manufacturing company.
Based on this manufacturing specification, write a compelling 3-paragraph overview:
- Paragraph 1: What is being manufactured and why it matters
- Paragraph 2: How it is manufactured (key process steps, quality highlights)
- Paragraph 3: Expected outcome, quality standards, and business value

Use flowing professional prose. No bullet points.

Specification:
{spec}"""
    )
    narrative = narr_resp.text

# ── Imagen image generation ────────────────────────────────────────────────────
image_bytes = None
image_error = None

if st.session_state.sa_json and st.session_state.gcp_project:
    with st.spinner("Generating product image via Imagen..."):
        try:
            import vertexai
            from vertexai.preview.vision_models import ImageGenerationModel
            from google.oauth2 import service_account

            # Write SA JSON to temp file
            sa_tmp = tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            )
            json.dump(st.session_state.sa_json, sa_tmp)
            sa_tmp.flush()
            sa_tmp.close()

            creds = service_account.Credentials.from_service_account_file(
                sa_tmp.name,
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
            os.unlink(sa_tmp.name)

            vertexai.init(
                project=st.session_state.gcp_project,
                location=st.session_state.gcp_region,
                credentials=creds,
            )

            # Build a focused image prompt from the spec
            prompt_model = genai.GenerativeModel("gemini-2.5-flash")
            img_prompt_resp = prompt_model.generate_content(
                f"In one sentence (max 25 words), describe a photorealistic studio product image for this manufacturing item: {spec[:600]}"
            )
            image_prompt = (
                "Photorealistic studio product photography, clean white background, "
                "professional industrial manufacturing: "
                + img_prompt_resp.text.strip()
            )

            imagen = ImageGenerationModel.from_pretrained("imagegeneration@006")
            images = imagen.generate_images(
                prompt=image_prompt,
                number_of_images=1,
                aspect_ratio="1:1",
                safety_filter_level="block_few",
                person_generation="dont_allow",
            )
            image_bytes = images[0]._image_bytes

        except Exception as e:
            image_error = str(e)
else:
    image_error = "Upload Service Account JSON + GCP Project ID in the sidebar to enable image generation."

# ── ChromaDB store ─────────────────────────────────────────────────────────────
doc_id = None
try:
    import chromadb
    from chromadb.utils import embedding_functions

    client = chromadb.PersistentClient(path="./chroma_store")
    ef = embedding_functions.DefaultEmbeddingFunction()
    col = client.get_or_create_collection("manufacturing_specs", embedding_function=ef)
    doc_id = f"spec_{int(time.time())}"
    col.add(
        documents=[f"REQUIREMENT:\n{requirement}\n\nSPEC:\n{spec}\n\nNARRATIVE:\n{narrative}"],
        metadatas=[{"requirement": requirement[:200], "ts": str(int(time.time()))}],
        ids=[doc_id],
    )
except Exception:
    pass

# ── Cache and rerun to render cleanly ─────────────────────────────────────────
st.session_state.last_result = dict(
    requirement=requirement,
    spec=spec,
    narrative=narrative,
    image_bytes=image_bytes,
    image_error=image_error,
    doc_id=doc_id,
)
st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# RESULTS RENDERER
# ══════════════════════════════════════════════════════════════════════════════
def _show_results(r):
    st.markdown("---")

    # ── Spec ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="step-card sc-purple">
      <div class="sc-tag">// Step 01 Complete · Agentic AI</div>
      <h3>Manufacturing Specification</h3>
      <div style="margin-top:8px;">
        <span class="tag tp">CrewAI Agents</span>
        <span class="tag tp">Gemini 1.5 Flash</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    with st.expander("View full agent-generated spec"):
        st.markdown(f'<div class="spec-block">{r["spec"]}</div>', unsafe_allow_html=True)

    # ── Narrative + Image ──────────────────────────────────────────────────
    st.markdown("""
    <div class="step-card sc-teal">
      <div class="sc-tag">// Step 02 Complete · Generative AI</div>
      <h3>Narrative + Product Visual</h3>
      <div style="margin-top:8px;">
        <span class="tag tt">Gemini Narrative</span>
        <span class="tag tt">Imagen 3 · Vertex AI</span>
        <span class="tag tt">ChromaDB</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if r["image_bytes"]:
        col_img, col_narr = st.columns([1, 2])
        with col_img:
            st.image(r["image_bytes"], caption="Generated by Imagen 3 · Vertex AI",
                     use_column_width=True)
        with col_narr:
            st.markdown(f'<div class="narrative-block">{r["narrative"]}</div>',
                        unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="narrative-block">{r["narrative"]}</div>',
                    unsafe_allow_html=True)
        if r["image_error"]:
            st.info(f"ℹ Image generation: {r['image_error']}")

    if r["doc_id"]:
        st.markdown(
            f'<p style="font-family:\'IBM Plex Mono\',monospace;font-size:0.7rem;'
            f'color:#4b5563;margin-top:6px;">✓ Stored in ChromaDB · {r["doc_id"]}</p>',
            unsafe_allow_html=True,
        )

    # ── Downloads ──────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, _ = st.columns([1, 1, 3])
    with c1:
        st.download_button("⬇ Download Spec", data=r["spec"],
                           file_name="manufacturing_spec.txt",
                           mime="text/plain", use_container_width=True)
    with c2:
        st.download_button("⬇ Download Narrative", data=r["narrative"],
                           file_name="manufacturing_narrative.txt",
                           mime="text/plain", use_container_width=True)