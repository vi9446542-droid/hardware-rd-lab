import streamlit as st
from google import genai
from pypdf import PdfReader
import schemdraw
import schemdraw.elements as elm
import matplotlib.pyplot as plt
import io
import re
import time

# పేజీ సెటప్
st.set_page_config(page_title="Autonomous Hardware R&D Platform", page_icon="🔬", layout="wide")

st.title("🔬 Autonomous Hardware R&D Multi-Agent Platform")
st.markdown("**ఒక్క ప్రాంప్ట్ తో: A to Z ఐడియా ➡️ కాంపోనెంట్లు (BOM) ➡️ Visual Schematic బొమ్మ ➡️ Breadboard వైరింగ్ ➡️ ESP32 C++ కోడ్**")

# సైడ్‌బార్: API Key & ఆప్షనల్ PDF Datasheet
with st.sidebar:
    st.header("🔑 1. API Configuration")
    api_key = st.text_input("మీ Gemini API Key ఎంటర్ చేయండి:", type="password").strip()
    
    st.divider()
    st.header("📄 2. Optional Datasheet (100% Accuracy)")
    uploaded_pdf = st.file_uploader("అధికారిక PDF Datasheet ఉంటే అప్‌లోడ్ చేయండి:", type=["pdf"])
    pdf_context = ""
    if uploaded_pdf:
        reader = PdfReader(uploaded_pdf)
        for i, page in enumerate(reader.pages):
            txt = page.extract_text()
            if txt:
                pdf_context += f"\n[Page {i+1}]\n" + txt
        st.success(f"✅ {uploaded_pdf.name} లోడ్ అయింది!")

    st.divider()
    st.header("⚙️ 3. Hardware Constraints")
    mcu_choice = st.selectbox("Microcontroller:", ["ESP32-C3 (3.3V, 12-bit ADC)", "ESP32 DevKit V1 (3.3V, 12-bit ADC)", "RP2040 / Pico (3.3V, 12-bit ADC)"])
    budget_limit = st.text_input("Target BOM Budget:", value="Under ₹500 (Discrete Op-Amps like MCP6002 / LM358)")

# మెయిన్ ఇన్‌పుట్
project_prompt = st.text_area(
    "మీ హార్డ్‌వేర్ R&D ప్రాజెక్ట్ ఐడియాను రాయండి:",
    value="Design a low-cost discrete PPG heart rate sensor circuit using BPW34 photodiode, 525nm green LED, MCP6002 op-amp (Gain 100, 0.5Hz to 40Hz bandpass filter, 1.65V mid-rail bias) for ESP32-C3.",
    height=100
)

# Helper Function: Auto-Discover Working Models & Handle 503 High Demand
def ask_gemini_smart(client, prompt):
    # ముందుగా gemini-3.8-flash మరియు అందుబాటులో ఉన్న ఇతర flash/lite మోడల్స్ లిస్ట్ తీసుకుంటుంది
    models_to_try = ["gemini-3.8-flash"]
    try:
        for m in client.models.list():
            m_name = m.name.replace("models/", "")
            if ("flash" in m_name or "lite" in m_name) and m_name not in models_to_try:
                models_to_try.append(m_name)
    except Exception:
        pass

    last_error = ""
    for model_name in models_to_try:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                return response.text, model_name
            except Exception as e:
                last_error = str(e)
                if "503" in last_error or "UNAVAILABLE" in last_error or "429" in last_error:
                    time.sleep(4) # 4 సెకన్లు ఆగి మళ్ళీ ప్రయత్నిస్తుంది
                    continue
                else:
                    break # 404 లేదా ఇతర ఎర్రర్ అయితే వెంటనే తర్వాతి మోడల్ కి వెళ్తుంది

    st.error(f"⚠️ ప్రస్తుతం Google సర్వర్లు చాలా బిజీగా ఉన్నాయి (503 High Demand). దయచేసి 1-2 నిమిషాల తర్వాత మళ్ళీ 'Run' నొక్కండి.\n\nవివరాలు: {last_error}")
    st.stop()

# Helper Function: Python Code Extractor
def extract_python_code(text):
    match = re.search(r"```python\n(.*?)\n```", text, re.DOTALL)
    if match:
        return match.group(1)
    return None

