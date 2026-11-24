import streamlit as st
from google import genai
import schemdraw
import schemdraw.elements as elm
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io
import re
import time
import math
import urllib.request
import json

# పేజీ సెటప్
st.set_page_config(page_title="Universal Principal Electronics R&D Studio", page_icon="⚡", layout="wide")

st.title("⚡ Universal Principal Electronics R&D Studio")
st.markdown("**Any Electronics Domain • End-to-End Physics & Worst-Case Math • Verified Datasheets • Schematic & 3D PCB • Production Firmware**")

# --- SIDEBAR: SMART API ROUTER ---
with st.sidebar:
    st.header("🔑 API Configuration")
    gemini_key = st.text_input("Gemini API Key (AIzaSy...):", type="password").strip()
    groq_key = st.text_input("Groq API Key (gsk_... Optional Backup):", type="password").strip()
    st.caption("💡 Gemini కీ 'AIzaSy' తో, Groq కీ 'gsk_' తో మొదలవుతాయి. ఏ ఒక్కటి ఇచ్చినా పనిచేస్తుంది.")
    st.divider()
    st.success("🏆 **Principal Engineer Mode:**\n- Universal R&D (Any Circuit/System)\n- Worst-Case Tolerance & Noise Math\n- EMI/EMC & Thermal PCB Rules\n- Auto-Healing Schematic & 3D PCB")

