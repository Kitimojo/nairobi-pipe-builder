import streamlit as st
import calendar
from datetime import datetime, timedelta

# Page Setup
st.set_page_config(page_title="Nairobi Pipe Builder v6.2", layout="wide")

# --- DATA ---
LOCATIONS = ["Any", "JVJ", "AGW", "Mbingu", "KEN", "KICC", "Train", "Adams", "Comet", "Sarit", "Nyayo", "Sig"]

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
NTHS = ["1st", "2nd", "3rd", "4th", "5th"]
WEEKS = ["W1", "W2", "W3", "W4", "W5"]

# NEW SHIFT CODES
SHIFTS_NORMAL = ["am1", "am2", "am3", "pm1", "pm2", "pm3"]
SHIFTS_SIG = ["Sig1", "Sig2", "Sig3", "Sig4"]

ALTS = {"Alternating Odd Weeks": "Alt1", "Alternating Even Weeks": "Alt2"}


# --- CLEAR ALL LOGIC ---
def clear_all_fields():
    keys = list(st.session_state.keys())
    for key in keys:
        if any(x in key for x in ["loc_", "day_", "nth_", "wk_", "shift_"]):
            st.session_state[key] = False
        if key == "method_choice":
            st.session_state[key] = "Method A: Scheduling Week (W1...)"
        if key == "alt_choice":
            st.session_state[key] = "None"


# --- WEEK CALCULATION ---
def get_scheduling_weeks(year):
    options = []
    for m_idx in range(1, 13):
        month_name = calendar.month_name[m_idx]
        first_day = datetime(year, m_idx, 1)
        first_mon = first_day + timedelta(days=(7 - first_day.weekday()) % 7)

        next_m = m_idx + 1 if m_idx < 12 else 1
        next_y = year if m_idx < 12 else year + 1
        next_first_day = datetime(next_y, next_m, 1)
        next_first_mon = next_first_day + timedelta(days=(7 - next_first_day.weekday()) % 7)

        num_weeks = (next_first_mon - first_mon).days // 7
        for w in range(1, num_weeks + 1):
            options.append(f"{month_name} {year} - W{w}")
    return options


# --- UI ---
st.title("Nairobi Pipe Code Builder v6.2")

col_left, col_right = st.columns([2, 1])

with col_left:

    # --- LOCATIONS ---
    st.subheader("1. Locations")
    sel_locs = []
    loc_cols = st.columns(4)

    # Track whether we need to clean up non-Sig locations
    cleanup_non_sig = False

    for i, loc in enumerate(LOCATIONS):
        if loc_cols[i % 4].checkbox(loc, key=f"loc_{loc}"):
            sel_locs.append(loc)

    sig_selected = "Sig" in sel_locs

    # If Sig is selected AND other locations are selected → mark for cleanup
    if sig_selected and len(sel_locs) > 1:
        cleanup_non_sig = True

    # Perform cleanup AFTER widgets have been created
    if cleanup_non_sig:
        for loc in LOCATIONS:
            if loc != "Sig":
                st.session_state[f"loc_{loc}"] = False
        sel_locs = ["Sig"]
        sig_selected = True

    # --- DAYS ---
    st.subheader("2. Days of the Week")
    day_cols = st.columns(7)
    sel_days = [day for i, day in enumerate(DAYS) if day_cols[i].checkbox(day, key=f"day_{day}")]

    # --- METHOD ---
    st.subheader("3. Timing Method")
    method = st.radio(
        "Pick ONE Method:",
        ["Method A: Scheduling Week (W1...)", 
         "Method B: Calendar Occurrence (1st Wed...)", 
         "Method C: Alternating Weeks (Odd/Even)"],
        key="method_choice",
        horizontal=True
    )

    sel_nths, sel_weeks, sel_alt = [], [], None

    if "Method A" in method:
        wk_cols = st.columns(5)
        sel_weeks = [w for i, w in enumerate(WEEKS) if wk_cols[i].checkbox(w, key=f"wk_{w}")]
    elif "Method B" in method:
        nth_cols = st.columns(5)
        sel_nths = [n for i, n in enumerate(NTHS) if nth_cols[i].checkbox(n, key=f"nth_{n}")]
    else:
        sel_alt_text = st.selectbox("Select Cycle:", ["None", "Alternating Odd Weeks", "Alternating Even Weeks"], key="alt_choice")
        if sel_alt_text != "None":
            sel_alt = ALTS[sel_alt_text]

    # --- SHIFTS ---
    st.subheader("4. Shifts")
    sel_shifts = []

    if sig_selected:
        st.info("Sig selected — choose from Sig-specific shifts.")
        shift_cols = st.columns(4)
        for i, s in enumerate(SHIFTS_SIG):
            if shift_cols[i].checkbox(s, key=f"shift_{s}"):
                sel_shifts.append(s)
    else:
        shift_cols = st.columns(6)
        for i, s in enumerate(SHIFTS_NORMAL):
            if shift_cols[i].checkbox(s, key=f"shift_{s}"):
                sel_shifts.append(s)

    # Enforce reverse rule: Sig shifts require Sig location
    if any(s in SHIFTS_SIG for s in sel_shifts) and not sig_selected:
        st.warning("Sig shift selected — Sig location has been automatically enabled.")
        st.session_state["loc_Sig"] = True
        for loc in LOCATIONS:
            if loc != "Sig":
                st.session_state[f"loc_{loc}"] = False
        sel_locs = ["Sig"]
        sig_selected = True


