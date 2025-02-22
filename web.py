import streamlit as st


def main():
    st.set_page_config(page_title="Triage System", layout="centered")

    st.title("🏥 Patient Triage System")
    st.write("Enter patient details below to determine their triage status.")

    # Input Fields
    name = st.text_input("Patient Name")
    age = st.number_input("Age", min_value=0, max_value=120, step=1)
    description = st.text_area("Patient Description",
                               placeholder="Describe symptoms, conditions, or any relevant details.")
    pain_level = st.slider("Pain Level (0-10)", 0, 10, 5)
    bp_systolic = st.number_input("Systolic BP (mmHg)", min_value=50, max_value=250, step=1)
    bp_diastolic = st.number_input("Diastolic BP (mmHg)", min_value=30, max_value=150, step=1)
    heart_rate = st.number_input("Heart Rate (bpm)", min_value=30, max_value=200, step=1)
    oxygen_saturation = st.number_input("Oxygen Saturation (%)", min_value=50, max_value=100, step=1)

    if st.button("Submit", use_container_width=True):
        patient_data = {
            "name": name,
            "age": age,
            "description": description,
            "pain_level": pain_level,
            "bp_systolic": bp_systolic,
            "bp_diastolic": bp_diastolic,
            "heart_rate": heart_rate,
            "oxygen_saturation": oxygen_saturation,
        }

        # Placeholder for model prediction
        triage_status = "Pending Model Prediction"  # Replace with model logic

        st.success(f"Triage Status: {triage_status}")

        # Display entered details for confirmation
        st.subheader("Patient Details")
        st.json(patient_data)


if __name__ == "__main__":
    main()
