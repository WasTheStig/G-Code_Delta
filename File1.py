import streamlit as st

def generate_gcode(
    program_type,
    feed_rate,
    laser_schedule,
    gas_delay,
    circle_radius,
    rotation_angle,
    corner_radius,
    overlap_pass,
    weld_direction,
    loop_count,
    use_pbf,
    pbf_overlap
):
    gcode = []
    cmd = "G2" if weld_direction.upper() == "CW" else "G3"

    gcode.append("OPEN PROG 1 CLEAR")
    gcode.append(f" ;Power Mode CW {power_mode}%")
    gcode.append(f";Point 1, Time {pp_1_t}s, Power {pp_1_p}%"
    gcode.append(f";Point 2, Time {pp_2_t}s, Power {pp_2_p}%"
    gcode.append(f";Point 3, Time {pp_3_t}s, Power {pp_3_p}%"
    gcode.append(f";Point 1, Time {pp_4_t}s, Power {pp_4_p}%"    
    gcode.append("p480=0")
    gcode.append("M36 ;Door Close")
    gcode.append(f"DWELL {initial_gas_delay} ;Cover Gas Delay")
    gcode.append("M53 ;Laser External Mode")
    gcode.append(f"M10 S{laser_schedule} ;Select Laser Schedule")
    gcode.append(f"DWELL {gas_delay} ;Gas Delay")
    gcode.append("M16 ;Cover Gas ON")
    gcode.append("G91 ;Relative Mode")
    gcode.append(f"F{feed_rate} ;Feed Rate")

    program_type = program_type.upper()

    if program_type == "TACK":
        gcode += [
            "M60 ;Shutter Open",
            "M54 ;Laser ON (Tack)",
            "DWELL 100 ;Short pulse",
            "M55 ;Laser OFF"
        ]

    elif program_type == "STITCH":
        gcode += [
            "G90 ;Absolute Mode",
            "M00 ;Optional Stop",
            "M54 ;Laser ON",
            "X0 Y0 ;Return Home",
            "M55 ;Laser OFF"
        ]

    elif program_type == "SQUARE":
        gcode += [
            "M54 ;Laser ON",
            "X1.1748",
            "Y-1.1748",
            "X-1.1748",
            "Y1.1748",
            "X0.25 ;Overlap",
            "M55 ;Laser OFF"
        ]

    elif program_type == "CIRCLE":
        gcode += [
            f"Y{circle_radius} ;Start position",
            f"F{feed_rate} ;Feed Rate",
            "M54 ;Laser ON",
            f"{cmd} X0 Y0 I0 J-{circle_radius}"
        ]
        if overlap_pass.upper() == "Y":
            gcode.append(f"{cmd} X0 Y0 I0 J-{circle_radius} ;Overlap")
        gcode.append("M55 ;Laser OFF")

    elif program_type == "ROTARY":
        gcode += [
            "M54 ;Laser ON",
            f"F{feed_rate}",
            f"A-{rotation_angle} ;Rotate part",
            "M55 ;Laser OFF"
        ]

    elif program_type == "ROUNDED":
        gcode += [
            "G90",
            "M00 ;Pause to position",
            "G91",
            "M54 ;Laser ON",
            "X.20",
            f"G2 X0.08 Y-0.08 R{corner_radius}",
            "Y-.6",
            f"G2 X-0.08 Y-0.08 R{corner_radius}",
            "X-.20",
            f"G2 X-0.08 Y0.08 R{corner_radius}",
            "Y0.6",
            f"G2 X0.08 Y0.08 R{corner_radius}",
            "M55 ;Laser OFF"
        ]

    elif program_type == "LOOP":
        gcode.append(f"P299={loop_count}")
        gcode.append("WHILE (P299>0)")
        gcode.append("M54 ;Laser ON")
        gcode.append("G2 X0.1 Y0 I0.1 J0")
        gcode.append("M55 ;Laser OFF")
        gcode.append("P299=(P299-1)")
        gcode.append("ENDWHILE")

    elif program_type == "PBF" and use_pbf.upper() == "Y":
        gcode.append(f"M149 S1 D{pbf_overlap} ;PBF ON")
        gcode += [
            "X.20",
            f"G2 X0.08 Y-0.08 R{pbf_overlap}",
            "Y-.6",
            f"G2 X0.08 Y-0.08 R{pbf_overlap}",
            "X-.20",
            f"G2 X-0.08 Y0.08 R{pbf_overlap}",
            "Y0.6",
            f"G2 X0.08 Y0.08 R{pbf_overlap}",
            "M149 S0 ;PBF OFF"
        ]

    gcode += [
        f"DWELL {cover_gas_delay} ;Cover Gas Delay",
        "M17 ;Cover Gas OFF",
        "M35 ;Door Open",
        "M52 ;Laser Pendant Mode",
        "p480=1 ;System Flag ON",
        "CLOSE ;End Program"
    ]

    return "\n".join(gcode)

st.title("Delta Motion G-Code Generator")
program_type = st.selectbox("Program Type", ["TACK", "STITCH", "SQUARE", "CIRCLE", "ROTARY", "ROUNDED", "LOOP", "PBF"])
st.title("Title Block Info")
power_mode = st.number_input("Power Mode CW (w)", value=0)
pp_1_t = st.number_input("Power Point 1 Time (s)", value=0)
pp_1_p = st.number_input("Power Point 1 Power (%)", value=0)
pp_2_t = st.number_input("Power Point 2 Time (s)", value=0)
pp_2_p = st.number_input("Power Point 2 Power (%)", value=0)
pp_3_t = st.number_input("Power Point 3 Time (s)", value=0)
pp_3_p = st.number_input("Power Point 3 Power (%)", value=0)
pp_4_t = st.number_input("Power Point 4 Time (s)", value=0)
pp_4_p = st.number_input("Power Point 4 Power (%)", value=0)
feed_rate = st.number_input("Feed Rate (in/s)", value=0.2)
laser_schedule = st.number_input("Laser Schedule #", value=1)
initial_gas_delay = st.number_input("Initial Gas Delay (ms)", value=2500)
gas_delay = st.number_input("Gas Delay (ms)", value=1500)
cover_gas_delay = st.number_input("Cover Gas Delay (ms)", value=3000)
circle_radius = st.number_input("Circle Radius (in)", value=0.125)
rotation_angle = st.number_input("Rotation Angle (deg)", value=480)
corner_radius = st.number_input("Corner Radius (in)", value=0.08)
overlap_pass = st.selectbox("Overlap Pass", ["Y", "N"])
weld_direction = st.selectbox("Weld Direction", ["CW", "CCW"])
loop_count = st.number_input("# of Loops", value=3)
use_pbf = st.selectbox("Use PBF?", ["Y", "N"])
pbf_overlap = st.number_input("PBF Overlap (in)", value=0.06)

if st.button("Generate G-Code"):
    result = generate_gcode(program_type, feed_rate, laser_schedule, gas_delay, circle_radius,
                            rotation_angle, corner_radius, overlap_pass, weld_direction,
                            loop_count, use_pbf, pbf_overlap)
    st.text_area("Generated G-Code", result, height=400)
    st.download_button("Download G-Code", result, file_name="weld_program.txt", mime="text/plain")
