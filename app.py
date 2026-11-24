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

# 1. ప్రొఫెషనల్ పేజీ సెటప్ & కస్టమ్ UI స్టైలింగ్
st.set_page_config(page_title="APEX Hardware R&D Studio", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%);
        padding: 18px 24px;
        border-radius: 12px;
        border-left: 6px solid #00e5ff;
        color: white;
        margin-bottom: 20px;
    }
    .main-header h1 { color: #ffffff; margin: 0; font-size: 1.7rem; }
    .main-header p { color: #94a3b8; margin: 4px 0 0 0; font-size: 0.95rem; }
    .spec-card {
        background-color: #1e293b;
        color: #f8fafc;
        padding: 14px;
        border-radius: 8px;
        border: 1px solid #334155;
        font-size: 0.9rem;
    }
</style>
<div class="main-header">
    <h1>⚡ APEX Universal Electronics & Hardware R&D Studio</h1>
    <p>World-Class End-to-End Hardware Architecture • Component Datasheets • Worst-Case Math • Schematic & 3D PCB • Production Firmware</p>
</div>
""", unsafe_allow_html=True)

# 2. సైడ్‌బార్: క్లీన్ API సెటప్
with st.sidebar:
    st.header("🔑 System Configuration")
    gemini_key = st.text_input("Gemini API Key (AIzaSy...):", type="password").strip()
    st.caption("మీ Gemini API Key ఇక్కడ పేస్ట్ చేయండి.")
    st.divider()
    st.markdown("""
    **🛠️ Platform Capabilities:**
    - ✅ **Zero-Upload Datasheets:** 15+ Core ICs & Sensors Built-in
    - ✅ **Live Formula Workbench:** RC, Op-Amp, Power, RF, ADC
    - ✅ **Principal R&D Engine:** Any Electronics Domain
    - ✅ **Auto Schematic & 3D PCB:** Visual Hardware Layouts
    """)

# ==============================================================================
# SECTION 1: PRO ENGINEERING DASHBOARD (DATASHEETS & FORMULAS - ALWAYS VISIBLE)
# ==============================================================================
st.subheader("📊 1. Principal Engineering Dashboard (Datasheets & Formula Workbench)")

dash_col1, dash_col2 = st.columns([1.15, 1])

with dash_col1:
    st.markdown("#### 🔌 Component Datasheet & Pinout Explorer")
    comp_cat = st.selectbox("Select Component Category:", [
        "Analog & Precision Op-Amps",
        "Sensors & Transducers (Optical, Temp, Bio-Z, Piezo)",
        "Microcontrollers & ADCs",
        "Power Management & MOSFET Drivers"
    ])

    datasheet_library = {
        "Analog & Precision Op-Amps": {
            "MCP6002 (Dual 3.3V Rail-to-Rail Op-Amp)": {
                "Supply & Power": "1.8V to 6.0V Single Supply | Quiescent Current: 100µA/ch",
                "Key Specs": "GBWP: 1 MHz | Slew Rate: 0.6 V/µs | Input Bias: 1 pA (CMOS) | Rail-to-Rail I/O",
                "Pinout (8-Pin DIP/SOIC)": "Pin 1: OUTA | Pin 2: INA- | Pin 3: INA+ | Pin 4: VSS (GND) | Pin 5: INB+ | Pin 6: INB- | Pin 7: OUTB | Pin 8: VDD (+3.3V)",
                "Design Rule": "Always place 100nF ceramic capacitor between Pin 8 & Pin 4. Bias IN+ to 1.65V for AC signals."
            },
            "OPA2350 (High-Speed 38MHz Precision Op-Amp)": {
                "Supply & Power": "2.7V to 5.5V | Quiescent Current: 5.2 mA/ch",
                "Key Specs": "GBWP: 38 MHz | Slew Rate: 22 V/µs | Noise: 5 nV/√Hz | Ideal for 50kHz–250kHz Bio-Z / Ultrasonic",
                "Pinout (8-Pin SOIC)": "Pin 1: OUTA | Pin 2: INA- | Pin 3: INA+ | Pin 4: V- (GND) | Pin 5: INB+ | Pin 6: INB- | Pin 7: OUTB | Pin 8: V+ (+3.3V/5V)",
                "Design Rule": "Use 0.1µF + 10µF decoupling right at Pin 8 to prevent high-frequency oscillation."
            },
            "INA128 / AD8421 (Instrumentation Amplifier)": {
                "Supply & Power": "±2.25V to ±18V (or 5V single supply with Vref=2.5V)",
                "Key Specs": "CMRR: >110 dB | Gain Equation: G = 1 + (50kΩ / Rg) for INA128 | Low Drift: 0.5 µV/°C",
                "Pinout (8-Pin)": "Pin 1: -IN | Pin 2: Rg1 | Pin 3: Rg2 | Pin 4: +IN | Pin 5: V- | Pin 6: REF | Pin 7: VOUT | Pin 8: V+",
                "Design Rule": "Drive Pin 6 (REF) with a low-impedance Op-Amp buffer (never a raw resistor divider)."
            }
        },
        "Sensors & Transducers (Optical, Temp, Bio-Z, Piezo)": {
            "BPW34 / TEMD5010X01 (Silicon PIN Photodiode)": {
                "Supply & Power": "Photovoltaic (0V bias) for lowest noise, or 3.3V Reverse Bias for high speed",
                "Key Specs": "Spectral Range: 400nm–1100nm (Peak 850nm) | Active Area: 7.5 mm² | Dark Current: 2 nA",
                "Pinout": "Anode (+) -> Op-Amp Inverting Input (IN-) | Cathode (-) [Notch/Tab side] -> Vbias (+1.65V or +3.3V)",
                "Design Rule": "Use 0.8mm opaque optical barrier between LED & PD to block direct light leakage."
            },
            "NTC 10K B3950 (0.5mm Glass Micro-Bead Thermistor)": {
                "Supply & Power": "3.3V Excitation via 10kΩ (±0.1%) Precision Metal-Film Resistor",
                "Key Specs": "R25 = 10,000Ω at 25°C | Beta (25/50) = 3950K | Thermal Time Constant: < 0.8 sec",
                "Pinout": "2-Wire Non-Polarized: Wire 1 -> 3.3V (via 10kΩ 0.1% resistor) | Wire 2 -> GND | Mid-node -> 100nF C0G cap & ADC",
                "Design Rule": "Keep excitation current < 165µA to avoid self-heating error (<0.01°C)."
            },
            "PZT-5A Piezoelectric Disc (5mm, 2.0–2.5 MHz)": {
                "Supply & Power": "Pulse-Echo Excitation (3.3V–15V burst) or Passive Acoustic Charge Mode",
                "Key Specs": "Resonant Freq: 2.0–2.5 MHz | High Coupling Coefficient k33 | Requires Tungsten-Epoxy Backing",
                "Pinout": "Top Silver Electrode -> Signal / Charge Amp | Bottom Wrap-Around Electrode -> Shield GND",
                "Design Rule": "Use quarter-wavelength acoustic matching layer + ultrasonic gel for skin coupling."
            }
        },
        "Microcontrollers & ADCs": {
            "ESP32-C3 (RISC-V Wi-Fi + BLE 5.0 MCU)": {
                "Supply & Power": "3.0V to 3.6V (3.3V Nominal) | Peak Wi-Fi TX Current: 330mA",
                "Key Specs": "12-bit SAR ADC (0–4095) | 160 MHz CPU | Hardware PWM (LEDC), I2C, SPI, UART",
                "Pinout": "ADC1 Channels: GPIO0, GPIO1, GPIO2, GPIO3, GPIO4 | 3V3: Regulated Out | GND: Ground",
                "Design Rule": "Avoid ADC2 pins when Wi-Fi is active; use GPIO0–GPIO4 with 100nF anti-aliasing cap."
            },
            "ADS1115 (16-Bit Precision Delta-Sigma ADC)": {
                "Supply & Power": "2.0V to 5.5V | Current: 150µA",
                "Key Specs": "16-bit Resolution (0.125 mV/bit) | Programmable Gain Amp (PGA up to 16x) | I2C Interface",
                "Pinout": "VDD: 3.3V | GND: GND | SCL/SDA: I2C Bus (4.7kΩ pull-ups) | A0–A3: Differential/Single Analog Inputs",
                "Design Rule": "Ideal when 12-bit MCU ADC is insufficient for microvolt physiological signals."
            }
        },
        "Power Management & MOSFET Drivers": {
            "2N7002 / AO3400 (Logic-Level N-Channel MOSFET)": {
                "Supply & Power": "Vds Max: 30V–60V | Vgs(th): 1.0V–2.1V (Fully turns ON at 3.3V GPIO)",
                "Key Specs": "AO3400 Rds(on): 26mΩ (5.7A) | 2N7002 Rds(on): 2Ω (115mA)",
                "Pinout (SOT-23)": "Pin 1 (Left): Gate -> MCU GPIO (via 100Ω) | Pin 2 (Right): Source -> GND | Pin 3 (Top): Drain -> Load (-)",
                "Design Rule": "Always add 10kΩ pull-down resistor from Gate to GND so load stays OFF during MCU boot."
            },
            "TPS7A02 / AMS1117-3.3 (Low-Noise LDO Regulator)": {
                "Supply & Power": "Vin: 3.6V–6.0V (TPS7A02) or 4.5V–12V (AMS1117) -> Vout: 3.3V",
                "Key Specs": "TPS7A02 Iq: 25 nA (Ultra-low power wearables) | High PSRR for clean analog rails",
                "Pinout": "IN: Battery/USB (+) | GND: Common Ground | OUT: Clean 3.3V Analog/Digital Rail",
                "Design Rule": "Place 10µF X7R ceramic capacitor on both IN and OUT pins within 3mm of IC."
            }
        }
    }

    selected_part = st.selectbox("Select Specific Part:", list(datasheet_library[comp_cat].keys()))
    p_info = datasheet_library[comp_cat][selected_part]
    st.markdown(f"""
    <div class="spec-card">
        <b>⚡ Supply & Power:</b> {p_info['Supply & Power']}<br>
        <b>📊 Electrical Specs:</b> {p_info['Key Specs']}<br>
        <b>📍 Verified Pinout:</b> <code>{p_info['Pinout']}</code><br>
        <b>🛡️ Senior Design Rule:</b> {p_info['Design Rule']}
    </div>
    """, unsafe_allow_html=True)

with dash_col2:
    st.markdown("#### 🧮 Complete Electronics Formula & Math Engine")
    formula_choice = st.selectbox("Select Engineering Formula:", [
        "1. RC Low-Pass / High-Pass Filter (fc = 1 / 2πRC)",
        "2. Op-Amp Gain (Non-Inverting & Inverting)",
        "3. Voltage Divider & Mid-Rail Bias (Vout)",
        "4. LED / Load Current Resistor & Wattage",
        "5. Capacitive Reactance (Xc = 1 / 2πfC)",
        "6. ADC Resolution & Voltage Converter (12-bit / 16-bit)"
    ])

    if "1. RC" in formula_choice:
        c_a, c_b = st.columns(2)
        r_k = c_a.number_input("Resistor R (kΩ):", min_value=0.001, value=39.0)
        c_n = c_b.number_input("Capacitor C (nF):", min_value=0.001, value=100.0)
        fc = 1.0 / (2 * math.pi * (r_k * 1000) * (c_n * 1e-9))
        st.success(f"**Cut-off Frequency ($f_c$) = {fc:.2f} Hz** (Time Constant $\\tau$ = {r_k*c_n/1000:.2f} ms)")

    elif "2. Op-Amp" in formula_choice:
        c_a, c_b, c_c = st.columns(3)
        rin = c_a.number_input("Rin (kΩ):", min_value=0.01, value=1.0)
        rf = c_b.number_input("Rf (kΩ):", min_value=0.01, value=99.0)
        vin_mv = c_c.number_input("Vin (mV):", min_value=0.1, value=10.0)
        gain_ni = 1.0 + (rf / rin)
        st.success(f"**Non-Inverting Gain = {gain_ni:.2f}x** | **Vout = {vin_mv * gain_ni:.1f} mV**")

    elif "3. Voltage Divider" in formula_choice:
        c_a, c_b, c_c = st.columns(3)
        vin = c_a.number_input("Vin (V):", min_value=0.1, value=3.3)
        r1 = c_b.number_input("R1 Top (kΩ):", min_value=0.01, value=10.0)
        r2 = c_c.number_input("R2 Bottom (kΩ):", min_value=0.01, value=10.0)
        vout = vin * (r2 / (r1 + r2))
        st.success(f"**Vout = {vout:.3f} V** | **Divider Current = {(vin/(r1+r2))*1000:.1f} µA**")

    elif "4. LED" in formula_choice:
        c_a, c_b, c_c = st.columns(3)
        vs = c_a.number_input("Supply (V):", min_value=0.5, value=3.3)
        vf = c_b.number_input("LED Vf (V):", min_value=0.1, value=2.0)
        ima = c_c.number_input("Current (mA):", min_value=0.1, value=15.0)
        if vs > vf:
            r_ohms = (vs - vf) / (ima / 1000.0)
            p_mw = (vs - vf) * ima
            st.success(f"**Resistor = {r_ohms:.1f} Ω** | **Power = {p_mw:.1f} mW**")
        else:
            st.error("Supply must be > Vf")

    elif "5. Capacitive" in formula_choice:
        c_a, c_b = st.columns(2)
        f_khz = c_a.number_input("Frequency (kHz):", min_value=0.001, value=50.0)
        c_nf = c_b.number_input("Capacitor (nF):", min_value=0.001, value=10.0)
        xc = 1.0 / (2 * math.pi * (f_khz * 1000) * (c_nf * 1e-9))
        st.success(f"**Reactance ($X_c$) = {xc:.2f} Ω**")

    elif "6. ADC" in formula_choice:
        c_a, c_b, c_c = st.columns(3)
        bits = c_a.selectbox("ADC Bits:", [12, 16, 10, 24])
        vref = c_b.number_input("Vref (V):", value=3.3)
        raw_val = c_c.number_input("Raw ADC Value:", min_value=0, value=2048)
        max_cnt = (2 ** bits) - 1
        lsb_mv = (vref * 1000.0) / max_cnt
        meas_v = (raw_val / max_cnt) * vref
        st.success(f"**Voltage = {meas_v:.4f} V** | **1 LSB = {lsb_mv:.4f} mV**")

st.divider()

# ==============================================================================
# SECTION 2: END-TO-END WORLD-CLASS R&D GENERATOR
# ==============================================================================
st.subheader("🚀 2. End-to-End Principal R&D Project Generator")

col1, col2, col3 = st.columns(3)
with col1:
    rd_domain = st.selectbox("Engineering Domain:", [
        "Any Custom Electronics R&D",
        "Biomedical & Wearable Sensors (PPG, ECG, Bio-Z, EDA)",
        "Power Electronics (SMPS, Buck/Boost, BMS, Solar)",
        "Precision Analog & Instrumentation",
        "Robotics, BLDC Motor Control & Actuators",
        "RF, Wireless & Industrial IoT",
        "High-Fidelity Audio & Active DSP"
    ])
with col2:
    mcu_choice = st.selectbox("Target Controller:", [
        "ESP32-C3 / ESP32-S3 (3.3V, 12-bit ADC)",
        "STM32F4 / STM32G4 (3.3V, 12/16-bit ADC)",
        "RP2040 / Raspberry Pi Pico (3.3V)",
        "Arduino Uno / Nano (5V, 10-bit ADC)",
        "Pure Analog Hardware (No MCU)"
    ])
with col3:
    output_lang = st.selectbox("Explanation Language:", [
        "Telugu + English Technical Terms (తెలుగులో స్పష్టంగా)",
        "Pure International Engineering English"
    ])

project_prompt = st.text_area(
    "మీరు నిర్మించాలనుకుంటున్న ఎలక్ట్రానిక్ ప్రాజెక్ట్ వివరాలు రాయండి (ఏ రకమైన ప్రాజెక్ట్ అయినా సరే):",
    value="Design a discrete multi-wavelength PPG & Bio-Impedance analog front-end using MCP6002 & OPA2350 op-amps, BPW34 photodiode, 1.65V precision mid-rail bias, and 0.5Hz–40Hz active bandpass filter for ESP32-C3.",
    height=90
)

# ==============================================================================
# BULLETPROOF AI ENGINE (DIRECT GEMINI-3.8-FLASH FIRST + SMART RETRY)
# ==============================================================================
def call_bulletproof_ai(api_key, prompt):
    client = genai.Client(api_key=api_key)
    # స్క్రీన్‌షాట్ ప్రకారం ప్రస్తుత లైవ్ మోడల్ gemini-3.8-flash కి మొదటి ప్రాధాన్యత
    priority_models = ["gemini-3.8-flash", "gemini-3.8-pro"]
    
    # అదనంగా పనిచేసే ఇతర మోడల్స్ ఉంటే జత చేస్తుంది (పాత 2.5 లేదా image మోడల్స్ వదిలేస్తుంది)
    try:
        for m in client.models.list():
            m_name = m.name.replace("models/", "")
            if ("3.8" in m_name or "3.5" in m_name or "3.0" in m_name) and "image" not in m_name and m_name not in priority_models:
                priority_models.append(m_name)
    except Exception:
        pass

    last_err = ""
    for model_id in priority_models:
        for attempt in range(3): # 503 బిజీ వస్తే 3 సార్లు ఆగి మళ్ళీ ప్రయత్నిస్తుంది
            try:
                response = client.models.generate_content(
                    model=model_id,
                    contents=prompt
                )
                return response.text, model_id
            except Exception as e:
                last_err = str(e)
                if "503" in last_err or "UNAVAILABLE" in last_err or "429" in last_err:
                    time.sleep(3)
                    continue
                else:
                    break

    st.error(f"⚠️ Google API సర్వర్ ప్రస్తుతం రద్దీగా ఉంది. దయచేసి 15 సెకన్ల తర్వాత మళ్ళీ బటన్ నొక్కండి.\n\n**Log:** {last_err}")
    st.stop()

# ==============================================================================
# 3D PCB LAYOUT & SCHEMATIC RENDERERS
# ==============================================================================
def render_3d_pcb(proj_title, domain_name, mcu_name):
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    fig.patch.set_facecolor('#0b0f19')
    ax.set_facecolor('#0b0f19')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis('off')

    # 3D Substrate Depth & Gold Edge
    ax.add_patch(patches.FancyBboxPatch((7.5, 5.5), 86, 46, boxstyle="round,pad=1.5", facecolor='#041f10', edgecolor='#021008', lw=2))
    ax.add_patch(patches.FancyBboxPatch((6.8, 6.2), 86, 46, boxstyle="round,pad=1.5", facecolor='#114b29', edgecolor='#082614', lw=1.5))
    ax.add_patch(patches.FancyBboxPatch((6, 7), 86, 46, boxstyle="round,pad=1.5", facecolor='#0a6130', edgecolor='#d4af37', lw=2.5))

    for hx, hy in [(9, 10), (89, 10), (9, 50), (89, 50)]:
        ax.add_patch(patches.Circle((hx, hy), 2.0, facecolor='#d4af37', edgecolor='#7d6014', lw=1))
        ax.add_patch(patches.Circle((hx, hy), 0.9, facecolor='#0b0f19'))

    ax.plot([14, 84], [46, 46], color='#d4af37', lw=3.2, zorder=2)
    ax.plot([14, 84], [13, 13], color='#22b560', lw=4.5, zorder=2)
    for tx, ty in [([21, 38], [36, 33]), ([21, 38], [23, 27]), ([56, 74], [33, 36]), ([56, 74], [27, 23])]:
        ax.plot(tx, ty, color='#1ca354', lw=3.0, zorder=2)

    ax.add_patch(patches.Rectangle((12, 20), 9, 19, facecolor='#1c2430', edgecolor='#d4af37', lw=1.5, zorder=4))
    ax.text(16.5, 29.5, "SENSOR /\nINPUT\nSTAGE", color='#00e5ff', fontsize=7, ha='center', va='center', fontweight='bold', zorder=5)

    ic_x, ic_y, ic_w, ic_h = 39, 22, 16, 16
    for idx in range(4):
        py = ic_y + 1.8 + idx * 3.8
        ax.add_patch(patches.Rectangle((ic_x - 2.4, py), 2.4, 1.5, facecolor='#d4af37', zorder=3))
        ax.add_patch(patches.Rectangle((ic_x + ic_w, py), 2.4, 1.5, facecolor='#d4af37', zorder=3))
        ax.text(ic_x - 3.2, py + 0.6, f"P{4-idx}", color='#ffd700', fontsize=6.5, ha='right', va='center', fontweight='bold')
        ax.text(ic_x + ic_w + 3.2, py + 0.6, f"P{5+idx}", color='#ffd700', fontsize=6.5, ha='left', va='center', fontweight='bold')
    ax.add_patch(patches.FancyBboxPatch((ic_x, ic_y), ic_w, ic_h, boxstyle="round,pad=0.3", facecolor='#181818', edgecolor='#888888', lw=1.5, zorder=4))
    ax.add_patch(patches.Circle((ic_x + 2.2, ic_y + ic_h - 2.2), 0.8, facecolor='#999999', zorder=5))
    ax.text(ic_x + ic_w/2, ic_y + ic_h/2, "ANALOG /\nPOWER IC\nCORE", color='white', fontsize=8, ha='center', va='center', fontweight='bold', zorder=5)

    for sx, sy, lbl, col in [(28, 36, "R_in\n0.1%", '#111111'), (28, 20, "C_flt\nC0G", '#8d5524'), (62, 36, "R_fb\n0.1%", '#111111'), (62, 20, "C_dec\n100nF", '#8d5524')]:
        ax.add_patch(patches.Rectangle((sx-0.8, sy), 1.0, 2.8, facecolor='#cccccc', zorder=4))
        ax.add_patch(patches.Rectangle((sx+4.0, sy), 1.0, 2.8, facecolor='#cccccc', zorder=4))
        ax.add_patch(patches.Rectangle((sx, sy), 4.2, 2.8, facecolor=col, edgecolor='#555555', lw=0.8, zorder=5))
        ax.text(sx+2.1, sy-2.8, lbl, color='white', fontsize=6.8, ha='center', fontweight='bold')

    ax.add_patch(patches.Rectangle((74, 19), 11, 22, facecolor='#1a1a1a', edgecolor='#d4af37', lw=1.5, zorder=4))
    for i, pin_txt in enumerate(["VCC_3V3", "ADC_SIG", "CTRL_IO", "GND_REF"]):
        py = 37 - i * 4.8
        ax.add_patch(patches.Circle((76.5, py), 1.3, facecolor='#d4af37', edgecolor='white', lw=0.8, zorder=5))
        ax.text(79, py, pin_txt, color='#00e5ff', fontsize=6.5, va='center', fontweight='bold', zorder=6)

    ax.text(49, 55.5, f"3D PCB ARCHITECTURE: {proj_title[:48]}", color='#00e5ff', fontsize=9.5, ha='center', fontweight='bold')
    ax.text(49, 2.2, f"Domain: {domain_name} | Controller: {mcu_name} | ENIG Gold Finish & Star-Ground", color='#bbbbbb', fontsize=7.5, ha='center')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf

def sanitize_schemdraw(code):
    for bad in ["elm.Output()", "elm.Input()", "elm.Terminal()", "elm.Port()"]:
        code = code.replace(bad, "elm.Dot()")
    return code.replace("d.draw()", "").replace("plt.show()", "").strip()

if st.button("⚡ Build Complete World-Class Hardware Design", type="primary"):
    if not gemini_key:
        st.error("⚠️ దయచేసి ఎడమవైపు సైడ్‌బార్‌లో మీ Gemini API Key పేస్ట్ చేయండి.")
    else:
        with st.spinner("🧠 Principal Electronics Architect పూర్తి R&D డిజైన్, లెక్కలు, Schematic & కోడ్ సిద్ధం చేస్తోంది..."):
            master_prompt = f"""
            You are a Chief Electronics & Hardware R&D Architect (30+ years experience).
            Build a complete, end-to-end, industry-grade hardware engineering package for the project below.
            Language preference: {output_lang}.

            DOMAIN: {rd_domain}
            PROJECT: {project_prompt}
            TARGET MCU: {mcu_choice}

            Output strictly divided into these 5 markers:

            ===TAB1===
            **1. End-to-End System Architecture & Verified BOM:**
            - First-principles physics & block-by-block signal/power flow explanation.
            - Complete BOM Table: Designator, Exact Part Number, Value, Tolerance/Dielectric (e.g., 0.1% Thin Film, C0G/NP0), Qty, Role, Approx Price (₹).
            - Verified Datasheet Pinout & Electrical Limits Table for every IC & Sensor.

            ===TAB2===
            **2. Complete Engineering Math & Worst-Case Tolerance Analysis:**
            - Exact step-by-step calculations for every resistor, capacitor, gain stage, cut-off frequency ($f_c$), power dissipation, and ADC resolution.
            - Worst-case error budget + Professional PCB Layout / EMI-EMC rules (Star Ground, Guard Rings, Decoupling).

            ===TAB3===
            Write ONLY valid Python `schemdraw` code inside ```python ... ``` to draw a clean horizontal circuit schematic.
            Rules: `d = schemdraw.Drawing(show=False)`, use ONLY `elm.Resistor()`, `elm.Capacitor()`, `elm.Opamp()`, `elm.Ground()`, `elm.Vdd()`, `elm.Dot()`, `elm.Line()`, `elm.LED()`, `elm.Diode()`, `elm.SourceV()`, `elm.Inductor()`. NEVER use `elm.Output()` or `elm.Input()`. Save to `buf`:
            ```python
            buf = io.BytesIO()
            d.save(buf, format='png', dpi=300)
            buf.seek(0)
            ```

            ===TAB4===
            **4. Assembly, Bench Testing & LTspice Simulation:**
            - Pin-by-pin Breadboard/PCB wiring steps.
            - Multimeter & Oscilloscope test checkpoints (TP1, TP2, TP3 expected voltages).
            - Complete runnable LTspice `.cir` netlist.

            ===TAB5===
            **5. Production Embedded C++ Firmware & Digital Signal Processing:**
            - Non-blocking C++ code for {mcu_choice} using `micros()`, physical unit conversion, digital filtering, and Serial Plotter output + upload guide.
            """
            raw_out, used_model = call_bulletproof_ai(gemini_key, master_prompt)
            st.toast(f"✅ పూర్తయింది! Model: {used_model}")

        def get_sec(txt, s, e=None):
            if s not in txt: return ""
            sub = txt.split(s)[1]
            return sub.split(e)[0].strip() if (e and e in sub) else sub.strip()

        t1_data = get_sec(raw_out, "===TAB1===", "===TAB2===")
        t2_data = get_sec(raw_out, "===TAB2===", "===TAB3===")
        t3_raw  = get_sec(raw_out, "===TAB3===", "===TAB4===")
        t4_data = get_sec(raw_out, "===TAB4===", "===TAB5===")
        t5_data = get_sec(raw_out, "===TAB5===")

        tabs = st.tabs([
            "1️⃣ Architecture & BOM",
            "2️⃣ End-to-End Math & PCB Rules",
            "3️⃣ Circuit Schematic (బొమ్మ)",
            "4️⃣ 3D PCB Layout (బోర్డు)",
            "5️⃣ Bench Test & LTspice",
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
                    st.image(env["buf"], caption="Circuit Schematic Diagram", use_container_width=True)
                    st.download_button("⬇️ Schematic PNG డౌన్‌లోడ్", data=env["buf"], file_name="schematic.png", mime="image/png")
                else:
                    st.code(py_code, language="python")
            except Exception as err:
                st.warning(f"Schematic కోడ్ వివరాలు ({err}):")
                st.code(py_code, language="python")

        with tabs[3]:
            pcb_buf = render_3d_pcb(project_prompt, rd_domain, mcu_choice)
            st.image(pcb_buf, caption="3D PCB Architecture (ENIG Gold Pads, Star-Ground & Guard-Ring)", use_container_width=True)
            st.download_button("⬇️ 3D PCB PNG డౌన్‌లోడ్", data=pcb_buf, file_name="3d_pcb.png", mime="image/png")
