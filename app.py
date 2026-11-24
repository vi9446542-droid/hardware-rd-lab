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
st.set_page_config(page_title="3D PCB & Hardware R&D Dashboard", page_icon="🎛️", layout="wide")

st.title("🎛️ Autonomous 3D PCB & Hardware Engineering Dashboard")
st.markdown("**Live Component Datasheets • Built-in Formulas • 3D-Style Clear PCB Layout • Schematic • ESP32 Code**")

# --- SIDEBAR: API SETUP ---
with st.sidebar:
    st.header("🔑 API Setup")
    gemini_key = st.text_input("1. Gemini API Key (Primary):", type="password").strip()
    groq_key = st.text_input("2. Groq API Key (Optional 0.5s Backup):", type="password").strip()
    st.divider()
    st.info("💡 **Zero-Upload Mode:** అన్ని కాంపోనెంట్ల డేటాషీట్ పిన్స్ & ఫార్ములాలు కింద Dashboard లోనే సిద్ధంగా ఉన్నాయి!")

# ==============================================================================
# SECTION A: ALWAYS-VISIBLE COMPONENT DATASHEET & FORMULA DASHBOARD
# ==============================================================================
with st.expander("📚 LIVE DASHBOARD: Components Datasheet Pinouts & Electronics Formulas (క్లిక్ చేసి చూడండి)", expanded=True):
    d_col1, d_col2 = st.columns([1.2, 1])
    
    with d_col1:
        st.subheader("🔌 Built-in Component Datasheets (Verified Pinouts)")
        selected_ic = st.selectbox("కాంపోనెంట్ ఎంచుకుని దాని అసలు Datasheet వివరాలు చూడండి:", [
            "MCP6002 (Dual Rail-to-Rail Op-Amp - PPG/Bio-Z)",
            "LM358 (Dual Low-Power Op-Amp)",
            "BPW34 / TEMD5010 (PIN Photodiode - Optical PPG)",
            "ESP32-C3 (3.3V RISC-V Microcontroller)",
            "NTC 10K B3950 (0.5mm Glass Micro-Bead Thermistor)",
            "2N7002 (N-Channel MOSFET - LED Switching)"
        ])
        
        ic_database = {
            "MCP6002 (Dual Rail-to-Rail Op-Amp - PPG/Bio-Z)": {
                "Supply": "1.8V to 6.0V (Single Supply 3.3V Ideal)",
                "Specs": "GBWP: 1 MHz | Rail-to-Rail Input/Output | Quiescent Current: 100µA",
                "Pins": "Pin 1: OUT A | Pin 2: IN A- | Pin 3: IN A+ | Pin 4: VSS (GND) | Pin 5: IN B+ | Pin 6: IN B- | Pin 7: OUT B | Pin 8: VDD (+3.3V)"
            },
            "LM358 (Dual Low-Power Op-Amp)": {
                "Supply": "3.0V to 32V (Note: Output max is Vcc - 1.5V, so at 3.3V max out is 1.8V)",
                "Specs": "GBWP: 1 MHz | Not Rail-to-Rail | Use MCP6002 for full 3.3V swing",
                "Pins": "Pin 1: OUT 1 | Pin 2: IN 1- | Pin 3: IN 1+ | Pin 4: GND | Pin 5: IN 2+ | Pin 6: IN 2- | Pin 7: OUT 2 | Pin 8: VCC (+3.3V/5V)"
            },
            "BPW34 / TEMD5010 (PIN Photodiode - Optical PPG)": {
                "Supply": "Reverse Bias 0V (Photovoltaic) to 5V (Photoconductive)",
                "Specs": "Wavelength: 400nm–1100nm (Peak 850nm, works great at 525nm/660nm/940nm) | Dark Current: 2nA",
                "Pins": "Anode (+) -> Op-Amp IN- (Virtual Ground 1.65V) | Cathode (-) [Marked Notch/Tab] -> +3.3V or Bias"
            },
            "ESP32-C3 (3.3V RISC-V Microcontroller)": {
                "Supply": "3.3V (Never apply >3.3V to GPIO pins!)",
                "Specs": "12-bit ADC (0–4095) | Built-in Wi-Fi & BLE 5.0 | Hardware I2C/SPI/PWM",
                "Pins": "ADC1 Analog Pins: GPIO0, GPIO1, GPIO2, GPIO3, GPIO4 | 3V3: Power Out | GND: Ground"
            },
            "NTC 10K B3950 (0.5mm Glass Micro-Bead Thermistor)": {
                "Supply": "3.3V via 10kΩ (0.1% precision) Wheatstone / Voltage Divider",
                "Specs": "R25 = 10,000Ω at 25°C | Beta = 3950K | Fast thermal response (<1 sec)",
                "Pins": "2-Wire Non-Polarized: Pin 1 -> 3.3V (via 10kΩ 0.1% resistor) | Pin 2 -> GND | Midpoint -> ADC"
            },
            "2N7002 (N-Channel MOSFET - LED Switching)": {
                "Supply": "Max Vds: 60V | Gate Threshold Vgs(th): 1.0V–2.5V (3.3V GPIO Compatible)",
                "Specs": "Continuous Drain Current: 115mA | Rds(on): ~2Ω | Ideal for PWM LED pulsing",
                "Pins": "Pin 1: Gate (to ESP32 GPIO via 100Ω) | Pin 2: Source (to GND) | Pin 3: Drain (to LED Cathode)"
            }
        }
        info = ic_database[selected_ic]
        st.info(f"**⚡ Supply:** {info['Supply']}\n\n**📊 Key Specs:** {info['Specs']}\n\n**📍 Exact Pinout:** `{info['Pins']}`")

    with d_col2:
        st.subheader("📐 Live Electronics Formula Calculator")
        f_tab1, f_tab2, f_tab3 = st.tabs(["RC Filter (Hz)", "Op-Amp Gain", "LED Resistor"])
        with f_tab1:
            r_k = st.number_input("Resistor R (kΩ):", value=39.0, key="dash_r")
            c_n = st.number_input("Capacitor C (nF):", value=100.0, key="dash_c")
            fc = 1.0 / (2 * math.pi * (r_k * 1000) * (c_n * 1e-9))
            st.success(f"**Cut-off Frequency ($f_c$) = {fc:.2f} Hz**")
        with f_tab2:
            rin = st.number_input("Rin (kΩ):", value=1.0, key="dash_rin")
            rf = st.number_input("Rf (kΩ):", value=100.0, key="dash_rf")
            st.success(f"**Gain ($1 + R_f/R_{{in}}$) = {1 + rf/rin:.1f}x**")
        with f_tab3:
            vs = st.number_input("Supply (V):", value=3.3, key="dash_vs")
            vf = st.number_input("LED Vf (V):", value=2.0, key="dash_vf")
            ima = st.number_input("Current (mA):", value=10.0, key="dash_i")
            st.success(f"**Resistor = {(vs-vf)/(ima/1000):.1f} Ω**")

