import streamlit as st
from google import genai
from google.genai import types
import schemdraw
import schemdraw.elements as elm
import matplotlib.pyplot as plt
import io
import re
import time
import math

# పేజీ సెటప్
st.set_page_config(page_title="Auto Senior Electronics Engineer", page_icon="⚡", layout="wide")

st.title("⚡ Autonomous Senior Electronics Engineer (Zero-Upload)")
st.markdown("**మీరు ఏ డేటాషీట్ లేదా ఫార్ములా అప్‌లోడ్ చేయాల్సిన పనిలేదు — మీ ఐడియా చెబితే చాలు, లైవ్ వెబ్ డేటాషీట్‌లతో A to Z హార్డ్‌వేర్ డిజైన్ సిద్ధమవుతుంది!**")

# సైడ్‌బార్: కేవలం API Key మాత్రమే
with st.sidebar:
    st.header("🔑 API Setup")
    api_key = st.text_input("మీ Gemini API Key పేస్ట్ చేయండి:", type="password").strip()
    st.divider()
    st.success("✅ **Built-in Engines Active:**\n- Live Web Datasheet Search (Auto)\n- All Electronics Formulas (Built-in)\n- Self-Healing Schematic Drawer\n- Breadboard & ESP32 Code Builder")

# మెయిన్ ఇన్‌పుట్ (చాలా సింపుల్ — కేవలం మీ ఐడియా మాత్రమే)
project_idea = st.text_area(
    "మీకు ఏ ఎలక్ట్రానిక్ ప్రాజెక్ట్ / సెన్సార్ కావాలో సాధారణ భాషలో రాయండి:",
    value="Low-cost PPG heart rate and SpO2 sensor circuit using discrete Op-Amps (MCP6002), BPW34 photodiode, 525nm & 660nm LEDs connected to ESP32-C3.",
    height=90
)

col1, col2 = st.columns(2)
with col1:
    mcu_type = st.selectbox("మైక్రోకంట్రోలర్ (Controller):", ["ESP32-C3 (3.3V)", "ESP32 DevKit (3.3V)", "Arduino Uno / Nano (5V)", "RP2040 / Pico (3.3V)"])
with col2:
    budget_pref = st.selectbox("బడ్జెట్ & డిజైన్ రకం:", ["Low-Cost Discrete Components (Under ₹500)", "Standard Prototype (Under ₹1500)", "Medical Grade High-Precision"])

# ఇన్‌బిల్ట్ సీనియర్ ఇంజనీర్ నాలెడ్జ్ బేస్ (మీరు టైప్ చేయాల్సిన పనిలేకుండా కోడ్ లోనే ఉంటుంది)
BUILTIN_ENGINEERING_BRAIN = """
VERIFIED ELECTRONICS FORMULAS & RULES:
1. Ohm's Law: V = I * R | LED Resistor: R = (V_supply - V_f) / I_led | Power: P = V * I (Keep resistor power < 125mW for 1/4W).
2. Voltage Divider & Mid-Rail Bias: V_out = V_in * (R2 / (R1 + R2)). For 3.3V single-supply Op-Amp, create 1.65V bias using two equal 10kΩ/100kΩ 1% resistors + 10µF bypass capacitor to GND.
3. RC Low-Pass / High-Pass Filter: fc = 1 / (2 * pi * R * C). (For PPG/ECG: High-pass fc = 0.5Hz to remove DC drift; Low-pass fc = 40Hz to block 50Hz AC powerline hum).
4. Non-Inverting Op-Amp Gain: Av = 1 + (Rf / Rin). Output V_out = V_in * Av (Must stay within 0.1V to 3.2V to prevent rail saturation).
5. Transimpedance Amplifier (TIA) for Photodiode: V_out = V_bias + (I_photo * Rf), Feedback capacitor Cf = 1 / (2 * pi * Rf * fc) for stability.
6. Instrumentation Amplifier (3-Op-Amp INA for ECG/Bio-Z/EDA): V_out = (V+ - V-) * (1 + 2*R1 / R_gain).
7. Decoupling Rule: Always place 100nF (0.1µF) ceramic capacitor within 2mm of every IC VDD-GND pin pair.
8. ADC Conversion: V_mv = (ADC_raw / (2^bits - 1)) * V_ref_mv.
"""

