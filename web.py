import streamlit as st
import os

from groq import Groq

API_KEY = os.getenv("API_KEY")

print(secrets.API_KEY)

client = Groq(
    api_key=API_KEY,
)

def get_triage_color(triage_level):
    if triage_level == "1":
        return "#E3242B"
    elif triage_level == "2":
        return "#FFA62B"
    elif triage_level == "3":
        return "#FFE135"
    elif triage_level == "4":
        return "#74C365"
    elif triage_level == "5":
        return "#89CFF0"
    else:
        return "black"

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
    heart_rate = st.number_input("Heart Rate (bpm)", min_value=30, max_value=220, step=1)
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

        query = ("Give the triage level based on the following info. Description: " + str(patient_data["description"])
                 + ", Age: " + str(patient_data["age"])
                 + ", Pain Level: " + str(patient_data["pain_level"])
                 + ", BP: " + str(patient_data["bp_systolic"]) + "/" + str(patient_data["bp_diastolic"])
                 + ", Heart Rate: " + str(patient_data["heart_rate"])
                 + ", Oxygen Saturation: " + str(patient_data["oxygen_saturation"])
                 + ". Give a number from 1 through 5, where 1 is a life threatening injury that requires intervention, and 5 is not life-threatening in any way. Be sure to give only a number and nothing else. No punctuation or extra words. Only a number that is 1, 2, 3, 4, or 5")

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": query,
                }
            ],
            model="llama-3.3-70b-versatile",
        )


        print(query)
        triage_level = chat_completion.choices[0].message.content
        triage_color = get_triage_color(triage_level)

        # Display the triage status in a colored box
        st.markdown(
            f"""
                    <div style="
                        background-color: {triage_color};
                        padding: 20px;
                        border-radius: 10px;
                        text-align: center;
                        font-size: 24px;
                        color: black;
                        font-weight: bold;
                    ">
                        Triage Level: {triage_level}
                    </div>
                    """,
            unsafe_allow_html=True,
        )
        # Display entered details for confirmation
        #st.subheader("Patient Details")
        #st.json(patient_data)


if __name__ == "__main__":
    main()
