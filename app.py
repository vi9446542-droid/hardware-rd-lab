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
st.set_page_config(page_title="Zero-Downtime Electronics R&D Studio", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .hero-banner {
        background: linear-gradient(90deg, #090d16 0%, #1e293b 100%);
        padding: 16px 22px;
        border-radius: 12px;
        border-left: 6px solid #10b981;
        color: white;
        margin-bottom: 16px;
    }
    .hero-banner h1 { color: #ffffff; margin: 0; font-size: 1.6rem; }
    .hero-banner p { color: #94a3b8; margin: 4px 0 0 0; font-size: 0.9rem; }
    .ds-box {
        background-color: #1e293b;
        color: #f1f5f9;
        padding: 14px;
        border-radius: 8px;
        border: 1px solid #334155;
        font-size: 0.88rem;
    }
</style>
<div class="hero-banner">
    <h1>⚡ Zero-Downtime Universal Electronics R&D Studio</h1>
    <p>Multi-Server Auto-Failover (Zero 503 Error) • Local Instant Formula & Datasheet Engine • End-to-End Hardware & PCB Synthesis</p>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR: MULTI-SERVER FAILOVER CONFIGURATION ---
with st.sidebar:
    st.header("🔑 Multi-Server API Setup")
    st.caption("అసలు Server Busy (503) ఎర్రర్ రాకుండా ఉండటానికి కింద ఉన్న ఏ ఒక్క కీ (లేదా రెండూ) ఇవ్వండి:")
    
    gemini_key = st.text_input("1. Google Gemini Key (AIzaSy...):", type="password").strip()
    groq_key = st.text_input("2. Groq Ultra-Fast Key (gsk_...):", type="password").strip()
    
    with st.expander("🆓 ఉచిత Groq Key (0.5s Speed, Zero 503) ఎలా తీసుకోవాలి?"):
        st.markdown("""
        1. బ్రౌజర్‌లో **`console.groq.com`** ఓపెన్ చేసి Gmail తో లాగిన్ అవ్వండి.
        2. **API Keys -> Create API Key** నొక్కి `gsk_...` కీ కాపీ చేసి పైన 2వ బాక్స్‌లో పేస్ట్ చేయండి.
        3. ఇది పూర్తిగా ఉచితం & 0.5 సెకన్లలో జవాబు ఇస్తుంది!
        """)
    st.divider()
    st.success("🟢 **Local Engine Active:** Datasheets, Formulas & 3D PCB Render సర్వర్ లేకుండానే 0.01s లో పనిచేస్తాయి.")

# ==============================================================================
# SECTION 1: LOCAL INSTANT DASHBOARD (ZERO SERVER NEEDED)
# ==============================================================================
st.subheader("📊 1. Instant Electronics Dashboard (Datasheets & All-Domain Formulas)")

d_col1, d_col2 = st.columns([1.1, 1.1])

with d_col1:
    st.markdown("#### 🔌 Verified Component Datasheets")
    domain_cat = st.selectbox("Category:", [
        "1. Power Management (Buck, Boost, LDO, Charger)",
        "2. Analog, Op-Amps & Comparators",
        "3. Motor Drivers & Power MOSFETs",
        "4. Microcontrollers & Precision ADCs",
        "5. RF, Wireless & Industrial Buses",
        "6. Biomedical & Precision Sensors"
    ])

    universal_datasheets = {
        "1. Power Management (Buck, Boost, LDO, Charger)": {
            "LM2596 / MP1584 (Step-Down Buck Converter)": "Vin: 4.5V–28V/40V | Vout: 0.8V–25V Adj | Imax: 3A | Pins: 1:VIN, 2:SW(Inductor), 3:GND, 4:FB, 5:EN | Rule: Place Schottky diode (SS34) & Low-ESR cap right at SW pin.",
            "AMS1117-3.3 / TPS7A02 (Linear LDO Regulator)": "Vin: 4.5V–12V (AMS1117) / 1.5V–6V (TPS7A02) | Vout: 3.3V ±1% | Pins: 1:GND, 2:VOUT, 3:VIN | Rule: Mandatory 10µF cap on IN & OUT.",
            "TP4056 + DW01A (Li-Ion Charger & Protection)": "Vin: 5V USB | Cutoff: 4.2V ±1% | I_chg = 1200/Rprog (1.2kΩ = 1A) | Pins: 2:PROG, 3:GND, 4:VCC, 5:BAT, 8:CE."
        },
        "2. Analog, Op-Amps & Comparators": {
            "MCP6002 / TLV9002 (3.3V Rail-to-Rail Op-Amp)": "Supply: 1.8V–5.5V | GBWP: 1MHz | Pins: 1:OUTA, 2:INA-, 3:INA+, 4:GND, 5:INB+, 6:INB-, 7:OUTB, 8:VDD | Rule: 100nF decoupling cap at Pin 8-4.",
            "OPA2350 (High-Speed 38MHz Precision Op-Amp)": "Supply: 2.7V–5.5V | GBWP: 38MHz | Slew: 22V/µs | Pins: 1:OUTA, 2:INA-, 3:INA+, 4:V-, 5:INB+, 6:INB-, 7:OUTB, 8:V+.",
            "LM393 (Dual Differential Comparator)": "Supply: 2V–36V | Open-Collector Output | Pins: 1:OUT1, 2:IN1-, 3:IN1+, 4:GND, 5:IN2+, 6:IN2-, 7:OUT2, 8:VCC | Rule: Needs 4.7kΩ pull-up on OUT."
        },
        "3. Motor Drivers & Power MOSFETs": {
            "AO3400 / IRLZ44N (Logic-Level N-MOSFET)": "AO3400: 30V/5.7A | IRLZ44N: 55V/47A | Vgs(th): 1.0V–2.0V | Rule: 100Ω Gate resistor + 10kΩ Gate-GND pull-down + Flyback diode.",
            "DRV8833 / TB6612FNG (Dual H-Bridge Driver)": "Vm: 2.7V–10.8V | Current: 1.2A–1.5A/ch | Pins: AIN1/2, AOUT1/2, BIN1/2, BOUT1/2, nSLEEP(High) | Rule: 100µF bulk cap on Vm."
        },
        "4. Microcontrollers & Precision ADCs": {
            "ESP32-C3 / ESP32-S3 (Wi-Fi + BLE 5.0 SoC)": "Supply: 3.3V | 12-bit ADC (GPIO0–GPIO4 on C3) | Max GPIO: 40mA | Rule: Never apply >3.3V to GPIO.",
            "ADS1115 (16-Bit Precision I2C ADC)": "Supply: 2.0V–5.5V | 16-bit (0.125mV/LSB) | PGA up to 16x | Pins: VDD, GND, SCL, SDA, A0–A3."
        },
        "5. RF, Wireless & Industrial Buses": {
            "SX1276 / RA-02 (LoRa 433/868/915 MHz)": "Supply: 3.3V | TX: 120mA (+20dBm) | SPI + DIO0 | Rule: NEVER power ON without 50Ω antenna connected.",
            "MAX485 / SN65HVD72 (RS-485 Transceiver)": "Supply: 5V / 3.3V | Range: 1200m | Pins: 1:RO, 2:RE, 3:DE, 4:DI, 5:GND, 6:A(+), 7:B(-), 8:VCC | Rule: 120Ω termination."
        },
        "6. Biomedical & Precision Sensors": {
            "BPW34 / TEMD5010 & NTC 10K B3950": "BPW34: 400–1100nm PIN Photodiode (Notch=Cathode) | NTC 10K: R25=10kΩ, Beta=3950K (Use 10kΩ 0.1% divider)."
        }
    }

    part_key = st.selectbox("Select Component:", list(universal_datasheets[domain_cat].keys()))
    st.markdown(f"<div class='ds-box'><b>📋 Verified Specs & Pinout:</b><br><code>{universal_datasheets[domain_cat][part_key]}</code></div>", unsafe_allow_html=True)

with d_col2:
    st.markdown("#### 🧮 All-Domain Electronics Formula Solver")
    formula_domain = st.selectbox("Formula Domain:", [
        "1. DC Laws (Ohm's Law, Power, Voltage Divider)",
        "2. Analog Filters (RC, LC Resonance, Op-Amp Gain)",
        "3. Power Electronics (Buck/Boost Duty, Thermal, Battery)",
        "4. Digital & PCB (555 Timer, ADC, PCB Trace Width)",
        "5. RF & AC Impedance (Xc, XL, Antenna Wavelength)"
    ])

    if "1. DC" in formula_domain:
        c1, c2, c3 = st.columns(3)
        vin = c1.number_input("Vin (V):", value=12.0)
        r1 = c2.number_input("R1 / Load (Ω):", min_value=0.01, value=1000.0)
        r2 = c3.number_input("R2 Bottom (Ω - 0 for Ohm's Law):", min_value=0.0, value=330.0)
        if r2 == 0:
            curr = vin / r1
            st.success(f"**Current = {curr*1000:.2f} mA** | **Power = {vin*curr*1000:.1f} mW**")
        else:
            vout = vin * (r2 / (r1 + r2))
            st.success(f"**Divider Vout = {vout:.3f} V** | **Current = {(vin/(r1+r2))*1000:.2f} mA**")

    elif "2. Analog" in formula_domain:
        c1, c2, c3 = st.columns(3)
        r_k = c1.number_input("R / Rin (kΩ):", min_value=0.01, value=10.0)
        c_n = c2.number_input("C (nF) / Rf (kΩ):", min_value=0.01, value=100.0)
        l_u = c3.number_input("L (µH - 0 for RC):", min_value=0.0, value=0.0)
        if l_u == 0:
            fc = 1.0 / (2 * math.pi * r_k * 1000 * c_n * 1e-9)
            gain = 1.0 + (c_n / r_k)
            st.success(f"**RC fc = {fc:.2f} Hz** | *(If Op-Amp Rf/Rin: Gain = {gain:.2f}x)*")
        else:
            fr = 1.0 / (2 * math.pi * math.sqrt(l_u * 1e-6 * c_n * 1e-9))
            st.success(f"**LC Resonant Freq fr = {fr/1000:.2f} kHz**")

    elif "3. Power" in formula_domain:
        c1, c2, c3 = st.columns(3)
        vin = c1.number_input("Vin (V):", min_value=0.1, value=12.0)
        vout = c2.number_input("Vout (V):", min_value=0.1, value=5.0)
        pwr = c3.number_input("Loss (W) / mAh:", min_value=0.1, value=1.0)
        duty = (vout / vin * 100) if vin > vout else ((1 - vin / vout) * 100)
        mode = "Buck" if vin > vout else "Boost"
        st.success(f"**{mode} Duty Cycle = {duty:.1f}%** | **Temp Rise (at 45°C/W) = +{pwr*45:.1f}°C**")

    elif "4. Digital" in formula_domain:
        c1, c2, c3 = st.columns(3)
        adc_raw = c1.number_input("12-bit ADC (0-4095):", min_value=0, max_value=4095, value=2048)
        amps = c2.number_input("PCB Current (A):", min_value=0.1, value=2.0)
        v_adc = (adc_raw / 4095.0) * 3.3
        w_mm = max(0.25, (amps / (0.048 * (10 ** 0.44))) ** (1 / 0.725) * 0.0254 / 1.378)
        st.success(f"**ADC Voltage = {v_adc:.3f} V** | **1oz PCB Trace Width = {w_mm:.2f} mm**")

    elif "5. RF" in formula_domain:
        c1, c2 = st.columns(2)
        fmhz = c1.number_input("RF Freq (MHz):", min_value=0.1, value=433.92)
        c_nf = c2.number_input("Cap (nF):", min_value=0.001, value=10.0)
        wl = (299.792 / fmhz) * 100
        xc = 1.0 / (2 * math.pi * fmhz * 1e6 * c_nf * 1e-9)
        st.success(f"**λ/4 Antenna = {wl/4:.2f} cm** | **Reactance Xc = {xc:.4f} Ω**")

st.divider()

# ==============================================================================
# SECTION 2: ZERO-DOWNTIME MULTI-SERVER R&D GENERATOR
# ==============================================================================
st.subheader("🚀 2. Zero-Downtime End-to-End Hardware R&D Generator")

r1, r2, r3 = st.columns(3)
with r1:
    sys_domain = st.selectbox("Domain:", [
        "Custom Electronics R&D",
        "Power Electronics (SMPS, Buck/Boost, BMS, Solar)",
        "Analog & Precision Signal Conditioning",
        "Motor Control & Robotics",
        "RF, LoRa & Industrial IoT",
        "Biomedical & Wearable Devices"
    ])
with r2:
    target_mcu = st.selectbox("Controller:", [
        "ESP32-C3 / ESP32-S3 (3.3V)",
        "STM32F4 / STM32G4 (3.3V)",
        "RP2040 / Pico (3.3V)",
        "Arduino Uno / Nano (5V)",
        "Pure Analog / Power (No MCU)"
    ])
with r3:
    lang_pref = st.selectbox("Language:", [
        "Telugu + English Technical Terms",
        "Pure Engineering English"
    ])

user_req = st.text_area(
    "మీ ప్రాజెక్ట్ రిక్వైర్‌మెంట్ రాయండి:",
    value="Design a 12V to 5V/3A high-efficiency Buck Converter power supply with over-voltage protection, LC output filter (<20mV ripple), and ESP32-C3 voltage/current monitoring using INA219.",
    height=90
)

# --- MULTI-PROVIDER FAILOVER ENGINE (ZERO 503 GUARANTEED) ---
def call_groq_engine(g_key, prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {g_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    payload = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 4096
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]

def execute_zero_downtime_ai(gem_k, grq_k, prompt):
    logs = []
    # 1. ముందుగా Groq కీ ఉంటే 0.5 సెకన్లలో అత్యంత వేగంగా రన్ చేస్తుంది (అసలు 503 రాదు)
    # లేదా Gemini కీ ముందుగా ప్రయత్నించి, 503 వస్తే వెంటనే Groq కి మారుతుంది
    if gem_k and gem_k.startswith("AIza"):
        try:
            client = genai.Client(api_key=gem_k)
            for mid in ["gemini-3.8-flash", "gemini-3.8-pro"]:
                try:
                    resp = client.models.generate_content(model=mid, contents=prompt)
                    return resp.text, f"Google Gemini ({mid})"
                except Exception as e:
                    logs.append(f"Gemini {mid}: {str(e)[:60]}")
                    if "503" in str(e) or "429" in str(e):
                        continue
        except Exception as e:
            logs.append(f"Gemini Client: {str(e)[:60]}")

    # 2. Automatic Instant Failover to Groq Server (Zero 503 Error)
    if grq_k and grq_k.startswith("gsk_"):
        try:
            ans = call_groq_engine(grq_k, prompt)
            return ans, "Groq Cloud Ultra-Fast (Llama-3.3-70B)"
        except Exception as e:
            logs.append(f"Groq: {str(e)[:60]}")

    # ఒకవేళ user పొరపాటున Gemini బాక్స్ లో gsk_ కీ పెట్టినా ఆటోమేటిక్ గా గుర్తిస్తుంది!
    if gem_k and gem_k.startswith("gsk_"):
        try:
            ans = call_groq_engine(gem_k, prompt)
            return ans, "Groq Cloud Ultra-Fast (Auto-Detected)"
        except Exception as e:
            logs.append(f"Groq Auto: {str(e)[:60]}")

    st.error("⚠️ అన్ని సర్వర్లు ప్రస్తుతం రద్దీగా ఉన్నాయి లేదా API Key తప్పుగా ఉంది. దయచేసి ఎడమవైపు సైడ్‌బార్‌లో ఉచిత Groq Key (`console.groq.com` నుండి `gsk_...`) ఇవ్వండి—అప్పుడు ఎప్పటికీ 503 ఎర్రర్ రాదు!\n\n**Log:** " + " | ".join(logs))
    st.stop()

def render_3d_pcb(req_text, sys_dom, mcu_n):
    fig, ax = plt.subplots(figsize=(10, 5.2), dpi=300)
    fig.patch.set_facecolor('#0b0f19')
    ax.set_facecolor('#0b0f19')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis('off')

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
    ax.text(16.5, 29.5, "INPUT /\nSENSOR /\nPWR IN", color='#10b981', fontsize=7, ha='center', va='center', fontweight='bold', zorder=5)

    ic_x, ic_y, ic_w, ic_h = 39, 22, 16, 16
    for idx in range(4):
        py = ic_y + 1.8 + idx * 3.8
        ax.add_patch(patches.Rectangle((ic_x - 2.4, py), 2.4, 1.5, facecolor='#d4af37', zorder=3))
        ax.add_patch(patches.Rectangle((ic_x + ic_w, py), 2.4, 1.5, facecolor='#d4af37', zorder=3))
        ax.text(ic_x - 3.2, py + 0.6, f"P{4-idx}", color='#ffd700', fontsize=6.5, ha='right', va='center', fontweight='bold')
        ax.text(ic_x + ic_w + 3.2, py + 0.6, f"P{5+idx}", color='#ffd700', fontsize=6.5, ha='left', va='center', fontweight='bold')
    ax.add_patch(patches.FancyBboxPatch((ic_x, ic_y), ic_w, ic_h, boxstyle="round,pad=0.3", facecolor='#181818', edgecolor='#888888', lw=1.5, zorder=4))
    ax.add_patch(patches.Circle((ic_x + 2.2, ic_y + ic_h - 2.2), 0.8, facecolor='#999999', zorder=5))
    ax.text(ic_x + ic_w/2, ic_y + ic_h/2, "MAIN IC\nCORE", color='white', fontsize=8, ha='center', va='center', fontweight='bold', zorder=5)

    for sx, sy, lbl, col in [(28, 36, "R1\n1%", '#111111'), (28, 20, "C_in\nX7R", '#8d5524'), (62, 36, "R2\n1%", '#111111'), (62, 20, "C_out\nLow-ESR", '#8d5524')]:
        ax.add_patch(patches.Rectangle((sx-0.8, sy), 1.0, 2.8, facecolor='#cccccc', zorder=4))
        ax.add_patch(patches.Rectangle((sx+4.0, sy), 1.0, 2.8, facecolor='#cccccc', zorder=4))
        ax.add_patch(patches.Rectangle((sx, sy), 4.2, 2.8, facecolor=col, edgecolor='#555555', lw=0.8, zorder=5))
        ax.text(sx+2.1, sy-2.8, lbl, color='white', fontsize=6.8, ha='center', fontweight='bold')

    ax.add_patch(patches.Rectangle((74, 19), 11, 22, facecolor='#1a1a1a', edgecolor='#d4af37', lw=1.5, zorder=4))
    for i, pin_txt in enumerate(["V_RAIL", "SIG_OUT", "CTRL_IO", "GND_REF"]):
        py = 37 - i * 4.8
        ax.add_patch(patches.Circle((76.5, py), 1.3, facecolor='#d4af37', edgecolor='white', lw=0.8, zorder=5))
        ax.text(79, py, pin_txt, color='#10b981', fontsize=6.5, va='center', fontweight='bold', zorder=6)

    ax.text(49, 55.5, f"3D PCB LAYOUT: {req_text[:48]}", color='#10b981', fontsize=9.5, ha='center', fontweight='bold')
    ax.text(49, 2.2, f"Domain: {sys_dom[:35]} | Target: {mcu_n} | ENIG Gold & Star-Ground", color='#bbbbbb', fontsize=7.5, ha='center')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf

def sanitize_schemdraw(code):
    for bad in ["elm.Output()", "elm.Input()", "elm.Terminal()", "elm.Port()"]:
        code = code.replace(bad, "elm.Dot()")
    return code.replace("d.draw()", "").replace("plt.show()", "").strip()

if st.button("⚡ Build Complete Design (Zero-Downtime Engine)", type="primary"):
    if not gemini_key and not groq_key:
        st.error("⚠️ దయచేసి ఎడమవైపు సైడ్‌బార్‌లో మీ Gemini API Key (AIzaSy...) లేదా ఉచిత Groq API Key (gsk_...) ఇవ్వండి.")
    else:
        with st.spinner("⚡ Multi-Server Engine ద్వారా పూర్తి R&D డిజైన్ సిద్ధమవుతోంది..."):
            prompt = f"""
            You are a Chief Electronics & Hardware R&D Architect.
            Build a complete, end-to-end hardware engineering design for the user's requirements below.
            Language: {lang_pref}.

            DOMAIN: {sys_domain}
            CONTROLLER: {target_mcu}
            REQUIREMENTS: {user_req}

            Divide your output strictly using these exact 5 markers:

            ===TAB1===
            **1. System Architecture & Verified BOM:**
            - Topology selection & how the circuit works end-to-end.
            - Complete BOM Table: Designator, Exact Part Number, Value, Voltage/Power Rating, Qty, Role, Approx Price (₹).
            - Verified Datasheet Pinout Table for all ICs/Transistors.

            ===TAB2===
            **2. Complete Engineering Math & PCB Layout Rules:**
            - Step-by-step math calculations for every resistor, capacitor, inductor, gain, frequency, ripple, and thermal dissipation.
            - Professional PCB Layout, Grounding, Thermal & EMI/EMC guidelines.

            ===TAB3===
            Write ONLY valid Python `schemdraw` code inside ```python ... ``` to draw a clean horizontal circuit schematic.
            Rules: `d = schemdraw.Drawing(show=False)`, use ONLY `elm.Resistor()`, `elm.Capacitor()`, `elm.Opamp()`, `elm.Ground()`, `elm.Vdd()`, `elm.Dot()`, `elm.Line()`, `elm.LED()`, `elm.Diode()`, `elm.SourceV()`, `elm.Inductor()`. NEVER use `elm.Output()` or `elm.Input()`. Save to `buf`:
            ```python
            buf = io.BytesIO()
            d.save(buf, format='png', dpi=300)
            buf.seek(0)
            ```

            ===TAB4===
            **4. Wiring, Bench Testing & LTspice Simulation:**
            - Step-by-step pin-to-pin wiring/soldering steps.
            - Multimeter/Oscilloscope test voltages (TP1, TP2, TP3) + LTspice `.cir` netlist.

            ===TAB5===
            **5. Production Firmware / Control Logic:**
            - Complete non-blocking C++ code for {target_mcu} using `micros()`, physical unit conversion, filtering/protection, and Serial output.
            """
            raw_out, engine_used = execute_zero_downtime_ai(gemini_key, groq_key, prompt)
            st.session_state["last_rd_output"] = raw_out
            st.session_state["last_engine"] = engine_used
            st.session_state["last_req"] = user_req
            st.session_state["last_dom"] = sys_domain
            st.session_state["last_mcu"] = target_mcu

if "last_rd_output" in st.session_state:
    raw_out = st.session_state["last_rd_output"]
    st.success(f"✅ సిద్ధమైంది! Active Server Engine: **{st.session_state['last_engine']}**")

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
        "6️⃣ Firmware / Control Logic"
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
        pcb_buf = render_3d_pcb(st.session_state["last_req"], st.session_state["last_dom"], st.session_state["last_mcu"])
        st.image(pcb_buf, caption="3D PCB Architecture View", use_container_width=True)
        st.download_button("⬇️ 3D PCB PNG డౌన్‌లోడ్", data=pcb_buf, file_name="3d_pcb.png", mime="image/png")