st.divider()

# ==============================================================================
# SECTION B: PROJECT GENERATOR INPUTS
# ==============================================================================
st.subheader("🚀 Generate 3D-Style PCB Layout, Schematic, Wiring & Code")
project_idea = st.text_area(
    "మీ ప్రాజెక్ట్ ఐడియా రాయండి (ఉదా: PPG Heart Rate Sensor, Bio-Z, Temperature Probe):",
    value="Discrete PPG heart rate sensor using BPW34 photodiode, 525nm green LED, MCP6002 dual op-amp (Gain 100, 0.5Hz-40Hz filter, 1.65V bias) for ESP32-C3.",
    height=80
)

col1, col2 = st.columns(2)
with col1:
    mcu_type = st.selectbox("Controller:", ["ESP32-C3 (3.3V)", "ESP32 DevKit (3.3V)", "Arduino Uno (5V)", "RP2040 Pico (3.3V)"])
with col2:
    pcb_size = st.selectbox("PCB Form Factor:", ["Smart Ring Flex/Mini PCB (18mm x 12mm)", "Standard Prototype PCB (50mm x 30mm)", "Breadboard Module"])

# ==============================================================================
# HELPER: 3D-STYLE REALISTIC PCB RENDERER (MATPLOTLIB)
# ==============================================================================
def render_3d_pcb_view(title_text, pcb_dim_label):
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    fig.patch.set_facecolor('#12161f')
    ax.set_facecolor('#12161f')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 58)
    ax.axis('off')

    # 3D Extrusion Shadow (PCB థిక్‌నెస్ / 3D ఎఫెక్ట్ కోసం)
    shadow = patches.FancyBboxPatch((7.5, 5.5), 86, 44, boxstyle="round,pad=1.5", facecolor='#072915', edgecolor='#041a0d', linewidth=2)
    ax.add_patch(shadow)
    board_edge = patches.FancyBboxPatch((6.8, 6.2), 86, 44, boxstyle="round,pad=1.5", facecolor='#1e4620', edgecolor='#0f2b12', linewidth=1.5)
    ax.add_patch(board_edge)

    # Main Green Soldermask PCB Top Layer
    pcb = patches.FancyBboxPatch((6, 7), 86, 44, boxstyle="round,pad=1.5", facecolor='#0d6e36', edgecolor='#d4af37', linewidth=2.5)
    ax.add_patch(pcb)

    # Gold Mounting Holes (4 Corners)
    for hx, hy in [(9, 10), (89, 10), (9, 48), (89, 48)]:
        ax.add_patch(patches.Circle((hx, hy), 2.1, facecolor='#d4af37', edgecolor='#8a6d1b', linewidth=1))
        ax.add_patch(patches.Circle((hx, hy), 1.0, facecolor='#12161f'))

    # Copper PCB Traces (3D Gold/Light-Green Tracks)
    traces = [
        ([18, 28, 28, 42], [35, 35, 31, 31], '#199c4f', 3.5),
        ([18, 25, 25, 42], [23, 23, 27, 27], '#199c4f', 3.5),
        ([54, 65, 65, 76], [31, 31, 35, 35], '#199c4f', 3.5),
        ([54, 68, 68, 76], [27, 27, 22, 22], '#199c4f', 3.5),
        ([15, 83], [14, 14], '#23b55e', 4.5), # GND Plane Bus
        ([15, 83], [44, 44], '#d4af37', 3.0), # 3.3V Power Bus
    ]
    for tx, ty, col, lw in traces:
        ax.plot(tx, ty, color=col, linewidth=lw, solid_capstyle='round', zorder=2)

    # Optical Isolation Barrier (3D Printed Black Resin Wall between LED & Photodiode)
    barrier = patches.Rectangle((22.5, 19), 2.2, 20, facecolor='#1a1a1a', edgecolor='#555555', linewidth=1.2, zorder=5)
    ax.add_patch(barrier)
    ax.text(23.6, 40.2, "0.8mm 3D Barrier", color='#ffcc00', fontsize=7, ha='center', fontweight='bold', zorder=6)

    # Component 1: LED (525nm Green)
    ax.add_patch(patches.Rectangle((14, 32), 6, 6, facecolor='#222222', edgecolor='#d4af37', lw=1.5, zorder=4))
    ax.add_patch(patches.Circle((17, 35), 2.0, facecolor='#00ff66', edgecolor='white', lw=0.8, zorder=5))
    ax.text(17, 29.8, "LED1\n(525nm)", color='white', fontsize=7.5, ha='center', fontweight='bold')

    # Component 2: Photodiode (BPW34 / TEMD5010)
    ax.add_patch(patches.Rectangle((14, 20), 6, 6, facecolor='#1c2833', edgecolor='#d4af37', lw=1.5, zorder=4))
    ax.add_patch(patches.Rectangle((15.2, 21.2), 3.6, 3.6, facecolor='#2e4053', edgecolor='#85c1e9', lw=0.8, zorder=5))
    ax.text(17, 17.5, "PD1\n(BPW34)", color='white', fontsize=7.5, ha='center', fontweight='bold')

    # Component 3: Main IC (MCP6002 SOIC-8 3D Chip Package)
    ic_x, ic_y, ic_w, ic_h = 42, 22, 12, 14
    # Gold IC Leads (Pins 1-4 Left, Pins 5-8 Right)
    for idx in range(4):
        py = ic_y + 1.5 + idx * 3.3
        ax.add_patch(patches.Rectangle((ic_x - 2.2, py), 2.2, 1.4, facecolor='#d4af37', zorder=3))
        ax.add_patch(patches.Rectangle((ic_x + ic_w, py), 2.2, 1.4, facecolor='#d4af37', zorder=3))
        ax.text(ic_x - 3.0, py + 0.5, f"P{4-idx}", color='#ffd700', fontsize=6.5, ha='right', va='center', fontweight='bold')
        ax.text(ic_x + ic_w + 3.0, py + 0.5, f"P{5+idx}", color='#ffd700', fontsize=6.5, ha='left', va='center', fontweight='bold')
    # IC Black Epoxy Body
    ax.add_patch(patches.FancyBboxPatch((ic_x, ic_y), ic_w, ic_h, boxstyle="round,pad=0.3", facecolor='#1c1c1c', edgecolor='#777777', lw=1.5, zorder=4))
    ax.add_patch(patches.Circle((ic_x + 2, ic_y + ic_h - 2), 0.7, facecolor='#888888', zorder=5)) # Pin 1 Dot
    ax.text(ic_x + ic_w/2, ic_y + ic_h/2, "U1\nMCP6002\n(SOIC-8)", color='white', fontsize=8, ha='center', va='center', fontweight='bold', zorder=5)

    # SMD Resistors & Capacitors (0805 Packages with Silver Solder Caps)
    smd_parts = [
        (31, 33, "R1\n100kΩ", '#111111'),
        (31, 21, "C1\n100nF", '#8d5524'),
        (61, 33, "Rf\n100kΩ", '#111111'),
        (61, 21, "Cf\n39nF", '#8d5524'),
    ]
    for sx, sy, slabel, scol in smd_parts:
        ax.add_patch(patches.Rectangle((sx-0.8, sy), 1.0, 2.6, facecolor='#cccccc', zorder=4))
        ax.add_patch(patches.Rectangle((sx+3.8, sy), 1.0, 2.6, facecolor='#cccccc', zorder=4))
        ax.add_patch(patches.Rectangle((sx, sy), 4.0, 2.6, facecolor=scol, edgecolor='#444444', lw=0.8, zorder=5))
        ax.text(sx+2.0, sy-2.8, slabel, color='white', fontsize=7, ha='center', fontweight='bold')

    # Output Header Pins (3D Gold Header Connector to MCU)
    ax.add_patch(patches.Rectangle((75, 19), 9, 20, facecolor='#1a1a1a', edgecolor='#d4af37', lw=1.5, zorder=4))
    header_labels = ["3.3V", "ADC_OUT", "LED_PWM", "GND"]
    for h_i, h_lbl in enumerate(header_labels):
        hy = 35 - h_i * 4.3
        ax.add_patch(patches.Circle((77.5, hy), 1.3, facecolor='#d4af37', edgecolor='white', lw=0.8, zorder=5))
        ax.text(80, hy, h_lbl, color='#00ffcc', fontsize=7, va='center', fontweight='bold', zorder=6)

    # Silkscreen Header Title
    ax.text(49, 53.5, f"3D PCB TOP VIEW: {title_text[:45]} | {pcb_dim_label}", color='#00ffcc', fontsize=10, ha='center', fontweight='bold')
    ax.text(49, 2.5, "FR-4 1.6mm • ENIG Gold Finish • 0.8mm 3D Optical Barrier • 100nF Decoupling", color='#aaaaaa', fontsize=8, ha='center')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf

