import streamlit as st
from google import genai
from pypdf import PdfReader
import schemdraw
import schemdraw.elements as elm
import matplotlib.pyplot as plt
import io
import re

# పేజీ సెటప్
st.set_page_config(page_title="Autonomous Hardware R&D Platform", page_icon="🔬", layout="wide")

st.title("🔬 Autonomous Hardware R&D Multi-Agent Platform")
st.markdown("**ఒక్క ప్రాంప్ట్ తో: A to Z ఐడియా ➡️ కాంపోనెంట్లు (BOM) ➡️ Visual Schematic బొమ్మ ➡️ Breadboard వైరింగ్ ➡️ ESP32 C++ కోడ్**")

# సైడ్‌బార్: API Key & ఆప్షనల్ PDF Datasheet
with st.sidebar:
    st.header("🔑 1. API Configuration")
    api_key = st.text_input("మీ Gemini API Key ఎంటర్ చేయండి:", type="password")
    
    st.divider()
    st.header("📄 2. Optional Datasheet (100% Accuracy)")
    uploaded_pdf = st.file_uploader("అధికారిక PDF Datasheet ఉంటే అప్‌లోడ్ చేయండి (ఉదా: MCP6002.pdf):", type=["pdf"])
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

# Helper Function: Gemini Call
def ask_gemini(client, prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

# Helper Function: Python Code Extractor
def extract_python_code(text):
    match = re.search(r"```python\n(.*?)\n```", text, re.DOTALL)
    if match:
        return match.group(1)
    return None

# బటన్ క్లిక్ చేసినప్పుడు 5 ఏజెంట్లు వరుసగా పనిచేస్తాయి
if st.button("🚀 Run Complete A to Z R&D Pipeline", type="primary"):
    if not api_key:
        st.error("⚠️ దయచేసి ఎడమవైపు సైడ్‌బార్‌లో మీ Gemini API Key ఇవ్వండి.")
    elif not project_prompt.strip():
        st.warning("⚠️ దయచేసి మీ ప్రాజెక్ట్ ఐడియా టైప్ చేయండి.")
    else:
        client = genai.Client(api_key=api_key)
        ds_info = f"\nUse ONLY verified specs from this Datasheet context where applicable:\n{pdf_context[:40000]}" if pdf_context else ""

        # ఫలితాలను చూపించడానికి 5 ట్యాబ్‌లు
        t1, t2, t3, t4, t5 = st.tabs([
            "1️⃣ A to Z R&D ఐడియా",
            "2️⃣ కాంపోనెంట్లు (BOM) & విలువలు",
            "3️⃣ Visual Circuit Schematic (బొమ్మ)",
            "4️⃣ Breadboard వైరింగ్ & టెస్ట్",
            "5️⃣ ESP32 C++ & DSP కోడ్"
        ])

        # --- AGENT 1: A to Z R&D Idea & Physics ---
        with t1:
            with st.spinner("Agent 1: A to Z ఇంజనీరింగ్ ఆర్కిటెక్చర్ తయారు చేస్తోంది..."):
                p1 = f"""
                You are a Senior Biomedical Hardware R&D Engineer.
                Project: {project_prompt}
                Constraints: {mcu_choice}, {budget_limit}. {ds_info}
                
                Provide a clear, practical A-to-Z R&D Architecture in Telugu (keep technical terms like Op-Amp, Gain, Hz, mV, ADC in English):
                1. Core Sensing Principle & Physics (ఎలా పనిచేస్తుంది).
                2. Real-world Noise & Failure Challenges (50Hz hum, saturation, motion artifacts).
                3. Stage-by-Stage Signal Chain Block Diagram (Text blocks).
                4. Exact Engineering Math Calculations (Cut-off frequencies, Gain, Mid-rail bias).
                """
                res1 = ask_gemini(client, p1)
                st.markdown(res1)

        # --- AGENT 2: Component Details & BOM ---
        with t2:
            with st.spinner("Agent 2: ఖచ్చితమైన కాంపోనెంట్లు & విలువలు ఎంచుకుంటోంది..."):
                p2 = f"""
                Based on this R&D architecture:
                {res1}
                
                Create a detailed Bill of Materials (BOM) and Component Guide in Telugu (technical terms in English):
                - Markdown Table with: Component Name, Exact Value/Part Number (e.g., MCP6002, 1% Metal Film Resistor, C0G Capacitor), Quantity, Role in Circuit, and Approx Indian Price (₹).
                - Pinout warning for the main IC (exact pin numbers for VDD, VSS/GND, IN+, IN-, OUT).
                """
                res2 = ask_gemini(client, p2)
                st.markdown(res2)

        # --- AGENT 3: Visual Circuit Schematic Diagram (schemdraw) ---
        with t3:
            with st.spinner("Agent 3: Python schemdraw ద్వారా అసలైన Circuit Schematic బొమ్మ గీస్తోంది..."):
                p3 = f"""
                Write ONLY valid Python code using the `schemdraw` library (version 0.18+) to draw a clean, well-labeled electronic circuit schematic for:
                {project_prompt}
                
                STRICT RULES FOR SCHEMDRAW CODE:
                1. Import `schemdraw` and `schemdraw.elements as elm`.
                2. Create a drawing object: `d = schemdraw.Drawing(show=False)`
                3. Use standard elements like `elm.Resistor()`, `elm.Capacitor()`, `elm.Opamp()`, `elm.Ground()`, `elm.SourceV()`, `elm.Diode()`, `elm.LED()`, `elm.Line()`, `elm.Dot()`.
                4. Label every component with its exact value (e.g., `.label('10kΩ')`, `.label('100nF')`, `.label('MCP6002')`, `.label('3.3V')`, `.label('Vout -> ESP32')`).
                5. Do NOT call `d.draw()` or `plt.show()`. At the very end of the script, save the figure to a BytesIO buffer named `buf` like this:
                   ```python
                   buf = io.BytesIO()
                   d.save(buf, format='png', dpi=300)
                   buf.seek(0)
                   ```
                6. Output ONLY the ```python ... ``` code block, nothing else. Keep the geometry clean so wires do not overlap text.
                """
                res3_raw = ask_gemini(client, p3)
                py_code = extract_python_code(res3_raw)
                
                if py_code:
                    try:
                        local_env = {"schemdraw": schemdraw, "elm": elm, "plt": plt, "io": io}
                        exec(py_code, local_env)
                        if "buf" in local_env:
                            st.image(local_env["buf"], caption="Generated Circuit Schematic Diagram (Verify Pinouts with Datasheet)", use_container_width=True)
                            st.download_button("⬇️ Schematic బొమ్మను డౌన్‌లోడ్ చేయండి (PNG)", data=local_env["buf"], file_name="circuit_schematic.png", mime="image/png")
                        else:
                            st.warning("Schematic బొమ్మ జనరేట్ కాలేదు. కింద ఉన్న కోడ్ చూడండి.")
                    except Exception as err:
                        st.error(f"Schematic గీయడంలో చిన్న సింటాక్స్ ఎర్రర్ వచ్చింది: {err}")
                        st.info("మళ్ళీ 'Run' బటన్ నొక్కితే సెట్ అవుతుంది. జనరేట్ అయిన schemdraw కోడ్:")
                        st.code(py_code, language="python")
                else:
                    st.warning("Schematic కోడ్ జనరేట్ కాలేదు.")

        # --- AGENT 4: Breadboard Wiring & LTspice Verification ---
        with t4:
            with st.spinner("Agent 4: పిన్-టు-పిన్ Breadboard వైరింగ్ & LTspice టెస్ట్ కోడ్ సిద్ధం చేస్తోంది..."):
                p4 = f"""
                Based on this circuit design:
                {res2}
                
                Provide in clear Telugu (technical terms in English):
                1. **Step-by-Step Breadboard Wiring Guide:** Exact physical pin connections (e.g., MCP6002 Pin 8 -> 3.3V Rail, Pin 4 -> GND Rail, etc.) so a beginner can wire it without short circuits.
                2. **Hardware Verification Checklist:** What voltage to expect on a multimeter at each stage (e.g., 1.65V at bias node) before connecting ESP32.
                3. **LTspice Verification Netlist:** A ready-to-run SPICE netlist code block to test frequency response in LTspice.
                """
                res4 = ask_gemini(client, p4)
                st.markdown(res4)

        # --- AGENT 5: ESP32 C++ Firmware & Serial Plotter Code ---
        with t5:
            with st.spinner("Agent 5: ESP32 C++ & DSP ఫిల్టర్ కోడ్ రాస్తోంది..."):
                p5 = f"""
                Write complete, production-ready Arduino C++ code for {mcu_choice} for this project:
                {project_prompt}
                
                Requirements:
                1. Exact non-blocking sampling timer using `micros()`.
                2. Convert raw 12-bit ADC (0-4095) to exact Millivolts (mV) and remove the 1650mV DC offset.
                3. Include a clean digital IIR Band-Pass / Moving Average filter in C++ to remove 50Hz noise.
                4. Print clean formatted data for Arduino IDE Serial Plotter.
                5. After the code block, explain in simple Telugu how to upload and view the waveform in Serial Plotter.
                """
                res5 = ask_gemini(client, p5)
                st.markdown(res5)
