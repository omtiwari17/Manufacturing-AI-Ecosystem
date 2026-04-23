import os
import logging

# Fix CrewAI signal/telemetry error in Streamlit threads
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"

# Suppress litellm fastapi warning
logging.getLogger("LiteLLM").setLevel(logging.CRITICAL)

import streamlit as st
import google.generativeai as genai
from urllib.parse import quote
import requests
from PIL import Image
from io import BytesIO
import json
import sys

# Path Fix
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.agents import build_researcher, build_writer
from backend.tasks import research_task, write_task
from backend.orchestrator import Orchestrator

st.set_page_config(page_title="Manufacturing Hub", page_icon="🏭", layout="wide")
st.title("Unified Manufacturing System")

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    gemini_key = st.text_input("Gemini API Key (Tab 1)", type="password")
    groq_key = st.text_input("Groq API Key (Tab 2)", type="password", help="Free from console.groq.com")
    st.markdown("---")
    st.markdown("**Visual Style**")
    style = st.selectbox("Image style", [
        "Technical blueprint, engineering diagram",
        "Photorealistic industrial photography",
        "3D render, product prototype",
        "Schematic exploded view, labelled parts"
    ])

if not gemini_key.strip() and not groq_key.strip():
    st.info("👈 Enter your API keys in the sidebar to get started.")

tab1, tab2 = st.tabs(["🎨 Multimodal GenAI Creator", "🤖 Agentic Sourcing System"])

# ==========================================
# TAB 1
# ==========================================
with tab1:
    st.markdown("### Concept to Prototype")
    st.caption("Enter a manufacturing concept → technical narrative + visual prototype")

    examples = [
        "CNC milling machine for aerospace precision parts",
        "Robotic welding arm for automotive assembly line",
        "Injection molding press for plastic enclosures",
        "Conveyor belt sorting system with vision sensors"
    ]

    col_input, col_example = st.columns([3, 1])
    with col_input:
        concept = st.text_input("concept", placeholder="e.g. Robotic welding arm for automotive assembly", label_visibility="collapsed")
    with col_example:
        selected = st.selectbox("Or pick an example", ["— select —"] + examples, label_visibility="collapsed")
        if selected != "— select —":
            concept = selected

    api_choice = st.radio(
        "Choose AI Model:",
        ["Gemini", "Groq (free)"],
        index=1 if not gemini_key.strip() else 0,
        horizontal=True
    )

    generate_clicked = st.button("Generate Concept", type="primary", key="gen_btn")

    if generate_clicked:
        use_gemini = api_choice == "Gemini"

        if use_gemini and not gemini_key.strip():
            st.error("Please enter a Gemini API Key in the sidebar.")
        elif not use_gemini and not groq_key.strip():
            st.error("Please enter a Groq API Key in the sidebar.")
        elif not concept:
            st.warning("Please enter a concept.")
        else:
            # Generate narrative first
            narrative_text = None
            with st.spinner("Generating narrative..."):
                try:
                    if use_gemini:
                        genai.configure(api_key=gemini_key)
                        model_gemini = genai.GenerativeModel("gemini-2.5-flash")
                        prompt = f"""You are a senior manufacturing engineer and technical writer.
For the manufacturing concept: "{concept}"
Write a structured technical description with these exact sections:
1. **Overview** — What it is and its primary purpose (2-3 sentences)
2. **Working Principle** — How it operates step by step (3-4 sentences)
3. **Key Components** — List 4-5 main components with one-line descriptions
4. **Manufacturing Application** — Industry use cases (2-3 sentences)
5. **Advantages** — 3 key benefits in bullet points
Keep it professional, concise, and educational. Total: ~200 words."""
                        response = model_gemini.generate_content(prompt)
                        narrative_text = response.text
                    else:
                        from groq import Groq
                        client = Groq(api_key=groq_key)
                        prompt = f"""You are a senior manufacturing engineer and technical writer.
For the manufacturing concept: "{concept}"
Write a structured technical description with these exact sections:
1. **Overview** — What it is and its primary purpose (2-3 sentences)
2. **Working Principle** — How it operates step by step (3-4 sentences)
3. **Key Components** — List 4-5 main components with one-line descriptions
4. **Manufacturing Application** — Industry use cases (2-3 sentences)
5. **Advantages** — 3 key benefits in bullet points
Keep it professional, concise, and educational. Total: ~200 words."""
                        chat_completion = client.chat.completions.create(
                            messages=[{"role": "user", "content": prompt}],
                            model="llama-3.3-70b-versatile",
                            temperature=0.7,
                            max_tokens=1000,
                        )
                        narrative_text = chat_completion.choices[0].message.content
                except Exception as e:
                    st.error(f"Narrative Error: {e}")

            # Generate image
            image_bytes = None
            with st.spinner("Generating image..."):
                try:
                    img_prompt = f"{concept}, {style}, manufacturing, industrial, high detail, professional technical illustration, white background"
                    encoded = quote(img_prompt)
                    img_url = f"https://image.pollinations.ai/prompt/{encoded}?width=800&height=600&model=flux&nologo=true&seed=42"
                    resp = requests.get(img_url, timeout=60)
                    image_bytes = resp.content
                except Exception as e:
                    st.error(f"Image Error: {e}")

            # Save everything to session state together
            if narrative_text:
                st.session_state["tab1_narrative"] = narrative_text
                st.session_state["tab1_model"] = "Gemini" if use_gemini else "Groq Llama 3"
            if image_bytes:
                st.session_state["tab1_image_bytes"] = image_bytes
            if narrative_text or image_bytes:
                st.session_state["tab1_concept_label"] = concept
                st.session_state["last_concept"] = concept

    # Always render saved output — persists across tab switches
    if st.session_state.get("tab1_narrative") or st.session_state.get("tab1_image_bytes"):
        label = st.session_state.get("tab1_concept_label", "")
        model = st.session_state.get("tab1_model", "")
        st.markdown(f"---\n*Generated for: **{label}** — Model: {model}*")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📝 Technical Narrative")
            if st.session_state.get("tab1_narrative"):
                st.markdown(st.session_state["tab1_narrative"])
                st.success(f"✅ Generated by {model}")
        with col2:
            st.subheader("🖼️ Visual Prototype")
            if st.session_state.get("tab1_image_bytes"):
                img = Image.open(BytesIO(st.session_state["tab1_image_bytes"]))
                st.image(img, use_container_width=True)
                st.success("✅ Generated by Flux")

    if st.session_state.get("last_concept"):
        st.info(f"💡 Switch to **Tab 2** to find suppliers for: *{st.session_state['last_concept']}*")

