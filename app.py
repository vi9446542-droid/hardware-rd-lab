import streamlit as st
from google import genai
import schemdraw
import schemdraw.elements as elm
import matplotlib.pyplot as plt
import io
import re
import time
import urllib.request
import json

# పేజీ సెటప్
st.set_page_config(page_title="Instant Hardware R&D Studio", page_icon="⚡", layout="wide")

st.title("⚡ Instant Hardware R&D Platform (Ultra-Fast & Zero-503)")
st.markdown("**Google / WhatsApp లాగా వేగంగా — ఒక్క కాల్ లోనే కాంపోనెంట్లు, ఫార్ములాలు, సర్క్యూట్ బొమ్మ, బ్రెడ్‌బోర్డ్ వైరింగ్ & ESP32 కోడ్!**")

# సైడ్‌బార్: API Keys
with st.sidebar:
    st.header("🔑 API Configuration")
    gemini_key = st.text_input("1. Gemini API Key (Primary):", type="password").strip()
    groq_key = st.text_input("2. Groq API Key (Optional 0.5s Backup - console.groq.com):", type="password").strip()
    st.caption("💡 Gemini సర్వర్ 503 బిజీగా ఉన్నప్పుడు Groq కీ ఉంటే 0.5 సెకన్లలో ఆటోమేటిక్‌గా పనిచేస్తుంది!")

# మెయిన్ ఇన్‌పుట్
project_idea = st.text_area(
    "మీ ఎలక్ట్రానిక్ ప్రాజెక్ట్ ఐడియా రాయండి:",
    value="Low-cost PPG heart rate sensor circuit using BPW34 photodiode, 525nm green LED, MCP6002 op-amp (Gain 100, 0.5Hz to 40Hz bandpass filter, 1.65V mid-rail bias) for ESP32-C3.",
    height=90
)

col1, col2 = st.columns(2)
with col1:
    mcu_type = st.selectbox("Controller:", ["ESP32-C3 (3.3V)", "ESP32 DevKit (3.3V)", "Arduino Uno (5V)", "RP2040 Pico (3.3V)"])
with col2:
    budget_pref = st.selectbox("Design Type:", ["Low-Cost Discrete (Under ₹500)", "Standard Prototype (Under ₹1500)"])

# ఇన్‌బిల్ట్ ఫార్ములాలు
BUILTIN_RULES = """
FORMULAS: LED R=(Vs-Vf)/I | 1.65V Bias: two equal 10kΩ/100kΩ + 10µF cap | RC Filter: fc=1/(2*pi*R*C) | Non-Inverting Gain: Av=1+(Rf/Rin) | TIA: Vout=Vbias+(I*Rf), Cf=1/(2*pi*Rf*fc) | Decoupling: 100nF near VDD-GND.
"""

