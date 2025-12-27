import streamlit as st
import calendar
from datetime import datetime, timedelta

# Page Setup
st.set_page_config(page_title="Nairobi Pipe Builder", layout="wide")

# --- DATA ---
LOCATIONS = ["Any", "JVJ", "AGW", "Mbingu", "KEN", "Sig", "KICC", "Train", "Adams", "Comet", "Sarit", "Nyayo"]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
NTHS = ["1st", "2nd", "3rd", "4th", "5th"]
WEEKS = ["W1", "W2", "W3", "W4", "W5"]
SHIFTS = ["EM", "M", "A", "E"]

# Helper to generate Scheduling Week options for the year
def get_scheduling_weeks(year):
    options = []
    for m_idx in range(1, 13):
        month_name = calendar.month_name[m_idx]
        # Find first Monday
        first_day = datetime(year, m_idx, 1)
        first_mon = first_day + timedelta(days=(7 - first_day.weekday()) % 7)
        # Determine how many weeks are in this scheduling month (usually 4 or 5)
        # We calculate up to the start of the next month's first Monday
        next_m = m_idx + 1 if m_idx < 12 else 1
        next_y = year if m_idx < 12 else year + 1
        next_first_day = datetime(next_y, next_m, 1)
        next_first_mon = next_first_day + timedelta(days=(7 - next_first_day.weekday()) % 7)
        
        num_weeks = (next_first_mon - first_mon).days // 7
        for w in range(1, num_weeks + 1):
            options.append(f"{month_name} {year} - W{w}")
    return options

st.title("Nairobi Pipe Code Builder v5.1")

# --- LAYOUT ---
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
    method = st.radio("Pick ONE:", ["Method A: Calendar Occurrence (1st Wed...)", "Method B: Scheduling Week (W1...)"], horizontal=True)
    
    sel_nths, sel_weeks = [], []
    if "Calendar" in method:
        nth_cols = st.columns(5)
        sel_nths = [n for i, n in enumerate(NTHS) if nth_cols[i].checkbox(n)]
    else:
        wk_cols = st.columns(5)
        sel_weeks = [w for i, w in enumerate(WEEKS) if wk_cols[i].checkbox(w)]

    st.subheader("4. Shifts")
    shift_cols = st.columns(4)
    sel_shifts = [s for i, s in enumerate(SHIFTS) if shift_cols[i].checkbox(s)]

# --- LOGIC ---
time_elements = []

# Scenario 1: Method A (Nth + Day) - e.g., "1Wed, 3Wed"
if sel_nths and sel_days:
    for n in sel_nths:
        for d in sel_days:
            time_elements.append(f"{n[0]}{d}")

# Scenario 2: Method B (W-Weeks) - e.g., "W1, W2"
elif sel_weeks:
    time_elements = sel_weeks

# Scenario 3: Regular Weekdays (If no Method A or B is active) - e.g., "Wed"
elif sel_days:
    time_elements = sel_days

# --- STRING ASSEMBLY ---
# We use list comprehension to ensure we only join items that actually have content
loc_string = ", ".join(sel_locs)
time_string = ", ".join(time_elements)
shift_string = ", ".join(sel_shifts)

# Combine only the non-empty parts with the pipe "|" separator
parts = [p for p in [loc_string, time_string, shift_string] if p.strip()]

if parts:
    final_code = " | ".join(parts)
else:
    final_code = "Select options to generate code..."

st.divider()
st.subheader("Generated Pipe Code")
st.code(final_code, language="text")

# --- PREVIEW PANEL ---
with col_right:
    st.subheader("📅 Scheduling Context")
    week_options = get_scheduling_weeks(2026)
    selected_week_str = st.selectbox("Select Scheduling Week", week_options)
    
    # Extract month and week number from selection (e.g. "January 2026 - W1")
    parts = selected_week_str.split(" ")
    sel_month_name = parts[0]
    sel_week_num = parts[-1] # e.g., "W1"
    
    month_idx = list(calendar.month_name).index(sel_month_name)
    first_day = datetime(2026, month_idx, 1)
    first_mon = first_day + timedelta(days=(7 - first_day.weekday()) % 7)
    
    # Calculate the specific 7-day range for this Scheduling Week
    week_int = int(sel_week_num[1:]) - 1
    start_of_week = first_mon + timedelta(weeks=week_int)
    end_of_week = start_of_week + timedelta(days=6)
    
    st.write(f"**Dates:** {start_of_week.strftime('%b %d')} — {end_of_week.strftime('%b %d')}")
    st.divider()

    matches = []
    # Check each day in this specific 7-day scheduling window
    for i in range(7):
        curr_date = start_of_week + timedelta(days=i)
        d_name = DAYS[curr_date.weekday()]
        
        # Determine Calendar Nth (for Method A matching)
        nth_val = (curr_date.day - 1) // 7 + 1
        nth_s = f"{nth_val}{NTHS[nth_val-1][1:]}"
        
        # Matching Logic
        is_match = False
        if sel_nths and sel_days:
            if d_name in sel_days and nth_s in sel_nths: is_match = True
        elif sel_weeks and sel_days:
            if d_name in sel_days and sel_week_num in sel_weeks: is_match = True
        elif sel_days and not sel_nths and not sel_weeks:
            if d_name in sel_days: is_match = True

        if is_match:
            matches.append(f"{curr_date.strftime('%a, %b %d')}")

    if matches:
        st.write("Volunteer is **ACTIVE** on:")
        for m in matches: st.success(m)
    else:
        st.write("Volunteer is **NOT ACTIVE** during this scheduling week.")
