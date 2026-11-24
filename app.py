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

# పేజీ సెటప్ & ప్రొఫెషనల్ UI
st.set_page_config(page_title="Universal Electronics R&D Studio", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .hero-banner {
        background: linear-gradient(90deg, #0b1120 0%, #1e293b 100%);
        padding: 18px 24px;
        border-radius: 12px;
        border-left: 6px solid #38bdf8;
        color: white;
        margin-bottom: 18px;
    }
    .hero-banner h1 { color: #ffffff; margin: 0; font-size: 1.65rem; }
    .hero-banner p { color: #94a3b8; margin: 5px 0 0 0; font-size: 0.92rem; }
    .ds-box {
        background-color: #1e293b;
        color: #f1f5f9;
        padding: 14px;
        border-radius: 8px;
        border: 1px solid #334155;
        font-size: 0.88rem;
        line-height: 1.5;
    }
</style>
<div class="hero-banner">
    <h1>⚡ Universal End-to-End Electronics & Hardware R&D Studio</h1>
    <p>All-Domain Electronics Formulas • Global Component Datasheets • Requirement-Driven Circuit, PCB & Firmware Synthesis</p>
</div>
""", unsafe_allow_html=True)

# సైడ్‌బార్
with st.sidebar:
    st.header("🔑 API Configuration")
    gemini_key = st.text_input("Gemini API Key (AIzaSy...):", type="password").strip()
    st.caption("మీ Gemini API Key ఇక్కడ పేస్ట్ చేయండి.")
    st.divider()
    st.markdown("""
    **🌐 Universal R&D Capabilities:**
    - **All-Domain Formulas:** DC, Analog, Power/SMPS, Thermal, RF, Timing & Digital
    - **Global Datasheet Vault:** Power ICs, Op-Amps, Drivers, MCUs, RF & Sensors
    - **Custom Design Engine:** మీ రిక్వైర్‌మెంట్‌కు తగ్గట్టుగా A-to-Z హార్డ్‌వేర్ డిజైన్
    """)

# ==============================================================================
# SECTION 1: UNIVERSAL ELECTRONICS DASHBOARD (ALL FORMULAS & DATASHEETS)
# ==============================================================================
st.subheader("📊 1. Universal Electronics Dashboard (Datasheets & All-Domain Formula Engine)")

d_col1, d_col2 = st.columns([1.1, 1.1])

# --- LEFT: UNIVERSAL COMPONENT & DATASHEET EXPLORER ---
with d_col1:
    st.markdown("#### 🔌 Global Component & Datasheet Library")
    domain_cat = st.selectbox("Select Electronics Category:", [
        "1. Power Management & Converters (Buck, Boost, LDO, BMS)",
        "2. Analog, Op-Amps & Comparators",
        "3. Motor Drivers, MOSFETs & Relays",
        "4. Microcontrollers, Memory & ADCs",
        "5. RF, Wireless & Communication Transceivers",
        "6. Industrial & Biomedical Sensors"
    ])

    universal_datasheets = {
        "1. Power Management & Converters (Buck, Boost, LDO, BMS)": {
            "LM2596 / MP1584 (Step-Down Buck Converter IC)": {
                "Ratings": "Vin: 4.5V–28V (MP1584) / 40V (LM2596) | Vout: 0.8V–25V Adj | Max Current: 3A",
                "Pinout": "Pin 1: VIN | Pin 2: SW (Inductor Output) | Pin 3: GND | Pin 4: FB (Feedback 0.8V/1.23V) | Pin 5: EN",
                "Critical Rule": "Use Low-ESR ceramic caps + Schottky diode (SS34) close to SW pin to prevent voltage spikes."
            },
            "AMS1117-3.3 / TPS7A02 (Linear LDO Regulator)": {
                "Ratings": "Vin: 4.5V–12V (AMS1117) / 1.5V–6V (TPS7A02) | Vout: 3.3V ±1% | Dropout: 1.1V vs 100mV",
                "Pinout": "Pin 1: GND | Pin 2: VOUT (Tab) | Pin 3: VIN",
                "Critical Rule": "Mandatory 10µF capacitor on IN and OUT pins for loop stability."
            },
            "TP4056 + DW01A (1S Li-Ion Charger & Protection)": {
                "Ratings": "Input: 4.5V–5.5V USB | Charge Cutoff: 4.2V ±1% | Prog Current: I = 1200 / R_prog",
                "Pinout": "Pin 2: PROG (1.2kΩ = 1A) | Pin 3: GND | Pin 4: VCC | Pin 5: BAT | Pin 8: CE",
                "Critical Rule": "Add thermal via stitching under IC; it dissipates heat at 1A charging."
            }
        },
        "2. Analog, Op-Amps & Comparators": {
            "MCP6002 / TLV9002 (Low-Voltage Rail-to-Rail Op-Amp)": {
                "Ratings": "Supply: 1.8V–5.5V | GBWP: 1 MHz | Input Bias: 1 pA | Rail-to-Rail I/O",
                "Pinout": "1:OUTA, 2:INA-, 3:INA+, 4:GND, 5:INB+, 6:INB-, 7:OUTB, 8:VDD",
                "Critical Rule": "Place 100nF ceramic decoupling cap within 2mm of Pin 8 & Pin 4."
            },
            "NE5532 / OPA2134 (Low-Noise Audio & Precision Op-Amp)": {
                "Ratings": "Supply: ±3V to ±18V | Noise: 5 nV/√Hz | Slew Rate: 9 V/µs | GBWP: 10 MHz",
                "Pinout": "1:OUTA, 2:INA-, 3:INA+, 4:V-, 5:INB+, 6:INB-, 7:OUTB, 8:V+",
                "Critical Rule": "Needs dual rail (±5V to ±15V) or mid-rail virtual ground for single supply."
            },
            "LM393 (Dual Differential Comparator - Open Collector)": {
                "Ratings": "Supply: 2V–36V | Response Time: 1.3µs | Output: Open-Collector (Needs Pull-up)",
                "Pinout": "1:OUT1, 2:IN1-, 3:IN1+, 4:GND, 5:IN2+, 6:IN2-, 7:OUT2, 8:VCC",
                "Critical Rule": "Output cannot drive HIGH by itself; MUST connect 4.7kΩ–10kΩ pull-up resistor to VCC."
            }
        },
        "3. Motor Drivers, MOSFETs & Relays": {
            "AO3400 / IRLZ44N (Logic-Level N-Channel Power MOSFET)": {
                "Ratings": "AO3400: 30V, 5.7A (SOT-23) | IRLZ44N: 55V, 47A (TO-220) | Vgs(th): 1.0V–2.0V",
                "Pinout": "1: Gate (via 100Ω to MCU) | 2: Drain (Load -) | 3: Source (GND) [Check SOT-23 vs TO-220]",
                "Critical Rule": "Always place 10kΩ Gate-to-GND resistor + Flyback Diode (1N4007/SS34) across inductive loads."
            },
            "DRV8833 / TB6612FNG (Dual H-Bridge DC/Stepper Driver)": {
                "Ratings": "Motor Supply Vm: 2.7V–10.8V | Logic: 3.3V/5V | Continuous Current: 1.2A–1.5A/ch",
                "Pinout": "AIN1/AIN2 (PWM/Dir), AOUT1/AOUT2 (Motor A), BIN1/BIN2, BOUT1/BOUT2, nSLEEP (Pull High)",
                "Critical Rule": "Add 100µF electrolytic bulk capacitor across Vm & GND to absorb motor back-EMF spikes."
            }
        },
        "4. Microcontrollers, Memory & ADCs": {
            "ESP32-C3 / ESP32-S3 (Wi-Fi + BLE 5.0 SoC)": {
                "Ratings": "Supply: 3.0V–3.6V | 12-bit ADC | Hardware PWM, I2C, SPI, UART, USB-JTAG",
                "Pinout": "3V3, GND, ADC1 (GPIO0–GPIO4), I2C (Any GPIO via matrix)",
                "Critical Rule": "Never feed >3.3V into any GPIO; use resistor divider or level shifter for 5V sensors."
            },
            "STM32F103 / STM32G4 (ARM Cortex-M3/M4 Industrial MCU)": {
                "Ratings": "Supply: 2.0V–3.6V (Many 5V-tolerant digital pins) | 12-bit 1MSPS+ ADC | Hardware Timers",
                "Pinout": "VDD/VSS pairs (all must be decoupled), PA0–PA7 (ADC), PB6/PB7 (I2C1), SWDIO/SWCLK",
                "Critical Rule": "Connect VDDA & VSSA through ferrite bead for clean analog ADC conversions."
            }
        },
        "5. RF, Wireless & Communication Transceivers": {
            "SX1276 / RA-02 (LoRa Long-Range Sub-GHz Transceiver)": {
                "Ratings": "Supply: 1.8V–3.7V | Freq: 433/868/915 MHz | TX Current: 120mA (+20dBm) | SPI Interface",
                "Pinout": "3.3V, GND, SCK, MISO, MOSI, NSS (CS), RST, DIO0 (Interrupt), ANT (50Ω)",
                "Critical Rule": "NEVER power ON or transmit without an antenna connected—reflected RF power destroys the PA."
            },
            "MAX485 / SN65HVD72 (RS-485 Industrial Differential Bus)": {
                "Ratings": "Supply: 5V (MAX485) / 3.3V (SN65HVD72) | Distance: up to 1200m | Half-Duplex",
                "Pinout": "1:RO (RX), 2:RE, 3:DE, 4:DI (TX), 5:GND, 6:A (+), 7:B (-), 8:VCC",
                "Critical Rule": "Place 120Ω termination resistor across A and B lines at both ends of long cables."
            }
        },
        "6. Industrial & Biomedical Sensors": {
            "BPW34 / TEMD5010 (PIN Photodiode) & NTC 10K B3950": {
                "Ratings": "BPW34: 400–1100nm, 2nA dark current | NTC 10K: R25=10kΩ, Beta=3950K",
                "Pinout": "BPW34: Cathode(Notch) to Vbias, Anode to TIA IN- | NTC: 10kΩ 0.1% divider to ADC",
                "Critical Rule": "Shield optical sensors from ambient 50/60Hz flicker; keep NTC current <150µA."
            }
        }
    }

    part_key = st.selectbox("Select Component Datasheet:", list(universal_datasheets[domain_cat].keys()))
    ds = universal_datasheets[domain_cat][part_key]
    st.markdown(f"""
    <div class="ds-box">
        <b>⚡ Electrical Ratings:</b> {ds['Ratings']}<br>
        <b>📍 Verified Pinout:</b> <code>{ds['Pinout']}</code><br>
        <b>🛡️ Engineering Design Rule:</b> {ds['Critical Rule']}
    </div>
    """, unsafe_allow_html=True)

# --- RIGHT: COMPLETE ALL-DOMAIN ELECTRONICS FORMULA ENGINE ---
with d_col2:
    st.markdown("#### 🧮 All-Domain Electronics Formula Solver")
    formula_domain = st.selectbox("Select Formula Domain:", [
        "A. Basic DC, Ohm's Law, Power & Dividers",
        "B. Analog Filters (RC / RL / LC Resonance) & Op-Amps",
        "C. Power Electronics (Buck/Boost SMPS, Battery & Thermal)",
        "D. Digital, 555 Timer, ADC & PCB Trace Current",
        "E. RF, Wavelength & Impedance (Xc / XL)"
    ])

    if "A. Basic DC" in formula_domain:
        sub_f = st.radio("Formula:", ["Ohm's Law & Power (V, I, R, P)", "Voltage Divider (Vout)", "Parallel Resistors (Req)"], horizontal=True)
        if "Ohm" in sub_f:
            c1, c2 = st.columns(2)
            v_in = c1.number_input("Voltage V (Volts):", value=12.0)
            r_in = c2.number_input("Resistance R (Ω):", min_value=0.001, value=470.0)
            curr = v_in / r_in
            pwr = v_in * curr
            st.success(f"**Current (I) = {curr*1000:.2f} mA** ({curr:.4f} A) | **Power (P) = {pwr*1000:.1f} mW** ({pwr:.3f} W)")
        elif "Divider" in sub_f:
            c1, c2, c3 = st.columns(3)
            vin = c1.number_input("Vin (V):", value=12.0)
            r1 = c2.number_input("R1 Top (kΩ):", min_value=0.01, value=10.0)
            r2 = c3.number_input("R2 Bottom (kΩ):", min_value=0.01, value=3.3)
            st.success(f"**Vout = {vin * (r2 / (r1 + r2)):.3f} V** | **Quiescent Current = {(vin/(r1+r2))*1000:.1f} µA**")
        else:
            c1, c2 = st.columns(2)
            ra = c1.number_input("R1 (Ω):", min_value=0.01, value=100.0)
            rb = c2.number_input("R2 (Ω):", min_value=0.01, value=100.0)
            st.success(f"**Equivalent R_parallel = {(ra*rb)/(ra+rb):.2f} Ω**")

    elif "B. Analog Filters" in formula_domain:
        sub_f = st.radio("Formula:", ["RC Cut-off (fc)", "LC Resonant Freq (fr)", "Op-Amp Gain"], horizontal=True)
        if "RC" in sub_f:
            c1, c2 = st.columns(2)
            r_k = c1.number_input("R (kΩ):", min_value=0.001, value=10.0)
            c_n = c2.number_input("C (nF):", min_value=0.001, value=100.0)
            st.success(f"**Cut-off fc = {1.0/(2*math.pi*r_k*1000*c_n*1e-9):.2f} Hz**")
        elif "LC" in sub_f:
            c1, c2 = st.columns(2)
            l_uh = c1.number_input("Inductor L (µH):", min_value=0.001, value=100.0)
            c_nf = c2.number_input("Capacitor C (nF):", min_value=0.001, value=10.0)
            fr = 1.0 / (2 * math.pi * math.sqrt((l_uh * 1e-6) * (c_nf * 1e-9)))
            st.success(f"**Resonant Frequency fr = {fr/1000:.2f} kHz** ({fr:.1f} Hz)")
        else:
            c1, c2 = st.columns(2)
            rin = c1.number_input("Rin (kΩ):", min_value=0.01, value=1.0)
            rf = c2.number_input("Rf (kΩ):", min_value=0.01, value=47.0)
            st.success(f"**Non-Inverting = {1 + rf/rin:.2f}x** | **Inverting = -{rf/rin:.2f}x**")

    elif "C. Power Electronics" in formula_domain:
        sub_f = st.radio("Formula:", ["Buck/Boost Duty Cycle", "Thermal Temp Rise", "Battery Runtime"], horizontal=True)
        if "Buck" in sub_f:
            c1, c2 = st.columns(2)
            vin = c1.number_input("Vin (V):", min_value=0.1, value=12.0)
            vout = c2.number_input("Vout (V):", min_value=0.1, value=5.0)
            if vin > vout:
                st.success(f"**Buck Mode Duty Cycle (D) = {(vout/vin)*100:.1f}%**")
            else:
                st.success(f"**Boost Mode Duty Cycle (D) = {(1 - vin/vout)*100:.1f}%**")
        elif "Thermal" in sub_f:
            c1, c2, c3 = st.columns(3)
            pwr_w = c1.number_input("Power Loss (W):", min_value=0.01, value=1.5)
            r_ja = c2.number_input("Thermal RθJA (°C/W):", min_value=1.0, value=45.0)
            t_amb = c3.number_input("Ambient Temp (°C):", value=30.0)
            t_j = t_amb + (pwr_w * r_ja)
            st.success(f"**Junction Temp (Tj) = {t_j:.1f} °C** (Rise: +{pwr_w*r_ja:.1f} °C)")
        else:
            c1, c2 = st.columns(2)
            mah = c1.number_input("Battery (mAh):", min_value=1.0, value=2000.0)
            load_ma = c2.number_input("Avg Load (mA):", min_value=0.1, value=50.0)
            st.success(f"**Estimated Runtime = {(mah/load_ma)*0.85:.1f} Hours** (with 85% efficiency factor)")

    elif "D. Digital, 555" in formula_domain:
        sub_f = st.radio("Formula:", ["555 Astable Timer", "ADC Voltage", "PCB Trace Width"], horizontal=True)
        if "555" in sub_f:
            c1, c2, c3 = st.columns(3)
            ra = c1.number_input("RA (kΩ):", min_value=0.1, value=10.0)
            rb = c2.number_input("RB (kΩ):", min_value=0.1, value=47.0)
            cap = c3.number_input("C (µF):", min_value=0.0001, value=0.1, format="%.4f")
            freq = 1.44 / (((ra + 2*rb) * 1000) * (cap * 1e-6))
            duty = ((ra + rb) / (ra + 2*rb)) * 100
            st.success(f"**Freq = {freq:.2f} Hz** | **Duty Cycle = {duty:.1f}%**")
        elif "ADC" in sub_f:
            c1, c2, c3 = st.columns(3)
            bits = c1.selectbox("Bits:", [12, 10, 16, 24])
            vref = c2.number_input("Vref (V):", value=3.3)
            raw = c3.number_input("Raw ADC:", min_value=0, value=2048)
            st.success(f"**Voltage = {(raw / ((2**bits)-1))*vref:.4f} V**")
        else:
            amps = st.number_input("Trace Current (Amps):", min_value=0.1, value=2.0)
            # IPC-2221 External Layer approx for 1oz copper, 10C rise
            width_mm = (amps / (0.048 * (10 ** 0.44))) ** (1 / 0.725) * 0.0254 / 1.378
            st.success(f"**Recommended 1oz PCB Trace Width (10°C rise) ≈ {max(0.25, width_mm):.2f} mm**")

    elif "E. RF, Wavelength" in formula_domain:
        sub_f = st.radio("Formula:", ["Reactance (Xc & XL)", "RF Wavelength (λ)"], horizontal=True)
        if "Reactance" in sub_f:
            c1, c2, c3 = st.columns(3)
            fk = c1.number_input("Freq (kHz):", min_value=0.001, value=100.0)
            cn = c2.number_input("C (nF):", min_value=0.001, value=10.0)
            lu = c3.number_input("L (µH):", min_value=0.001, value=100.0)
            xc = 1.0 / (2 * math.pi * fk * 1000 * cn * 1e-9)
            xl = 2 * math.pi * fk * 1000 * lu * 1e-6
            st.success(f"**Xc = {xc:.2f} Ω** | **XL = {xl:.2f} Ω**")
        else:
            fmhz = st.number_input("RF Frequency (MHz):", min_value=0.1, value=433.92)
            wl_cm = (299.792 / fmhz) * 100
            st.success(f"**Full Wavelength (λ) = {wl_cm:.2f} cm** | **Quarter-Wave Whip Antenna (λ/4) = {wl_cm/4:.2f} cm**")

st.divider()

# ==============================================================================
# SECTION 2: REQUIREMENT-ADAPTIVE END-TO-END R&D SYNTHESIS ENGINE
# ==============================================================================
st.subheader("🚀 2. Custom Requirement-Driven End-to-End Hardware R&D Generator")

r_col1, r_col2, r_col3 = st.columns(3)
with r_col1:
    system_type = st.selectbox("Project Domain / System Type:", [
        "Custom Requirement (Auto-Detect Domain)",
        "Power Electronics (Buck/Boost SMPS, BMS, Solar MPPT, Inverter)",
        "Analog & Signal Conditioning (Filters, Op-Amps, Bridges)",
        "Motor Control & Robotics (BLDC, Stepper, H-Bridge, Servo)",
        "RF, Wireless & Industrial Automation (LoRa, RS-485, CAN)",
        "Biomedical & Wearable Devices (PPG, ECG, Bio-Z, Temp)",
        "Audio & High-Speed Digital Hardware"
    ])
with r_col2:
    target_mcu = st.selectbox("Target Controller / Architecture:", [
        "ESP32-C3 / ESP32-S3 (3.3V, 12-bit ADC)",
        "STM32F4 / STM32G4 (3.3V ARM Cortex-M4)",
        "RP2040 / Raspberry Pi Pico (3.3V)",
        "Arduino Uno / Nano / ATmega328P (5V)",
        "Pure Analog / Power Hardware (No MCU Required)"
    ])
with r_col3:
    lang_mode = st.selectbox("Output Language:", [
        "Telugu + English Technical Terms (తెలుగులో స్పష్టంగా)",
        "International Engineering English"
    ])

user_requirements = st.text_area(
    "మీ పూర్తి ప్రాజెక్ట్ రిక్వైర్‌మెంట్ రాయండి (Input Voltage, Output Specs, Sensors/Loads, Accuracy, Budget మొదలైనవి):",
    value="Design a 12V to 5V/3A high-efficiency Buck Converter power supply with over-voltage protection, LC output filter (<20mV ripple), and ESP32-C3 voltage/current telemetry monitoring using INA219.",
    height=100
)

# Bulletproof AI Caller
def run_rd_synthesis(api_key, prompt):
    client = genai.Client(api_key=api_key)
    models_list = ["gemini-3.8-flash", "gemini-3.8-pro"]
    try:
        for m in client.models.list():
            m_name = m.name.replace("models/", "")
            if ("3.8" in m_name or "3.5" in m_name or "3.0" in m_name) and "image" not in m_name and m_name not in models_list:
                models_list.append(m_name)
    except Exception:
        pass

    last_err = ""
    for mid in models_list:
        for _ in range(3):
            try:
                resp = client.models.generate_content(model=mid, contents=prompt)
                return resp.text, mid
            except Exception as e:
                last_err = str(e)
                if any(code in last_err for code in ["503", "UNAVAILABLE", "429"]):
                    time.sleep(3)
                    continue
                break
    st.error(f"⚠️ సర్వర్ తాత్కాలికంగా రద్దీగా ఉంది. 15 సెకన్ల తర్వాత మళ్ళీ ప్రయత్నించండి.\n\nLog: {last_err}")
    st.stop()

def render_adaptive_3d_pcb(req_text, sys_domain, mcu_name):
    fig, ax = plt.subplots(figsize=(10, 5.4), dpi=300)
    fig.patch.set_facecolor('#0b0f19')
    ax.set_facecolor('#0b0f19')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis('off')

    # 3D Substrate & Gold Edge
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
    ax.text(16.5, 29.5, "INPUT /\nSENSOR /\nPWR IN", color='#38bdf8', fontsize=7, ha='center', va='center', fontweight='bold', zorder=5)

    ic_x, ic_y, ic_w, ic_h = 39, 22, 16, 16
    for idx in range(4):
        py = ic_y + 1.8 + idx * 3.8
        ax.add_patch(patches.Rectangle((ic_x - 2.4, py), 2.4, 1.5, facecolor='#d4af37', zorder=3))
        ax.add_patch(patches.Rectangle((ic_x + ic_w, py), 2.4, 1.5, facecolor='#d4af37', zorder=3))
        ax.text(ic_x - 3.2, py + 0.6, f"P{4-idx}", color='#ffd700', fontsize=6.5, ha='right', va='center', fontweight='bold')
        ax.text(ic_x + ic_w + 3.2, py + 0.6, f"P{5+idx}", color='#ffd700', fontsize=6.5, ha='left', va='center', fontweight='bold')
    ax.add_patch(patches.FancyBboxPatch((ic_x, ic_y), ic_w, ic_h, boxstyle="round,pad=0.3", facecolor='#181818', edgecolor='#888888', lw=1.5, zorder=4))
    ax.add_patch(patches.Circle((ic_x + 2.2, ic_y + ic_h - 2.2), 0.8, facecolor='#999999', zorder=5))
    ax.text(ic_x + ic_w/2, ic_y + ic_h/2, "PRIMARY\nCONTROLLER /\nANALOG IC", color='white', fontsize=7.5, ha='center', va='center', fontweight='bold', zorder=5)

    for sx, sy, lbl, col in [(28, 36, "R1\n1%", '#111111'), (28, 20, "C_in\nX7R", '#8d5524'), (62, 36, "R2\n1%", '#111111'), (62, 20, "C_out\nLow-ESR", '#8d5524')]:
        ax.add_patch(patches.Rectangle((sx-0.8, sy), 1.0, 2.8, facecolor='#cccccc', zorder=4))
        ax.add_patch(patches.Rectangle((sx+4.0, sy), 1.0, 2.8, facecolor='#cccccc', zorder=4))
        ax.add_patch(patches.Rectangle((sx, sy), 4.2, 2.8, facecolor=col, edgecolor='#555555', lw=0.8, zorder=5))
        ax.text(sx+2.1, sy-2.8, lbl, color='white', fontsize=6.8, ha='center', fontweight='bold')

    ax.add_patch(patches.Rectangle((74, 19), 11, 22, facecolor='#1a1a1a', edgecolor='#d4af37', lw=1.5, zorder=4))
    for i, pin_txt in enumerate(["V_RAIL", "SIG_OUT", "CTRL_IO", "GND_REF"]):
        py = 37 - i * 4.8
        ax.add_patch(patches.Circle((76.5, py), 1.3, facecolor='#d4af37', edgecolor='white', lw=0.8, zorder=5))
        ax.text(79, py, pin_txt, color='#38bdf8', fontsize=6.5, va='center', fontweight='bold', zorder=6)

    ax.text(49, 55.5, f"3D PCB LAYOUT: {req_text[:48]}", color='#38bdf8', fontsize=9.5, ha='center', fontweight='bold')
    ax.text(49, 2.2, f"Domain: {sys_domain[:35]} | Target: {mcu_name} | 4-Layer Star-Ground & Thermal Vias", color='#bbbbbb', fontsize=7.5, ha='center')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf

def sanitize_schemdraw(code):
    for bad in ["elm.Output()", "elm.Input()", "elm.Terminal()", "elm.Port()"]:
        code = code.replace(bad, "elm.Dot()")
    return code.replace("d.draw()", "").replace("plt.show()", "").strip()

if st.button("⚡ Synthesize Complete End-to-End Hardware Design", type="primary"):
    if not gemini_key:
        st.error("⚠️ దయచేసి ఎడమవైపు సైడ్‌బార్‌లో మీ Gemini API Key పేస్ట్ చేయండి.")
    else:
        with st.spinner("🧠 Principal Electronics Architect మీ రిక్వైర్‌మెంట్ ప్రకారం పూర్తి R&D డిజైన్ తయారు చేస్తోంది..."):
            prompt = f"""
            You are a World-Class Principal Electronics & Hardware R&D Architect.
            Design a complete, requirement-adaptive, end-to-end hardware engineering package tailored specifically to the user's requirements below.
            Language: {lang_mode}.

            SYSTEM DOMAIN: {system_type}
            TARGET CONTROLLER: {target_mcu}
            USER REQUIREMENTS: {user_requirements}

            Divide your output strictly using these exact 5 markers:

            ===TAB1===
            **1. System Architecture, Topology Selection & Verified BOM:**
            - Why this topology was chosen for the exact requirements (voltage, current, frequency, noise, efficiency).
            - Complete BOM Table: Designator, Exact Part Number, Value, Voltage/Power Rating & Tolerance, Qty, Role, Approx Price (₹).
            - Verified Datasheet Pinout & Absolute Maximum Ratings Table for all active ICs/transistors.

            ===TAB2===
            **2. Complete End-to-End Engineering Math & PCB Layout Rules:**
            - Step-by-step mathematical derivations for EVERY component value (resistors, capacitors, inductors, gain, switching frequency, ripple, thermal dissipation $P=I^2R$, worst-case tolerance).
            - Professional PCB Layout, Grounding, Thermal Management & EMI/EMC guidelines specific to this circuit.

            ===TAB3===
            Write ONLY valid Python `schemdraw` code inside ```python ... ``` to draw a clean, well-labeled horizontal circuit schematic for these requirements.
            Rules: `d = schemdraw.Drawing(show=False)`, use ONLY `elm.Resistor()`, `elm.Capacitor()`, `elm.Opamp()`, `elm.Ground()`, `elm.Vdd()`, `elm.Dot()`, `elm.Line()`, `elm.LED()`, `elm.Diode()`, `elm.SourceV()`, `elm.Inductor()`, `elm.NFet()`. NEVER use `elm.Output()` or `elm.Input()`. Save to `buf`:
            ```python
            buf = io.BytesIO()
            d.save(buf, format='png', dpi=300)
            buf.seek(0)
            ```

            ===TAB4===
            **4. Assembly, Bench Testing & LTspice Simulation:**
            - Step-by-step wiring/soldering instructions.
            - Bench Verification & Oscilloscope/Multimeter test points (TP1, TP2, TP3 expected values) + Troubleshooting guide.
            - Complete runnable LTspice `.cir` simulation netlist.

            ===TAB5===
            **5. Production Firmware / Control Logic & Calibration:**
            - Complete non-blocking C++ firmware for {target_mcu} (or hardware tuning/calibration procedure if Pure Analog) with exact physical unit conversion, protection/filtering logic, and Serial Telemetry output.
            """
            raw_out, used_model = run_rd_synthesis(gemini_key, prompt)
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
                    st.image(env["buf"], caption="Requirement-Adaptive Circuit Schematic Diagram", use_container_width=True)
                    st.download_button("⬇️ Schematic PNG డౌన్‌లోడ్", data=env["buf"], file_name="circuit_schematic.png", mime="image/png")
                else:
                    st.code(py_code, language="python")
            except Exception as err:
                st.warning(f"Schematic కోడ్ వివరాలు ({err}):")
                st.code(py_code, language="python")

        with tabs[3]:
            pcb_buf = render_adaptive_3d_pcb(user_requirements, system_type, target_mcu)
            st.image(pcb_buf, caption="3D PCB Architecture View", use_container_width=True)
            st.download_button("⬇️ 3D PCB PNG డౌన్‌లోడ్", data=pcb_buf, file_name="3d_pcb.png", mime="image/png")