# ==========================================
# TAB 2
# ==========================================
with tab2:
    st.markdown("### Multi-Agent Supplier Research")
    st.caption("Enter sourcing requirements → Agents research and rank suppliers")

    prefill = st.session_state.get("last_concept", "")
    if prefill:
        st.success(f"✅ Pre-filled from Tab 1: *{prefill}*")

    sourcing_query = st.text_area(
        "Sourcing Requirements",
        value=prefill,
        placeholder="e.g. ISO 9001 certified CNC machining suppliers in Taiwan that handle aerospace grade aluminum..."
    )

    if st.button("Run Research", type="primary", key="research_btn"):
        if not groq_key.strip():
            st.error("Please enter a Groq API Key in the sidebar.")
        elif not sourcing_query:
            st.warning("Please enter your sourcing requirements.")
        else:
            with st.spinner("Agents are researching and writing the report... (may take 1-2 mins)"):
                try:
                    os.environ["GROQ_API_KEY"] = groq_key

                    groq_model = "groq/llama-3.3-70b-versatile"
                    researcher = build_researcher(api_key=groq_key, model=groq_model)
                    writer = build_writer(api_key=groq_key, model=groq_model)

                    r_task = research_task(researcher)
                    w_task = write_task(writer)

                    orchestrator = Orchestrator(researcher, writer, r_task, w_task)
                    result = orchestrator.run({"query": sourcing_query})

                    with open(result['report_path'], "r", encoding="utf-8") as f:
                        report_md = f.read()
                    with open(result['final_suppliers_path'], "r", encoding="utf-8") as f:
                        final_data = json.load(f)

                    # Save to session state so it persists across tab switches
                    st.session_state["tab2_report"] = report_md
                    st.session_state["tab2_json"] = final_data
                    st.session_state["tab2_run_id"] = result['run_id']

                except Exception as e:
                    st.error(f"Agent Pipeline Error: {e}")
                    st.exception(e)

    # Always render saved Tab 2 output
    if st.session_state.get("tab2_report"):
        st.success(f"✅ Research Complete! Run ID: {st.session_state.get('tab2_run_id', '')}")
        st.markdown("### Output Report")
        st.markdown(st.session_state["tab2_report"])
        with st.expander("View Raw JSON Data"):
            st.json(st.session_state["tab2_json"])