# Helper Function: Live Web Search Grounding + Auto-Retry
def ask_senior_engineer(client, prompt, use_web_search=True):
    models_to_try = ["gemini-3.8-flash"]
    try:
        for m in client.models.list():
            m_name = m.name.replace("models/", "")
            if ("flash" in m_name or "lite" in m_name) and m_name not in models_to_try:
                models_to_try.append(m_name)
    except Exception:
        pass

    config = None
    if use_web_search:
        config = types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )

    last_error = ""
    for model_name in models_to_try:
        for attempt in range(2):
            try:
                if config:
                    response = client.models.generate_content(model=model_name, contents=prompt, config=config)
                else:
                    response = client.models.generate_content(model=model_name, contents=prompt)
                return response.text
            except Exception as e:
                last_error = str(e)
                if "503" in last_error or "UNAVAILABLE" in last_error or "429" in last_error:
                    time.sleep(3)
                    continue
                elif use_web_search:
                    # ఒకవేళ ఫ్రీ కీలో search grounding సపోర్ట్ చేయకపోతే సాధారణ మోడ్ లో నడుస్తుంది
                    try:
                        response = client.models.generate_content(model=model_name, contents=prompt)
                        return response.text
                    except Exception as e2:
                        last_error = str(e2)
                break
    st.error(f"⚠️ సర్వర్ తాత్కాలికంగా బిజీగా ఉంది. 30 సెకన్ల తర్వాత మళ్ళీ ప్రయత్నించండి. ({last_error})")
    st.stop()

def extract_python_code(text):
    match = re.search(r"```python\n(.*?)\n```", text, re.DOTALL)
    return match.group(1) if match else text.replace("```python", "").replace("```", "").strip()

def sanitize_schemdraw(code):
    for bad in ["elm.Output()", "elm.Input()", "elm.Terminal()", "elm.Port()"]:
        code = code.replace(bad, "elm.Dot()")
    code = code.replace("d.draw()", "").replace("plt.show()", "")
    return code