# --- LOGIC ENGINE ---
loc_val = ", ".join(sel_locs) if sel_locs else "Any"
day_val = "Any"
week_val = "Any"
shift_val = "Any"

day_elements = []

if "Method A" in method:
    if sel_days:
        day_val = ", ".join(sel_days)
    if sel_weeks:
        week_val = ", ".join(sel_weeks)

elif "Method B" in method:
    if sel_nths and sel_days:
        for n in sel_nths:
            for d in sel_days:
                day_elements.append(f"{n[0]}{d}")
        day_val = ", ".join(day_elements)
    elif sel_days:
        day_val = ", ".join(sel_days)

else:  # Method C
    if sel_days:
        day_val = ", ".join(sel_days)
    if sel_alt:
        week_val = sel_alt

if sel_shifts:
    shift_val = ", ".join(sel_shifts)

# --- STRING ASSEMBLY ---
final_code = f"Location: {loc_val} | Day: {day_val} | Week: {week_val} | Shift: {shift_val}"

st.divider()
st.subheader("Generated Pipe Code")
st.code(final_code, language="text")

st.button("Clear All", on_click=clear_all_fields)


# --- PREVIEW PANEL ---
with col_right:
    st.subheader("📅 Scheduling Context")
    week_options = get_scheduling_weeks(2026)
    selected_week_str = st.selectbox("Select Week to Preview", week_options)

    p = selected_week_str.split(" ")
    start_dt = datetime(2026, list(calendar.month_name).index(p[0]), 1)
    f_mon = start_dt + timedelta(days=(7 - start_dt.weekday()) % 7)
    curr_start = f_mon + timedelta(weeks=int(p[-1][1:]) - 1)

    st.write(f"**Dates:** {curr_start.strftime('%b %d')} — {(curr_start + timedelta(days=6)).strftime('%b %d')}")
    st.divider()

    matches = []
    for i in range(7):
        curr = curr_start + timedelta(days=i)
        d_name = DAYS[curr.weekday()]
        nth_s = f"{(curr.day - 1) // 7 + 1}{NTHS[(curr.day - 1) // 7][1:]}"
        iso_wk = curr.isocalendar()[1]

        match = False

        if "Method B" in method and sel_nths and d_name in sel_days:
            if nth_s in sel_nths:
                match = True

        elif "Method A" in method and sel_weeks and d_name in sel_days:
            if p[-1] in sel_weeks:
                match = True

        elif "Method C" in method and sel_alt and d_name in sel_days:
            is_odd = iso_wk % 2 != 0
            if (sel_alt == "Alt1" and is_odd) or (sel_alt == "Alt2" and not is_odd):
                match = True

        elif sel_days and not (sel_nths or sel_weeks or sel_alt):
            if d_name in sel_days:
                match = True

        if match:
            matches.append(curr.strftime('%a, %b %d'))

    if matches:
        for m in matches:
            st.success(m)
    else:
        st.write("Volunteer is **NOT ACTIVE** this week.")
