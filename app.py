import streamlit as st
import calendar
from datetime import datetime, timedelta

# Page Setup
st.set_page_config(page_title="Nairobi Pipe Builder v5.4", layout="wide")

# --- DATA ---
LOCATIONS = ["Any", "JVJ", "AGW", "Mbingu", "KEN", "Sig", "KICC", "Train", "Adams", "Comet", "Sarit", "Nyayo"]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
NTHS = ["1st", "2nd", "3rd", "4th", "5th"]
WEEKS = ["W1", "W2", "W3", "W4", "W5"]
SHIFTS = ["EM", "M", "A", "E"]
ALTS = {"Alternating Odd Weeks": "Alt1", "Alternating Even Weeks": "Alt2"}

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

st.title("Nairobi Pipe Code Builder v5.4")

# --- UI LAYOUT ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("1. Locations")
    sel_locs = []
    loc_cols = st.columns(4) 
    for i, loc in enumerate(LOCATIONS):
        if loc_cols[i % 4].checkbox(loc, key=f"loc_{loc}"):
            sel_locs.append(loc)

    st.subheader("2. Days of the Week")
    day_cols = st.columns(7)
    sel_days = [day for i, day in enumerate(DAYS) if day_cols[i].checkbox(day)]

    st.subheader("3. Timing Method")
    method = st.radio("Pick ONE Method:", 
                      ["Method A: Scheduling Week (W1...)", 
                       "Method B: Calendar Occurrence (1st Wed...)",
                       "Method C: Alternating Weeks (Odd/Even)"], 
                      horizontal=True)
    
    sel_nths, sel_weeks, sel_alt = [], [], None
    
    if "Method A" in method:
        wk_cols = st.columns(5)
        sel_weeks = [w for i, w in enumerate(WEEKS) if wk_cols[i].checkbox(w)]
    elif "Method B" in method:
        nth_cols = st.columns(5)
        sel_nths = [n for i, n in enumerate(NTHS) if nth_cols[i].checkbox(n)]
    else:
        # Method C
        alt_choice = st.selectbox("Select Cycle:", ["None", "Alternating Odd Weeks", "Alternating Even Weeks"])
        if alt_choice != "None":
            sel_alt = ALTS[alt_choice]

    st.subheader("4. Shifts")
    shift_cols = st.columns(4)
    sel_shifts = [s for i, s in enumerate(SHIFTS) if shift_cols[i].checkbox(s)]

# --- INITIALIZE VARIABLES ---
loc_val, day_val, week_val, shift_val = "Any", "Any", "Any", "Any"
day_elements = []

# --- LOGIC ENGINE ---
if sel_locs: loc_val = ", ".join(sel_locs)

if "Method A" in method:
    if sel_days: day_val = ", ".join(sel_days)
    if sel_weeks: week_val = ", ".join(sel_weeks)
elif "Method B" in method:
    if sel_nths and sel_days:
        for n in sel_nths:
            for d in sel_days: day_elements.append(f"{n[0]}{d}")
        day_val = ", ".join(day_elements)
    elif sel_days: day_val = ", ".join(sel_days)
else:
    # Method C
    if sel_days: day_val = ", ".join(sel_days)
    if sel_alt: week_val = sel_alt

if sel_shifts: shift_val = ", ".join(sel_shifts)

# --- STRING ASSEMBLY ---
final_code = f"Location: {loc_val} | Day: {day_val} | Week: {week_val} | Shift: {shift_val}"

st.divider()
st.subheader("Generated Pipe Code")
st.code(final_code, language="text")

# 1) RESET BUTTON
if st.button("Reset All Form Fields"):
    st.cache_data.clear()
    st.rerun()

# --- PREVIEW PANEL ---
with col_right:
    st.subheader("📅 Scheduling Context")
    week_options = get_scheduling_weeks(2026)
    selected_week_str = st.selectbox("Select Week to Preview", week_options)
    
    p = selected_week_str.split(" ")
    sel_month_name, sel_week_num = p[0], p[-1]
    m_idx = list(calendar.month_name).index(sel_month_name)
    f_day = datetime(2026, m_idx, 1)
    f_mon = f_day + timedelta(days=(7 - f_day.weekday()) % 7)
    
    wk_int = int(sel_week_num[1:]) - 1
    start_dt = f_mon + timedelta(weeks=wk_int)
    end_dt = start_dt + timedelta(days=6)
    
    st.write(f"**Dates:** {start_dt.strftime('%b %d')} — {end_dt.strftime('%b %d')}")
    st.divider()

    matches = []
    for i in range(7):
        curr = start_dt + timedelta(days=i)
        d_name = DAYS[curr.weekday()]
        nth_s = f"{(curr.day - 1) // 7 + 1}{NTHS[(curr.day - 1) // 7][1:]}"
        iso_wk = curr.isocalendar()[1]
        
        is_match = False
        if "Method B" in method and sel_nths and sel_days:
            if d_name in sel_days and nth_s in sel_nths: is_match = True
        elif "Method A" in method and sel_weeks and sel_days:
            if d_name in sel_days and sel_week_num in sel_weeks: is_match = True
        elif "Method C" in method and sel_alt and sel_days:
            is_odd = iso_wk % 2 != 0
            if d_name in sel_days:
                if (sel_alt == "Alt1" and is_odd) or (sel_alt == "Alt2" and not is_odd):
                    is_match = True
        elif sel_days and not (sel_nths or sel_weeks or sel_alt):
            if d_name in sel_days: is_match = True

        if is_match: matches.append(curr.strftime('%a, %b %d'))

    if matches:
        st.write("Volunteer is **ACTIVE** on:")
        for m in matches: st.success(m)
    else:
        st.write("Volunteer is **NOT ACTIVE** this week.")