# ==============================================================================
# ENGINE: SINGLE-CALL ULTRA FAST AI (GEMINI + GROQ BACKUP)
# ==============================================================================
def call_groq_backup(api_key, prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    data = json.dumps({"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.2}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))["choices"][0]["message"]["content"]

def run_instant_engine(gem_key, grq_key, prompt):
    if gem_key:
        client = genai.Client(api_key=gem_key)
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
                if any(x in str(e) for x in ["503", "UNAVAILABLE", "429"]):
                    time.sleep(1.5)
                    continue
                break
    if grq_key:
        try:
            return call_groq_backup(grq_key, prompt), "Groq Instant Backup"
        except Exception as e:
            st.error(f"Backup Error: {e}")
    st.error("⚠️ సర్వర్ రద్దీగా ఉంది. సైడ్‌బార్‌లో Groq కీ ఇవ్వండి లేదా 20 సెకన్ల తర్వాత మళ్ళీ నొక్కండి.")
    st.stop()

def sanitize_schemdraw(code):
    for bad in ["elm.Output()", "elm.Input()", "elm.Terminal()", "elm.Port()"]:
        code = code.replace(bad, "elm.Dot()")
    return code.replace("d.draw()", "").replace("plt.show()", "").strip()

if st.button("⚡ Build 3D PCB + Schematic + Full Design", type="primary"):
    if not gemini_key and not groq_key:
        st.error("⚠️ దయచేసి ఎడమవైపు సైడ్‌బార్‌లో మీ API Key ఇవ్వండి.")
    else:
        with st.spinner("⚡ 3D PCB Layout, Circuit Schematic, BOM, Wiring & ESP32 Code సిద్ధమవుతున్నాయి..."):
            prompt = f"""
            You are a Senior Biomedical Hardware & PCB Design Engineer.
            Project: {project_idea} | MCU: {mcu_type} | PCB: {pcb_size}

            Generate the COMPLETE output in ONE response with these exact 5 markers:
            ===TAB1===
            (In simple Telugu with English technical terms: 1. Circuit Architecture & Working, 2. Exact BOM Table with Part Numbers, Values, Qty, Role, Price in ₹, 3. Verified Datasheet Pinout Table.)

            ===TAB2===
            (In Telugu: Step-by-step math calculations for every Resistor, Capacitor, Gain, Cut-off Frequency Hz, LED Resistor + 3D Printed Optical Barrier & PCB Layout tips.)

            ===TAB3===
            (Write ONLY valid Python `schemdraw` code inside ```python ... ``` to draw the circuit schematic. Rules: `d = schemdraw.Drawing(show=False)`, use ONLY `elm.Resistor()`, `elm.Capacitor()`, `elm.Opamp()`, `elm.Ground()`, `elm.Vdd()`, `elm.Dot()`, `elm.Line()`, `elm.LED()`, `elm.Diode()`, `elm.SourceV()`. Never use `elm.Output()`. Save to `buf`:
            buf = io.BytesIO()
            d.save(buf, format='png', dpi=300)
            buf.seek(0)
            )

            ===TAB4===
            (In Telugu: Step-by-step Breadboard / PCB Soldering Guide with exact pin numbers, Multimeter test voltages, and LTspice .cir netlist.)

            ===TAB5===
            (Complete non-blocking Arduino C++ code using micros() for {mcu_type} with ADC to mV conversion, 1650mV offset removal, digital filter, Serial Plotter output + Telugu upload guide.)
            """
            raw_out, engine_used = run_instant_engine(gemini_key, groq_key, prompt)
            st.toast(f"✅ పూర్తయింది! Engine: {engine_used}")

        def get_part(text, s, e=None):
            if s not in text: return ""
            sub = text.split(s)[1]
            return sub.split(e)[0].strip() if (e and e in sub) else sub.strip()

        t1_txt = get_part(raw_out, "===TAB1===", "===TAB2===")
        t2_txt = get_part(raw_out, "===TAB2===", "===TAB3===")
        t3_raw = get_part(raw_out, "===TAB3===", "===TAB4===")
        t4_txt = get_part(raw_out, "===TAB4===", "===TAB5===")
        t5_txt = get_part(raw_out, "===TAB5===")

        tab_pcb, tab_sch, tab1, tab2, tab4, tab5 = st.tabs([
            "🟩 3D PCB Layout (బోర్డు బొమ్మ)",
            "📐 Circuit Schematic (సర్క్యూట్)",
            "📦 కాంపోనెంట్లు & Datasheet",
            "🧮 ఫార్ములాలు & లెక్కలు",
            "🔌 వైరింగ్ & టెస్ట్",
            "💻 ESP32 C++ కోడ్"
        ])

        # TAB 1: 3D PCB LAYOUT VIEW
        with tab_pcb:
            st.subheader("🟩 3D-Style PCB Top View & 3D-Printed Optical Barrier Layout")
            pcb_img = render_3d_pcb_view(project_idea, pcb_size)
            st.image(pcb_img, caption="3D PCB Layout with Gold Pads, Copper Traces & 0.8mm 3D Optical Isolation Barrier", use_container_width=True)
            st.download_button("⬇️ 3D PCB Layout డౌన్‌లోడ్ (PNG)", data=pcb_img, file_name="3d_pcb_layout.png", mime="image/png")

        # TAB 2: SCHEMATIC DIAGRAM
        with tab_sch:
            match = re.search(r"```python\n(.*?)\n```", t3_raw, re.DOTALL)
            py_code = sanitize_schemdraw(match.group(1) if match else t3_raw.replace("```python", "").replace("```", ""))
            try:
                env = {"schemdraw": schemdraw, "elm": elm, "plt": plt, "io": io}
                exec(py_code, env)
                if "buf" in env:
                    st.image(env["buf"], caption="Circuit Schematic Diagram", use_container_width=True)
                    st.download_button("⬇️ Schematic డౌన్‌లోడ్ (PNG)", data=env["buf"], file_name="schematic.png", mime="image/png")
                else:
                    st.code(py_code, language="python")
            except Exception as err:
                st.warning(f"Schematic సింటాక్స్ వివరాలు ({err}):")
                st.code(py_code, language="python")

        with tab1: st.markdown(t1_txt)
        with tab2: st.markdown(t2_txt)
        with tab4: st.markdown(t4_txt)
        with tab5: st.markdown(t5_txt)