# Fast Groq Fallback Caller (Standard Python urllib — no extra library needed!)
def call_groq_backup(api_key, prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    data = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        res_json = json.loads(resp.read().decode("utf-8"))
        return res_json["choices"][0]["message"]["content"]

# Single-Call Ultra-Fast Engine
def run_instant_engine(gem_key, grq_key, prompt):
    if gem_key:
        client = genai.Client(api_key=gem_key)
        # అందుబాటులో ఉన్న అన్ని ఫాస్ట్ మోడల్స్ లిస్ట్ తీసుకుంటుంది
        models = ["gemini-3.8-flash"]
        try:
            for m in client.models.list():
                name = m.name.replace("models/", "")
                if ("flash" in name or "lite" in name) and name not in models:
                    models.append(name)
        except Exception:
            pass

        for m_name in models:
            try:
                resp = client.models.generate_content(model=m_name, contents=prompt)
                return resp.text, f"Gemini ({m_name})"
            except Exception as e:
                err_str = str(e)
                if "503" in err_str or "UNAVAILABLE" in err_str or "429" in err_str:
                    time.sleep(1.5)
                    continue
                break

    # Gemini 503 బిజీగా ఉంటే వెంటనే Groq Backup నడుస్తుంది
    if grq_key:
        try:
            text = call_groq_backup(grq_key, prompt)
            return text, "Groq Instant Backup (Llama-3.3-70B)"
        except Exception as e:
            st.error(f"Backup Error: {e}")

    st.error("⚠️ ప్రస్తుతం Gemini సర్వర్ తాత్కాలికంగా రద్దీగా ఉంది (503). వెంటనే 0.5 సెకన్లలో పనిచేయడానికి ఎడమవైపు సైడ్‌బార్‌లో ఉచిత Groq API Key (console.groq.com) ఇవ్వండి లేదా 30 సెకన్ల తర్వాత మళ్ళీ నొక్కండి.")
    st.stop()

def sanitize_schemdraw(code):
    for bad in ["elm.Output()", "elm.Input()", "elm.Terminal()", "elm.Port()"]:
        code = code.replace(bad, "elm.Dot()")
    return code.replace("d.draw()", "").replace("plt.show()", "").strip()

if st.button("⚡ Build Complete Design Instantly", type="primary"):
    if not gemini_key and not groq_key:
        st.error("⚠️ దయచేసి సైడ్‌బార్‌లో Gemini API Key (లేదా Groq API Key) ఇవ్వండి.")
    else:
        with st.spinner("⚡ ఒక్క కాల్ లోనే A to Z డిజైన్, సర్క్యూట్ బొమ్మ & కోడ్ సిద్ధమవుతున్నాయి..."):
            single_shot_prompt = f"""
            You are a Principal Electronics Hardware Engineer. The user is a beginner.
            {BUILTIN_RULES}
            Project: {project_idea} | MCU: {mcu_type} | Budget: {budget_pref}

            Generate the COMPLETE End-to-End output in ONE response using these exact 5 markers:

            ===TAB1===
            (In simple Telugu with English tech terms: 1. How it works, 2. BOM Table with Component, Exact Part/Value, Qty, Role, Price in ₹, 3. Verified Datasheet Pinout Table for every IC/Sensor.)

            ===TAB2===
            (In Telugu: Step-by-step math calculations for every resistor, capacitor, Gain, Cut-off frequency Hz, and LED current + 50Hz noise & saturation safety.)

            ===TAB3===
            (Write ONLY valid Python `schemdraw` code inside ```python ... ``` to draw the circuit schematic. Rules: `d = schemdraw.Drawing(show=False)`, use ONLY `elm.Resistor()`, `elm.Capacitor()`, `elm.Opamp()`, `elm.Ground()`, `elm.Vdd()`, `elm.Dot()`, `elm.Line()`, `elm.LED()`, `elm.Diode()`, `elm.SourceV()`. Never use `elm.Output()`. Save to `buf`:
            buf = io.BytesIO()
            d.save(buf, format='png', dpi=300)
            buf.seek(0)
            )

            ===TAB4===
            (In Telugu: Step-by-step Breadboard Pin-to-Pin Wiring Guide, Multimeter voltage check before connecting MCU, and LTspice .cir netlist.)

            ===TAB5===
            (Complete non-blocking Arduino C++ code using micros() for {mcu_type} with ADC to mV conversion, 1650mV offset removal, digital filter, Serial Plotter output + Telugu upload guide.)
            """
            raw_out, engine_used = run_instant_engine(gemini_key, groq_key, single_shot_prompt)
            st.toast(f"✅ పూర్తయింది! Engine: {engine_used}")

        def get_part(text, start_m, end_m=None):
            if start_m not in text: return ""
            sub = text.split(start_m)[1]
            return sub.split(end_m)[0].strip() if (end_m and end_m in sub) else sub.strip()

        t1_txt = get_part(raw_out, "===TAB1===", "===TAB2===")
        t2_txt = get_part(raw_out, "===TAB2===", "===TAB3===")
        t3_raw = get_part(raw_out, "===TAB3===", "===TAB4===")
        t4_txt = get_part(raw_out, "===TAB4===", "===TAB5===")
        t5_txt = get_part(raw_out, "===TAB5===")

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "1️⃣ కాంపోనెంట్లు & Datasheet పిన్స్",
            "2️⃣ ఫార్ములాలు & లెక్కలు",
            "3️⃣ Circuit Schematic (బొమ్మ)",
            "4️⃣ Breadboard వైరింగ్ & టెస్ట్",
            "5️⃣ ESP32 / Arduino కోడ్"
        ])

        with tab1: st.markdown(t1_txt)
        with tab2: st.markdown(t2_txt)
        with tab4: st.markdown(t4_txt)
        with tab5: st.markdown(t5_txt)

        with tab3:
            match = re.search(r"```python\n(.*?)\n```", t3_raw, re.DOTALL)
            py_code = sanitize_schemdraw(match.group(1) if match else t3_raw.replace("```python", "").replace("```", ""))
            try:
                env = {"schemdraw": schemdraw, "elm": elm, "plt": plt, "io": io}
                exec(py_code, env)
                if "buf" in env:
                    st.image(env["buf"], caption="Circuit Schematic Diagram", use_container_width=True)
                    st.download_button("⬇️ బొమ్మ డౌన్‌లోడ్ (PNG)", data=env["buf"], file_name="schematic.png", mime="image/png")
                else:
                    st.code(py_code, language="python")
            except Exception as err:
                st.warning(f"Schematic గీయడంలో చిన్న సింటాక్స్ మార్పు అవసరం ({err}). కోడ్ కింద ఉంది:")
                st.code(py_code, language="python")
