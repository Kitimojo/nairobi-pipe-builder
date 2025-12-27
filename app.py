import streamlit as st
import calendar
from datetime import datetime, timedelta

# Page Setup - Wide mode helps keep the preview panel visible
st.set_page_config(page_title="Nairobi Pipe Builder v5.2", layout="wide")

# --- DATA ---
LOCATIONS = ["Any", "JVJ", "AGW", "Mbingu", "KEN", "Sig", "KICC", "Train", "Adams", "Comet", "Sarit", "Nyayo"]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
NTHS = ["1st", "2nd", "3rd", "4th", "5th"]
WEEKS = ["W1", "W2", "W3", "W4", "W5"]
SHIFTS = ["EM", "M", "A", "E"]

# Helper to generate Scheduling Week options for 2026 (Starts with 1st Monday)
def get_scheduling_weeks(year):
    options = []
    for m_idx in range(1, 13):
        month_name = calendar.month_name[m_idx]
        first_day = datetime(year, m_idx, 1)
        # Find first Monday of the month
        first_mon = first_day + timedelta(days=(7 - first_day.weekday()) % 7)
        
        # Calculate when the next month's scheduling cycle starts
        next_m = m_idx + 1 if m_idx < 12 else 1
        next_y = year if m_idx < 12 else year + 1
        next_first_day = datetime(next_y, next_m, 1)
        next_first_mon = next_first_day + timedelta(days=(7 - next_first_day.weekday()) % 7)
        
        num_weeks = (next_first_mon - first_mon).days // 7
        for w in range(1, num_weeks + 1):
            options.append(f"{month_name} {year} - W{w}")
    return options

st.title("Nairobi Pipe Code Builder v5.2")

# --- UI LAYOUT ---
col_left, col_right = st.columns([2, 1])

with col_left:
    # 1. LOCATIONS (Grid layout)
    st.subheader("1. Locations")
    sel_locs = []
    loc_cols = st.columns(4) 
    for i, loc in enumerate(LOCATIONS):
        if loc_cols[i % 4].checkbox(loc, key=f"loc_{loc}"):
            sel_locs.append(loc)

    # 2. DAYS
    st.subheader("2. Days of the Week")
    day_cols = st.columns(7)
    sel_days = [day for i, day in enumerate(DAYS) if day_cols[i].checkbox(day)]

    # 3. TIMING METHOD (Mutually Exclusive)
    st.subheader("3. Timing Method")
    method = st.radio("Pick ONE Method:", ["Method A: Calendar Occurrence (1st Wed...)", "Method B: Scheduling Week (W1...)"], horizontal=True)
    
    sel_nths, sel_weeks = [], []
    if "Calendar" in method:
        nth_cols = st.columns(5)
        sel_nths = [n for i, n in enumerate(NTHS) if nth_cols[i].checkbox(n)]
    else:
        wk_cols = st.columns(5)
        sel_weeks = [w for i, w in enumerate(WEEKS) if wk_cols[i].checkbox(w)]

    # 4. SHIFTS
    st.subheader("4. Shifts")
    shift_cols = st.columns(4)
    sel_shifts = [s for i, s in enumerate(SHIFTS) if shift_cols[i].checkbox(s)]

# --- INITIALIZE PIPE VARIABLES (Prevents NameError) ---
loc_section = ""
day_section = ""
week_section = ""
shift_section = ""
day_elements = []

# --- LOGIC ENGINE ---
# 1. Locations
loc_section = ", ".join(sel_locs)

# 2. Timing/Days
if sel_nths and sel_days:
    # Method A: Fused format (e.g. 1Wed)
    for n in sel_nths:
        for d in sel_days:
            day_elements.append(f"{n[0]}{d}")
    day_section = ", ".join(day_elements)
    week_section = "" # Method A uses no separate week section
elif sel_weeks:
    # Method B: Separate sections (e.g. Tue | W1)
    day_section = ", ".join(sel_days)
    week_section = ", ".join(sel_weeks)
elif sel_days:
    # Standard weekly fallback
    day_section = ", ".join(sel_days)

# 3. Shifts
shift_section = ", ".join(sel_shifts)

# --- STRING ASSEMBLY ---
# Desired Format: Location | Days | Weeks | Shifts
parts = [p for p in [loc_section, day_section, week_section, shift_section] if p.strip()]
final_code = " | ".join(parts) if parts else "Select options to generate code..."

st.divider()
st.subheader("Generated Pipe Code")
st.code(final_code, language="text")

# --- PREVIEW PANEL (Right Column) ---
with col_right:
    st.subheader("📅 Scheduling Context")
    week_options = get_scheduling_weeks(2026)
    selected_week_str = st.selectbox("Select Week to Preview", week_options)
    
    # Parse selection
    p = selected_week_str.split(" ")
    sel_month_name = p[0]
    sel_week_num = p[-1]
    
    m_idx = list(calendar.month_name).index(sel_month_name)
    f_day = datetime(2026, m_idx, 1)
    f_mon = f_day + timedelta(days=(7 - f_day.weekday()) % 7)
    
    # Calculate dates for the chosen week
    wk_int = int(sel_week_num[1:]) - 1
    start_dt = f_mon + timedelta(weeks=wk_int)
    end_dt = start_dt + timedelta(days=6)
    
    st.write(f"**Dates:** {start_dt.strftime('%b %d')} — {end_dt.strftime('%b %d')}")
    st.divider()

    matches = []
    for i in range(7):
        curr = start_dt + timedelta(days=i)
        d_name = DAYS[curr.weekday()]
        nth_v = (curr.day - 1) // 7 + 1
        nth_s = f"{nth_v}{NTHS[nth_v-1][1:]}"
        
        is_match = False
        if sel_nths and sel_days:
            if d_name in sel_days and nth_s in sel_nths: is_match = True
        elif sel_weeks and sel_days:
            if d_name in sel_days and sel_week_num in sel_weeks: is_match = True
        elif sel_days and not sel_nths and not sel_weeks:
            if d_name in sel_days: is_match = True

        if is_match:
            matches.append(curr.strftime('%a, %b %d'))

    if matches:
        st.write("Volunteer is **ACTIVE** on:")
        for m in matches: st.success(m)
    else:
        st.write("Volunteer is **NOT ACTIVE** this week.")