# ==============================================================================
# SECTION 1: UNIVERSAL ELECTRONICS DATASHEET & FORMULA WORKBENCH
# ==============================================================================
with st.expander("📚 UNIVERSAL ENGINEERING WORKBENCH: Datasheets, Pinouts & Live Calculators", expanded=False):
    w_col1, w_col2 = st.columns([1.2, 1])
    
    with w_col1:
        st.subheader("🔌 Core Component Datasheet Vault")
        comp_choice = st.selectbox("Select Component Category / IC:", [
            "Op-Amp: MCP6002 (3.3V Rail-to-Rail Precision)",
            "Op-Amp: OPA350 / OPA2350 (38MHz High-Speed / Bio-Z)",
            "Instrumentation Amp: AD8421 / INA128 (Low-Noise Differential)",
            "MCU: ESP32-C3 / ESP32-S3 (3.3V RISC-V / Xtensa)",
            "MOSFET: 2N7002 / AO3400 (Logic-Level N-Channel Switch)",
            "Power: AMS1117-3.3 / TPS7A02 (LDO Voltage Regulator)",
            "Sensor: BPW34 / TEMD5010 (PIN Photodiode) & NTC 10K B3950"
        ])
        
        universal_db = {
            "Op-Amp: MCP6002 (3.3V Rail-to-Rail Precision)": "Supply: 1.8V–6.0V | GBWP: 1MHz | Iq: 100µA | Pins: 1:OUTA, 2:INA-, 3:INA+, 4:GND, 5:INB+, 6:INB-, 7:OUTB, 8:VDD(+3.3V)",
            "Op-Amp: OPA350 / OPA2350 (38MHz High-Speed / Bio-Z)": "Supply: 2.7V–5.5V | GBWP: 38MHz | Slew Rate: 22V/µs | Pins: 1:OUTA, 2:INA-, 3:INA+, 4:V-, 5:INB+, 6:INB-, 7:OUTB, 8:V+",
            "Instrumentation Amp: AD8421 / INA128 (Low-Noise Differential)": "Supply: ±2.5V to ±18V | Gain: G = 1 + (9.9kΩ / Rg) | CMRR: >110dB | Pins: 1:-IN, 2:Rg1, 3:Rg2, 4:+IN, 5:-Vs, 6:REF, 7:VOUT, 8:+Vs",
            "MCU: ESP32-C3 / ESP32-S3 (3.3V RISC-V / Xtensa)": "Supply: 3.0V–3.6V | 12-bit SAR ADC (0–4095) | ADC1: GPIO0–GPIO4 | Max GPIO Current: 40mA | Hardware PWM/I2C/SPI",
            "MOSFET: 2N7002 / AO3400 (Logic-Level N-Channel Switch)": "Vds: 30V–60V | Vgs(th): 1.0V–2.1V (3.3V Logic Safe) | Pins (SOT-23): 1:Gate, 2:Source, 3:Drain",
            "Power: AMS1117-3.3 / TPS7A02 (LDO Voltage Regulator)": "Input: 4.5V–12V (AMS1117) | Output: 3.3V ±1% | Mandatory: 10µF Tantalum/Ceramic Cap on IN and OUT to GND",
            "Sensor: BPW34 / TEMD5010 (PIN Photodiode) & NTC 10K B3950": "BPW34: 400–1100nm, Dark Current 2nA (Cathode=Notch) | NTC 10K: R25=10kΩ, Beta=3950K (Use 10kΩ 0.1% divider)"
        }
        st.info(f"**Verified Datasheet Specs:**\n\n`{universal_db[comp_choice]}`")

    with w_col2:
        st.subheader("🧮 Universal Electronics Formula Solver")
        calc_mode = st.selectbox("Select Formula:", [
            "RC Filter Cut-off Frequency (fc)",
            "Op-Amp Gain (Non-Inverting & Inverting)",
            "Voltage Divider & Mid-Rail Bias",
            "LED / Load Current Limiting Resistor",
            "Reactance (Xc = 1 / 2πfC) & Impedance"
        ])
        if calc_mode == "RC Filter Cut-off Frequency (fc)":
            r_v = st.number_input("R (kΩ):", value=10.0)
            c_v = st.number_input("C (nF):", value=100.0)
            st.success(f"**fc = {1.0 / (2 * math.pi * r_v * 1000 * c_v * 1e-9):.2f} Hz**")
        elif calc_mode == "Op-Amp Gain (Non-Inverting & Inverting)":
            r1_v = st.number_input("Rin (kΩ):", value=1.0)
            r2_v = st.number_input("Rf (kΩ):", value=47.0)
            st.success(f"**Non-Inverting Gain = {1 + r2_v/r1_v:.2f}x** | **Inverting Gain = -{r2_v/r1_v:.2f}x**")
        elif calc_mode == "Voltage Divider & Mid-Rail Bias":
            vin_v = st.number_input("Vin (V):", value=5.0)
            rt_v = st.number_input("R_top (kΩ):", value=10.0)
            rb_v = st.number_input("R_bottom (kΩ):", value=10.0)
            st.success(f"**Vout = {vin_v * (rb_v / (rt_v + rb_v)):.3f} V**")
        elif calc_mode == "LED / Load Current Limiting Resistor":
            vs_v = st.number_input("Supply (V):", value=3.3)
            vf_v = st.number_input("Drop Vf (V):", value=1.8)
            im_v = st.number_input("Current (mA):", value=15.0)
            st.success(f"**R = {(vs_v - vf_v)/(im_v/1000):.1f} Ω** | **Power = {(vs_v - vf_v)*im_v:.1f} mW**")
        elif calc_mode == "Reactance (Xc = 1 / 2πfC) & Impedance":
            freq_v = st.number_input("Frequency (kHz):", value=50.0)
            cap_v = st.number_input("Capacitor (nF):", value=10.0)
            xc = 1.0 / (2 * math.pi * (freq_v * 1000) * (cap_v * 1e-9))
            st.success(f"**Capacitive Reactance (Xc) = {xc:.2f} Ω**")

st.divider()

# ==============================================================================
# SECTION 2: UNIVERSAL END-TO-END R&D PROJECT INPUT
# ==============================================================================
st.subheader("🚀 Principal Engineer End-to-End R&D Generator")

c1, c2, c3 = st.columns(3)
with c1:
    rd_domain = st.selectbox("R&D Engineering Domain:", [
        "Any / Custom Electronics R&D",
        "Biomedical & Wearable Sensors (PPG, ECG, Bio-Z, EDA)",
        "Power Electronics (SMPS, Buck/Boost, BMS, Solar MPPT)",
        "Analog Signal Conditioning & Precision Instrumentation",
        "Motor Control, Robotics & Actuators (BLDC, Servo, H-Bridge)",
        "RF, Wireless & IoT Hardware (LoRa, BLE, Sub-GHz)",
        "Audio Electronics & Active Filters (Class-D, Pre-Amp)"
    ])
