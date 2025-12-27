import streamlit as st
import calendar
from datetime import datetime, timedelta

# Page Config
st.set_page_config(page_title="Nairobi Pipe Builder", layout="wide")

# --- DATA ---
LOCATIONS = ["Any", "JVJ", "AGW", "Mbingu", "KEN", "Sig", "KICC", "Train", "Adams", "Comet", "Sarit", "Nyayo"]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
NTHS = ["1st", "2nd", "3rd", "4th", "5th"]
WEEKS = ["W1", "W2", "W3", "W4", "W5"]
SHIFTS = ["EM", "M", "A", "E"]

st.title("🇰🇪 Nairobi Pipe Code Builder v5.0")
st.info("Build your pipe code on the left; see the live calendar impact on the right.")

# --- SIDEBAR / LAYOUT ---
col_left, col_right = st.columns([2, 1])

with col_left:
    # 1. LOCATIONS (Multi-line layout)
    st.subheader("1. Locations")
    sel_locs = []
    # Using 4 columns to prevent vertical stretching
    loc_cols = st.columns(4)
    for i, loc in enumerate(LOCATIONS):
        if loc_cols[i % 4].checkbox(loc, key=f"loc_{loc}"):
            sel_locs.append(loc)

    # 2. DAYS
    st.subheader("2. Days of the Week")
    day_cols = st.columns(7)
    sel_days = [day for i, day in enumerate(DAYS) if day_cols[i].checkbox(day)]

    # 3. TIMING (Mutual Exclusivity Logic)
    st.subheader("3. Timing Method")
    method = st.radio("Choose One Method:", ["Method A: Calendar (1st Wed...)", "Method B: Scheduling (W1...)"], horizontal=True)
    
    sel_nths = []
    sel_weeks = []
    
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

# --- LOGIC & GENERATION ---
time_elements = []
if sel_nths and sel_days:
    for n in sel_nths:
        for d in sel_days: time_elements.append(f"{n[0]}{d}")
elif sel_weeks:
    time_elements = sel_weeks
elif sel_days:
    time_elements = sel_days

parts = [p for p in [", ".join(sel_locs), ", ".join(time_elements), ", ".join(sel_shifts)] if p]
final_code = " | ".join(parts) if parts else "Select options..."

st.divider()
st.subheader("Generated Pipe Code")
st.code(final_code, language="text")

# --- CALENDAR PREVIEW ---
with col_right:
    st.subheader("📅 Preview Context")
    target_month = st.selectbox("Select Month", list(calendar.month_name)[1:], index=datetime.now().month-1)
    target_year = 2026 # As requested for the Nairobi project context
    
    month_idx = list(calendar.month_name).index(target_month)
    
    # Calculate Scheduling Week 1 (First Monday)
    first_day = datetime(target_year, month_idx, 1)
    first_monday = first_day + timedelta(days=(7 - first_day.weekday()) % 7)
    
    matches = []
    cal = calendar.monthcalendar(target_year, month_idx)
    
    for week in cal:
        for day_num in week:
            if day_num == 0: continue
            curr_date = datetime(target_year, month_idx, day_num)
            day_name = DAYS[curr_date.weekday()]
            nth_str = f"{(day_num-1)//7 + 1}{NTHS[(day_num-1)//7][1:]}"
            
            sched_wk = None
            if curr_date >= first_monday:
                sched_wk = f"W{(curr_date - first_monday).days // 7 + 1}"

            # Match Logic
            match = False
            if sel_nths and sel_days:
                if day_name in sel_days and nth_str in sel_nths: match = True
            elif sel_weeks and sel_days:
                if day_name in sel_days and sched_wk in sel_weeks: match = True
            elif sel_days:
                if day_name in sel_days and not sel_nths and not sel_weeks: match = True

            if match:
                prefix = f"[{sched_wk}] " if sched_wk else "[Pre-W1] "
                matches.append(f"{prefix} {target_month[:3]} {day_num} ({day_name})")

    if matches:
        st.write(f"Active Dates in {target_month}:")
        for m in matches: st.write(f"✅ {m}")
    else:
        st.write("No dates match this logic.")