# బటన్ క్లిక్ చేయగానే మొత్తం End-to-End డిజైన్ ఆటోమేటిక్ గా వస్తుంది
if st.button("🚀 Build Complete End-to-End Hardware Design", type="primary"):
    if not api_key:
        st.error("⚠️ దయచేసి ఎడమవైపు సైడ్‌బార్‌లో మీ Gemini API Key ఇవ్వండి.")
    else:
        client = genai.Client(api_key=api_key)

        with st.spinner("🔍 ఇంటర్నెట్ నుండి అసలు కాంపోనెంట్ డేటాషీట్‌లు తెచ్చి, పూర్తి సర్క్యూట్, లెక్కలు & కోడ్ తయారు చేస్తోంది..."):
            eng_prompt = f"""
            You are a Principal Electronics & Biomedical Hardware Engineer. The user is a beginner who does NOT know electronics formulas or datasheets.
            Automatically search and verify real datasheet pinouts, operating voltages, and component specs for the project below, and apply the built-in engineering rules.

            {BUILTIN_ENGINEERING_BRAIN}

            USER PROJECT: {project_idea}
            TARGET CONTROLLER: {mcu_type}
            BUDGET LEVEL: {budget_pref}

            Output the complete End-to-End solution strictly divided into these 4 exact markers:

            ===PART_1===
            (In clear, simple Telugu with English technical terms:
            1. **ఇది ఎలా పనిచేస్తుంది (Simple Explanation):** అసలు ఈ సర్క్యూట్ లాజిక్ ఏమిటి?
            2. **కాంపోనెంట్ల లిస్ట్ & ధరలు (Auto-Verified BOM Table):** Component Name, Exact Part Number, Value, Quantity, Role, Approx Indian Price (₹).
            3. **అసలు Datasheet పిన్ వివరాలు (Verified Pinout Table):** ప్రతి IC మరియు సెన్సార్ యొక్క ప్రతి పిన్ నంబర్ (Pin 1, Pin 2...) ఏమిటో డేటాషీట్ ప్రకారం కచ్చితంగా రాయండి.)

            ===PART_2===
            (In clear Telugu:
            1. **ఆటోమేటిక్ ఇంజనీరింగ్ లెక్కలు (Step-by-Step Math):** పైన ఎంచుకున్న రెసిస్టర్లు, కెపాసిటర్ల విలువలు ఎందుకు పెట్టామో Gain, Cut-off Frequency (Hz), LED Current ఫార్ములాలతో సహా విడమరిచి చూపండి.
            2. **సేఫ్టీ & నాయిస్ చెక్:** 50Hz కరెంట్ హమ్ మరియు సిగ్నల్ కట్ (Saturation) అవ్వకుండా ఎలా కాపాడామో వివరించండి.)

            ===PART_3===
            (In clear Telugu:
            1. **బ్రెడ్‌బోర్డ్ వైరింగ్ గైడ్ (Zero-Mistake Pin-to-Pin):** ఒక చిన్న పిల్లవాడికి కూడా అర్థమయ్యేలా 'ఈ పిన్ నుండి ఆ పిన్‌కు వైరు కలపండి' అని వరుసగా స్టెప్స్ రాయండి.
            2. **మల్టీమీటర్ టెస్ట్ (Multimeter Check):** బోర్డు ఆన్ చేశాక ఏ పిన్ దగ్గర ఎన్ని వోల్ట్లు (V) రావాలో చెప్పండి.
            3. **LTspice Simulation Code (.cir):** సర్క్యూట్ నిజమా కాదా చెక్ చేసుకోవడానికి SPICE నెట్‌లిస్ట్ ఇవ్వండి.)

            ===PART_4===
            (Complete, copy-paste ready Arduino C++ code for {mcu_type} with exact pin definitions, 12-bit/10-bit ADC to mV conversion, digital noise filter, and Serial Plotter output + Telugu లో కోడ్ ఎలా అప్‌లోడ్ చేసి గ్రాఫ్ చూడాలో గైడ్.)
            """
            full_output = ask_senior_engineer(client, eng_prompt, use_web_search=True)

        p1 = full_output.split("===PART_2===")[0].replace("===PART_1===", "").strip() if "===PART_2===" in full_output else full_output
        p2 = full_output.split("===PART_2===")[1].split("===PART_3===")[0].strip() if "===PART_3===" in full_output else ""
        p3 = full_output.split("===PART_3===")[1].split("===PART_4===")[0].strip() if "===PART_4===" in full_output else ""
        p4 = full_output.split("===PART_4===")[1].strip() if "===PART_4===" in full_output else ""

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "1️⃣ కాంపోనెంట్లు & Datasheet పిన్స్",
            "2️⃣ ఫార్ములాలు & లెక్కలు",
            "3️⃣ Circuit Schematic (సర్క్యూట్ బొమ్మ)",
            "4️⃣ Breadboard వైరింగ్ & టెస్ట్",
            "5️⃣ ESP32 / Arduino కోడ్"
        ])

        with tab1: st.markdown(p1)
        with tab2: st.markdown(p2)
        with tab4: st.markdown(p3)
        with tab5: st.markdown(p4)

        # --- TAB 3: AUTO SCHEMATIC DIAGRAM ---
        with tab3:
            with st.spinner("🎨 అసలైన Circuit Schematic బొమ్మ గీస్తోంది..."):
                sch_prompt = f"""
                Write ONLY valid Python code using `schemdraw` to draw a clean, left-to-right electronic circuit schematic for:
                {project_idea}

                STRICT RULES:
                1. Import `schemdraw`, `schemdraw.elements as elm`, `io`.
                2. `d = schemdraw.Drawing(show=False)`
                3. ONLY use these elements: `elm.Resistor()`, `elm.Capacitor()`, `elm.Opamp()`, `elm.Ground()`, `elm.Vdd()`, `elm.Dot()`, `elm.Line()`, `elm.Diode()`, `elm.LED()`, `elm.SourceV()`.
                4. NEVER use `elm.Output()`, `elm.Input()`, or `elm.Terminal()` — use `elm.Dot().label('Vout')`.
                5. Save to `buf`:
                   buf = io.BytesIO()
                   d.save(buf, format='png', dpi=300)
                   buf.seek(0)
                6. Output ONLY ```python ... ``` code.
                """
                raw_sch = ask_senior_engineer(client, sch_prompt, use_web_search=False)
                py_code = sanitize_schemdraw(extract_python_code(raw_sch))

                drawn = False
                for _ in range(2):
                    try:
                        env = {"schemdraw": schemdraw, "elm": elm, "plt": plt, "io": io}
                        exec(py_code, env)
                        if "buf" in env:
                            st.image(env["buf"], caption="Auto-Generated Circuit Schematic Diagram", use_container_width=True)
                            st.download_button("⬇️ Schematic బొమ్మ డౌన్‌లోడ్ (PNG)", data=env["buf"], file_name="circuit_diagram.png", mime="image/png")
                            drawn = True
                            break
                    except Exception as err:
                        fix_p = f"Fix this schemdraw Python error: '{err}'. Use ONLY Resistor, Capacitor, Opamp, Ground, Vdd, Dot, Line, LED, Diode. Return ONLY ```python``` code:\n{py_code}"
                        py_code = sanitize_schemdraw(extract_python_code(ask_senior_engineer(client, fix_p, use_web_search=False)))

                if not drawn:
                    st.warning("Schematic బొమ్మ గీయడంలో చిన్న ఇబ్బంది వచ్చింది. కింద కోడ్ ఉంది:")
                    st.code(py_code, language="python")