with c2:
    mcu_choice = st.selectbox("Target Controller / Processor:", [
        "ESP32-C3 / ESP32-S3 (3.3V, 12-bit ADC)",
        "STM32F4 / STM32G4 (3.3V, 12-bit/16-bit ADC)",
        "RP2040 / Raspberry Pi Pico (3.3V)",
        "Arduino Uno / Nano / ATmega328P (5V)",
        "Pure Analog Hardware (No MCU)"
    ])
with c3:
    eng_depth = st.selectbox("Engineering Depth:", [
        "Principal Architect (Shock-Level Full R&D + Worst-Case Math)",
        "Rapid Breadboard Prototype (Beginner Friendly Telugu)"
    ])

project_prompt = st.text_area(
    "మీ R&D ప్రాజెక్ట్ ఐడియాను వివరంగా రాయండి (ఏ రకమైన సర్క్యూట్ అయినా సరే):",
    value="Design a high-precision 3-frequency Bio-Impedance (Bio-Z) and PPG analog front-end using discrete Op-Amps (OPA350 & MCP6002), Howland current pump (10kHz, 50kHz, 250kHz), and synchronous I/Q demodulation for ESP32-C3.",
    height=95
)

# ==============================================================================
# HELPER: SMART ZERO-404 / ZERO-503 ENGINE
# ==============================================================================
def call_groq_safe(g_key, prompt):
    if not g_key.startswith("gsk_"):
        return None, "Invalid Groq Key format (must start with gsk_)"
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {g_key}", "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    data = json.dumps({"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.2}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=35) as resp:
        return json.loads(resp.read().decode("utf-8"))["choices"][0]["message"]["content"], "Groq (Llama-3.3-70B)"

def run_universal_engine(gem_key, grq_key, prompt):
    errors = []
    if gem_key:
        try:
            client = genai.Client(api_key=gem_key)
            # లైవ్ గా అందుబాటులో ఉన్న అన్ని మోడల్స్ ని కనుగొంటుంది
            available_models = []
            for m in client.models.list():
                m_name = m.name.replace("models/", "")
                if "gemini" in m_name and "embedding" not in m_name and "imagen" not in m_name:
                    available_models.append(m_name)
            
            # Flash మోడల్స్ కి మొదటి ప్రాధాన్యత ఇస్తుంది
            prioritized = [m for m in available_models if "flash" in m] + [m for m in available_models if "pro" in m]
            if not prioritized:
                prioritized = ["gemini-3.8-flash", "gemini-2.5-flash"]

            for model_id in prioritized[:4]:
                for _ in range(2):
                    try:
                        resp = client.models.generate_content(model=model_id, contents=prompt)
                        return resp.text, f"Gemini ({model_id})"
                    except Exception as e:
                        err_s = str(e)
                        errors.append(f"{model_id}: {err_s[:80]}")
                        if "503" in err_s or "429" in err_s:
                            time.sleep(2)
                            continue
                        break
        except Exception as e:
            errors.append(f"Gemini Init: {str(e)[:80]}")

    if grq_key:
        try:
            res, eng = call_groq_safe(grq_key, prompt)
            if res:
                return res, eng
            errors.append(eng)
        except Exception as e:
            errors.append(f"Groq: {str(e)[:80]}")

    st.error("⚠️ AI సర్వర్ కనెక్షన్ తాత్కాలికంగా రద్దీగా ఉంది. 15 సెకన్ల తర్వాత మళ్ళీ నొక్కండి.\n\n**Diagnostic Log:** " + " | ".join(errors))
    st.stop()

# ==============================================================================
# HELPER: DYNAMIC 3D PCB LAYOUT RENDERER
# ==============================================================================
def render_universal_3d_pcb(proj_title, domain_name, mcu_name):
    fig, ax = plt.subplots(figsize=(10, 5.6), dpi=300)
    fig.patch.set_facecolor('#0e1117')
    ax.set_facecolor('#0e1117')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis('off')

    # 3D Substrate Depth & Gold Edge Plating
    ax.add_patch(patches.FancyBboxPatch((7.5, 5.5), 86, 46, boxstyle="round,pad=1.5", facecolor='#052412', edgecolor='#021209', lw=2))
    ax.add_patch(patches.FancyBboxPatch((6.8, 6.2), 86, 46, boxstyle="round,pad=1.5", facecolor='#14522d', edgecolor='#0a2e18', lw=1.5))
    ax.add_patch(patches.FancyBboxPatch((6, 7), 86, 46, boxstyle="round,pad=1.5", facecolor='#0b6632', edgecolor='#d4af37', lw=2.5))

    # 4 Corner ENIG Gold Mounting Vias
    for hx, hy in [(9, 10), (89, 10), (9, 50), (89, 50)]:
        ax.add_patch(patches.Circle((hx, hy), 2.0, facecolor='#d4af37', edgecolor='#7d6014', lw=1))
        ax.add_patch(patches.Circle((hx, hy), 0.9, facecolor='#0e1117'))

    # Multi-Layer Copper Traces & Power/Ground Planes
    ax.plot([14, 84], [46, 46], color='#d4af37', lw=3.2, zorder=2) # VCC Rail
    ax.plot([14, 84], [13, 13], color='#22b560', lw=4.5, zorder=2) # Ground Plane
    for tx, ty in [([21, 38], [36, 33]), ([21, 38], [23, 27]), ([56, 74], [33, 36]), ([56, 74], [27, 23])]:
        ax.plot(tx, ty, color='#1ca354', lw=3.0, zorder=2)

    # Input Sensor / Front-End Stage Block (Left)
    ax.add_patch(patches.Rectangle((12, 20), 9, 19, facecolor='#1c2430', edgecolor='#d4af37', lw=1.5, zorder=4))
    ax.text(16.5, 29.5, "FRONT-END\nSENSOR /\nINPUT STAGE", color='#00ffcc', fontsize=7, ha='center', va='center', fontweight='bold', zorder=5)

    # Central Analog / Power IC (SOIC-8 / TSSOP-16 3D Package)
    ic_x, ic_y, ic_w, ic_h = 39, 22, 16, 16
    for idx in range(4):
        py = ic_y + 1.8 + idx * 3.8
        ax.add_patch(patches.Rectangle((ic_x - 2.4, py), 2.4, 1.5, facecolor='#d4af37', zorder=3))
        ax.add_patch(patches.Rectangle((ic_x + ic_w, py), 2.4, 1.5, facecolor='#d4af37', zorder=3))
        ax.text(ic_x - 3.2, py + 0.6, f"P{4-idx}", color='#ffd700', fontsize=6.5, ha='right', va='center', fontweight='bold')
        ax.text(ic_x + ic_w + 3.2, py + 0.6, f"P{5+idx}", color='#ffd700', fontsize=6.5, ha='left', va='center', fontweight='bold')
    ax.add_patch(patches.FancyBboxPatch((ic_x, ic_y), ic_w, ic_h, boxstyle="round,pad=0.3", facecolor='#181818', edgecolor='#888888', lw=1.5, zorder=4))
    ax.add_patch(patches.Circle((ic_x + 2.2, ic_y + ic_h - 2.2), 0.8, facecolor='#999999', zorder=5))
    ax.text(ic_x + ic_w/2, ic_y + ic_h/2, "MAIN IC\nANALOG / PWR\nCORE", color='white', fontsize=8, ha='center', va='center', fontweight='bold', zorder=5)

    # Precision 0.1% Resistors & C0G Capacitors
    for sx, sy, lbl, col in [(28, 36, "R_in\n0.1%", '#111111'), (28, 20, "C_flt\nC0G", '#8d5524'), (62, 36, "R_fb\n0.1%", '#111111'), (62, 20, "C_dec\n100nF", '#8d5524')]:
        ax.add_patch(patches.Rectangle((sx-0.8, sy), 1.0, 2.8, facecolor='#cccccc', zorder=4))
        ax.add_patch(patches.Rectangle((sx+4.0, sy), 1.0, 2.8, facecolor='#cccccc', zorder=4))
        ax.add_patch(patches.Rectangle((sx, sy), 4.2, 2.8, facecolor=col, edgecolor='#555555', lw=0.8, zorder=5))
        ax.text(sx+2.1, sy-2.8, lbl, color='white', fontsize=6.8, ha='center', fontweight='bold')

    # MCU Interface Header (Right)
    ax.add_patch(patches.Rectangle((74, 19), 11, 22, facecolor='#1a1a1a', edgecolor='#d4af37', lw=1.5, zorder=4))
    for i, pin_txt in enumerate(["VCC_3V3", "ADC_SIG", "CTRL_IO", "GND_REF"]):
        py = 37 - i * 4.8
        ax.add_patch(patches.Circle((76.5, py), 1.3, facecolor='#d4af37', edgecolor='white', lw=0.8, zorder=5))
        ax.text(79, py, pin_txt, color='#00ffcc', fontsize=6.5, va='center', fontweight='bold', zorder=6)

    ax.text(49, 55.5, f"3D PCB ARCHITECTURE: {proj_title[:48]}", color='#00ffcc', fontsize=9.5, ha='center', fontweight='bold')
    ax.text(49, 2.2, f"Domain: {domain_name} | Target: {mcu_name} | 4-Layer Star-Ground & Guard-Ring Layout", color='#bbbbbb', fontsize=7.5, ha='center')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf

def sanitize_schemdraw(code):
    for bad in ["elm.Output()", "elm.Input()", "elm.Terminal()", "elm.Port()"]:
        code = code.replace(bad, "elm.Dot()")
    return code.replace("d.draw()", "").replace("plt.show()", "").strip()

# ==============================================================================
# EXECUTION: PRINCIPAL ENGINEER SINGLE-CALL PIPELINE
# ==============================================================================
if st.button("⚡ Execute Principal Engineer End-to-End R&D", type="primary"):
    if not gemini_key and not groq_key:
        st.error("⚠️ దయచేసి ఎడమవైపు సైడ్‌బార్‌లో మీ Gemini API Key (AIzaSy...) ఇవ్వండి.")
    else:
        with st.spinner("🧠 Principal Electronics Architect పూర్తి సిస్టమ్, Worst-Case లెక్కలు, Schematic & కోడ్ సిద్ధం చేస్తోంది..."):
            master_prompt = f"""
            You are a World-Class Principal Electronics & Hardware R&D Architect (30+ years experience in Analog, Power, RF, Biomedical, and Embedded Systems).
            Design a shockingly thorough, mathematically rigorous, end-to-end hardware solution that any senior electronics engineer would respect.

            DOMAIN: {rd_domain}
            PROJECT SPECIFICATION: {project_prompt}
            TARGET CONTROLLER: {mcu_choice}
            DEPTH: {eng_depth}

            Generate the COMPLETE solution in ONE response strictly divided into these 5 markers (Explain concepts clearly in Telugu while keeping all engineering terms, formulas, part numbers, and code in crisp English):

            ===TAB1===
            **1. System Architecture & First-Principles Physics:**
            - Explain the complete end-to-end signal/power chain, impedance matching, noise floor, and why each stage exists.
            - **Complete Verified BOM Table:** Component Designator, Exact Part Number (e.g., OPA350, MCP6002, 0.1% Thin-Film Resistor, C0G/NP0 Capacitor), Exact Value, Package, Qty, Role, and Approx Indian Price (₹).
            - **Verified Datasheet Pinout & Absolute Maximum Ratings Table:** Exact pin numbers and critical limits (GBWP, Slew Rate, Vcm, Thermal limits).

            ===TAB2===
            **2. End-to-End Engineering Math & Worst-Case Tolerance Analysis:**
            - Show exact step-by-step derivations for EVERY component value (Gain, Cut-off frequencies $f_c$, Stability phase margin, Current limits, Thermal dissipation $P = I^2R$, ADC LSB resolution).
            - Include **Worst-Case Error Budget** (how 1% resistor tolerance, input offset voltage $V_{{os}}$, and temperature drift affect accuracy) + **EMI/EMC & PCB Layout Rules** (Star grounding, guard rings, decoupling).

            ===TAB3===
            Write ONLY valid Python `schemdraw` code inside ```python ... ``` to draw a clean, professional horizontal circuit schematic.
            Rules: `d = schemdraw.Drawing(show=False)`, use ONLY `elm.Resistor()`, `elm.Capacitor()`, `elm.Opamp()`, `elm.Ground()`, `elm.Vdd()`, `elm.Dot()`, `elm.Line()`, `elm.LED()`, `elm.Diode()`, `elm.SourceV()`, `elm.Inductor()`. NEVER use `elm.Output()` or `elm.Input()`. Save to `buf`:
            ```python
            buf = io.BytesIO()
            d.save(buf, format='png', dpi=300)
            buf.seek(0)
            ```

            ===TAB4===
            **4. Assembly, Bench Testing & SPICE Verification:**
            - Step-by-step Pin-to-Pin Wiring / Soldering Guide (zero ambiguity).
            - Bench Verification Protocol: Exact DC bias voltages and Oscilloscope waveforms expected at every test point (TP1, TP2, TP3) + Failure Mode Troubleshooting table.
            - Complete, runnable **LTspice `.cir` Netlist** with `.ac` / `.tran` simulation directives.

            ===TAB5===
            **5. Production-Grade Embedded Firmware & Signal Processing:**
            - Complete, non-blocking C++ firmware for {mcu_choice} using hardware timers / `micros()`, exact physical unit conversion formulas, digital DSP filtering (IIR/FIR/Lock-in/I-Q demodulation as applicable), and Serial Plotter / Telemetry output + Telugu setup instructions.
            """
            raw_out, engine_used = run_universal_engine(gemini_key, groq_key, master_prompt)
            st.toast(f"✅ పూర్తయింది! Engine: {engine_used}")

        def slice_sec(txt, s, e=None):
            if s not in txt: return ""
            sub = txt.split(s)[1]
            return sub.split(e)[0].strip() if (e and e in sub) else sub.strip()

        t1_data = slice_sec(raw_out, "===TAB1===", "===TAB2===")
        t2_data = slice_sec(raw_out, "===TAB2===", "===TAB3===")
        t3_raw  = slice_sec(raw_out, "===TAB3===", "===TAB4===")
        t4_data = slice_sec(raw_out, "===TAB4===", "===TAB5===")
        t5_data = slice_sec(raw_out, "===TAB5===")

        tabs = st.tabs([
            "1️⃣ System Architecture & BOM",
            "2️⃣ End-to-End Math & PCB Rules",
            "3️⃣ Circuit Schematic (బొమ్మ)",
            "4️⃣ 3D PCB Layout (బోర్డు)",
            "5️⃣ Bench Test & SPICE",
            "6️⃣ Production C++ Firmware"
        ])

        with tabs[0]: st.markdown(t1_data)
        with tabs[1]: st.markdown(t2_data)
        with tabs[4]: st.markdown(t4_data)
        with tabs[5]: st.markdown(t5_data)

        with tabs[2]:
            match = re.search(r"```python\n(.*?)\n```", t3_raw, re.DOTALL)
            py_code = sanitize_schemdraw(match.group(1) if match else t3_raw.replace("```python", "").replace("```", ""))
            try:
                env = {"schemdraw": schemdraw, "elm": elm, "plt": plt, "io": io}
                exec(py_code, env)
                if "buf" in env:
                    st.image(env["buf"], caption="Principal-Level Circuit Schematic Diagram", use_container_width=True)
                    st.download_button("⬇️ Schematic PNG డౌన్‌లోడ్", data=env["buf"], file_name="circuit_schematic.png", mime="image/png")
                else:
                    st.code(py_code, language="python")
            except Exception as err:
                st.warning(f"Schematic కోడ్ వివరాలు ({err}):")
                st.code(py_code, language="python")

        with tabs[3]:
            pcb_buf = render_universal_3d_pcb(project_prompt, rd_domain, mcu_choice)
            st.image(pcb_buf, caption="3D PCB Top-Layer Architecture (ENIG Gold Pads, Star-Ground & Guard-Ring)", use_container_width=True)
            st.download_button("⬇️ 3D PCB PNG డౌన్‌లోడ్", data=pcb_buf, file_name="3d_pcb_architecture.png", mime="image/png")