# బటన్ క్లిక్ చేసినప్పుడు కేవలం 2 ఫాస్ట్ API కాల్స్ తో మొత్తం 5 ట్యాబ్‌లు నిండుతాయి
if st.button("🚀 Run Complete A to Z R&D Pipeline", type="primary"):
    if not api_key:
        st.error("⚠️ దయచేసి ఎడమవైపు సైడ్‌బార్‌లో మీ Gemini API Key ఇవ్వండి.")
    elif not project_prompt.strip():
        st.warning("⚠️ దయచేసి మీ ప్రాజెక్ట్ ఐడియా టైప్ చేయండి.")
    else:
        client = genai.Client(api_key=api_key)
        ds_info = f"\nUse ONLY verified specs from this Datasheet context:\n{pdf_context[:35000]}" if pdf_context else ""

        with st.spinner("⚡ R&D ఇంజనీరింగ్ రిపోర్ట్, BOM, వైరింగ్ & C++ కోడ్ తయారవుతున్నాయి (ఒకే కాల్ లో వేగంగా)..."):
            master_prompt = f"""
            You are a Senior Biomedical Hardware R&D Engineer.
            Project: {project_prompt}
            Constraints: {mcu_choice}, {budget_limit}. {ds_info}

            Provide a complete, practical R&D output divided strictly into 4 clearly separated sections using these exact markers:
            ===SECTION_1===
            (Write A to Z R&D Architecture in Telugu with technical terms in English: 1. Core Physics, 2. Noise Challenges like 50Hz hum & saturation, 3. Signal Chain Block Diagram, 4. Exact Engineering Math Calculations for Gain, Cut-off frequency, Mid-rail bias.)

            ===SECTION_2===
            (Write Detailed Bill of Materials BOM Table in Telugu/English: Component Name, Exact Part/Value, Quantity, Role, Approx Indian Price in ₹, plus exact IC Pinout table for VDD, GND, IN+, IN-, OUT.)

            ===SECTION_3===
            (Write Step-by-Step Breadboard Wiring Guide in Telugu with exact pin numbers, Multimeter Verification Checklist before connecting ESP32, and a ready-to-run LTspice SPICE Netlist code block.)

            ===SECTION_4===
            (Write complete, non-blocking Arduino C++ code using micros() for {mcu_choice} that converts 12-bit ADC to mV, subtracts 1650mV bias, applies a digital IIR/Moving Average filter, and prints for Serial Plotter. Add a brief Telugu explanation after the code.)
            """
            full_report, used_model = ask_gemini_smart(client, master_prompt)
            st.toast(f"✅ {used_model} ద్వారా రిపోర్ట్ సిద్ధమైంది!")

        # విభాగాలను వేరు చేయడం
        sec1 = full_report.split("===SECTION_2===")[0].replace("===SECTION_1===", "").strip() if "===SECTION_2===" in full_report else full_report
        sec2 = full_report.split("===SECTION_2===")[1].split("===SECTION_3===")[0].strip() if "===SECTION_3===" in full_report else "BOM వివరాలు Section 1 లో చూడండి."
        sec3 = full_report.split("===SECTION_3===")[1].split("===SECTION_4===")[0].strip() if "===SECTION_4===" in full_report else "Wiring వివరాలు Section 1 లో చూడండి."
        sec4 = full_report.split("===SECTION_4===")[1].strip() if "===SECTION_4===" in full_report else "C++ కోడ్ కోసం మళ్ళీ ప్రయత్నించండి."

        # 5 ట్యాబ్‌లు
        t1, t2, t3, t4, t5 = st.tabs([
            "1️⃣ A to Z R&D ఐడియా",
            "2️⃣ కాంపోనెంట్లు (BOM) & విలువలు",
            "3️⃣ Visual Circuit Schematic (బొమ్మ)",
            "4️⃣ Breadboard వైరింగ్ & టెస్ట్",
            "5️⃣ ESP32 C++ & DSP కోడ్"
        ])

        with t1:
            st.markdown(sec1)
        with t2:
            st.markdown(sec2)
        with t4:
            st.markdown(sec3)
        with t5:
            st.markdown(sec4)

        # --- CALL 2: Visual Circuit Schematic Diagram (schemdraw) ---
        with t3:
            with st.spinner("🎨 Python schemdraw ద్వారా అసలైన Circuit Schematic బొమ్మ గీస్తోంది..."):
                p_sch = f"""
                Write ONLY valid Python code using `schemdraw` (version 0.18+) to draw a clean electronic circuit schematic for:
                {project_prompt}
                
                STRICT RULES:
                1. Import `schemdraw` and `schemdraw.elements as elm`.
                2. `d = schemdraw.Drawing(show=False)`
                3. Label components clearly (e.g., `.label('10kΩ')`, `.label('100nF')`, `.label('MCP6002')`, `.label('3.3V')`, `.label('Vout -> ESP32')`).
                4. Do NOT call `d.draw()` or `plt.show()`. Save to `buf` at the end:
                   ```python
                   buf = io.BytesIO()
                   d.save(buf, format='png', dpi=300)
                   buf.seek(0)
                   ```
                5. Output ONLY the ```python ... ``` code block.
                """
                res_sch, _ = ask_gemini_smart(client, p_sch)
                py_code = extract_python_code(res_sch)
                
                if py_code:
                    try:
                        local_env = {"schemdraw": schemdraw, "elm": elm, "plt": plt, "io": io}
                        exec(py_code, local_env)
                        if "buf" in local_env:
                            st.image(local_env["buf"], caption="Generated Circuit Schematic Diagram (Verify Pinouts with Datasheet)", use_container_width=True)
                            st.download_button("⬇️ Schematic బొమ్మను డౌన్‌లోడ్ చేయండి (PNG)", data=local_env["buf"], file_name="circuit_schematic.png", mime="image/png")
                        else:
                            st.warning("Schematic బొమ్మ జనరేట్ కాలేదు.")
                    except Exception as err:
                        st.error(f"Schematic గీయడంలో చిన్న సింటాక్స్ ఎర్రర్: {err}")
                        st.code(py_code, language="python")
