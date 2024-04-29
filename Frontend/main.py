import streamlit as st
from assets import Assets
from dataloader import display_battery_data
from swap import Swap
from dataloader import load_battery_data

def prepare_for_swap():
    print("\nInitial battery states, charge, and health before swapping:")
    print(st.session_state)
    st.session_state['discharging_battery'] = None
    st.session_state['candidate_battery'] = None
    highest_combined_value = -1

    for battery_id, state in st.session_state.battery_states.items():
        cycle_key = f'cycle_{battery_id}'
        cycle_count = st.session_state.get(cycle_key, 1)
        battery_data = load_battery_data(battery_id, state, cycle_count)
        soc = battery_data.get("State of charge", "N/A")
        soh = battery_data.get("State of health", "N/A")
        if state == "Discharge":
            st.session_state['discharging_battery'] = battery_id
        elif state == "Charge":
            soc = float(soc.replace('%', ''))
            soh = float(soh.replace('%', ''))
            combined_value = soc + soh
            if soc >= 75 and soh >= 75 and combined_value > highest_combined_value:
                highest_combined_value = combined_value
                st.session_state['candidate_battery'] = battery_id
    print('preparing for swap')
    set_robot_battery_na()
        
def set_robot_battery_na():
    if 'discharging_battery' in st.session_state:
        battery_id = st.session_state['discharging_battery']
        st.session_state.battery_states[battery_id] = "NA"
        # Set a flag indicating that this battery should not load data
        st.session_state[f'na_{battery_id}'] = True
        st.session_state['unplugged'] = True
        st.session_state['docked'] = False
        start_charging_robot_battery()

def start_charging_robot_battery():
    if 'discharging_battery' in st.session_state:
        battery_id = st.session_state['discharging_battery']
        # Change the state from "NA" to "Charge"
        st.session_state.battery_states[battery_id] = "Charge"
        # Reset the NA flag since the battery is now charging
        if f'na_{battery_id}' in st.session_state:
            del st.session_state[f'na_{battery_id}']
        set_swapping_battery_na()

def set_swapping_battery_na():
    if 'candidate_battery' in st.session_state:
        battery_id = st.session_state['candidate_battery']
        st.session_state.battery_states[battery_id] = "NA"
        # Similarly, set a flag for the swapping battery
        st.session_state[f'na_{battery_id}'] = True
        execute_swap()

def execute_swap():
    if 'discharging_battery' in st.session_state and 'candidate_battery' in st.session_state:
        discharging_battery = st.session_state['discharging_battery']
        candidate_battery = st.session_state['candidate_battery']

        # Execute the swap in battery states
        st.session_state.battery_states[discharging_battery] = "Charge"
        st.session_state.battery_states[candidate_battery] = "Discharge"

        # Log the swap for history
        swap_reason = f"{discharging_battery} --> {candidate_battery}"
        st.session_state.swap_history.append(swap_reason)
        st.session_state[f'swap_count_{discharging_battery}'] = st.session_state.get(f'swap_count_{discharging_battery}', 0) + 1
        st.session_state[f'swap_count_{candidate_battery}'] = st.session_state.get(f'swap_count_{candidate_battery}', 0) + 1

        # Set completion flags for tracking state
        st.session_state['discharge_complete_{discharging_battery}'] = True
        st.session_state['charge_complete_{candidate_battery}'] = True

        # Reset NA flags to allow data loading
        if f'na_{discharging_battery}' in st.session_state:
            del st.session_state[f'na_{discharging_battery}']
        if f'na_{candidate_battery}' in st.session_state:
            del st.session_state[f'na_{candidate_battery}']

        # Increment the cycle index based on the swap count
        if st.session_state[f'swap_count_{discharging_battery}'] % 2 == 0:
            cycle_key = f'cycle_{discharging_battery}'
            st.session_state[cycle_key] = st.session_state.get(cycle_key, 1) + 1

        if st.session_state[f'swap_count_{candidate_battery}'] % 2 == 0:
            cycle_key = f'cycle_{candidate_battery}'
            st.session_state[cycle_key] = st.session_state.get(cycle_key, 1) + 1
        st.session_state['swap'] = False
        print("\nInitial battery states, charge, and health after swapping:")
        print(st.session_state.battery_states)
        st.rerun()

if 'battery_states' not in st.session_state:
    st.session_state.battery_states = {"0005": "Discharge", "0006": "Charge", "0007": "Charge"}
    print("battery states initialized")
if 'pending_update' not in st.session_state:
    st.session_state.pending_update = False
if 'batteries_to_update' not in st.session_state:
    st.session_state.batteries_to_update = []
if 'swap_history' not in st.session_state:
    st.session_state.swap_history = []
if 'swap' not in st.session_state:
     st.session_state.swap = False


st.title("Battery Status Dashboard")


with st.sidebar:
    st.header("Battery Settings")

    st.markdown("### Alerts", unsafe_allow_html=True)
    alert_temp1 = st.empty()
    alert_temp2 = st.empty()
    alert_temp3 = st.empty()
    alert_health1 = st.empty()
    alert_health2 = st.empty()
    alert_health3 = st.empty()

    st.markdown("### Battery Cycles")
    cycle_b5 = st.number_input("Select Cycle Number:", min_value=1, value=st.session_state.get('cycle_0005', 1), step=1, key="cycle_b5")
    st.session_state['cycle_0005'] = cycle_b5
    
    cycle_b6 = st.number_input("Select Cycle Number:", min_value=1, value=st.session_state.get('cycle_0006', 1), step=1, key="cycle_b6")
    st.session_state['cycle_0006'] = cycle_b6

    cycle_b7 = st.number_input("Select Cycle Number:", min_value=1, value=st.session_state.get('cycle_0007', 1), step=1, key="cycle_b7")
    st.session_state['cycle_0007'] = cycle_b7


    st.subheader("Swap History")
    if st.session_state.get('swap_history', []):
        for history_item in st.session_state.swap_history:
            st.text(history_item)
    if st.button('Swap'):
        prepare_for_swap()

battery_data_placeholder = st.empty()  # The placeholder for battery data

for _ in range(200):
    with battery_data_placeholder.container():
        display_battery_data("0005", cycle_b5, alert_temp1, alert_health1)
        display_battery_data("0006", cycle_b6, alert_temp2, alert_health2)
        display_battery_data("0007", cycle_b7, alert_temp3, alert_health3)

