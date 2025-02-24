import streamlit as st
import os

from groq import Groq

API_KEY = st.secrets["API_KEY"]

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
    st.set_page_config(page_title="Triage Assist", layout="centered")

    st.title("🏥 Triage Assist")
    st.write("Enter patient details below to determine their triage status.")

    # Input Fields
    name = st.text_input("Patient Name")
    age = st.number_input("Age", min_value=0, max_value=120, step=1, value=None)
    description = st.text_area("Patient Description",
                               placeholder="Describe symptoms, conditions, or any relevant details.")
    pain_level = st.slider("Pain Level (0-10)", 0, 10, 0)
    bp_systolic = st.number_input("Systolic BP (mmHg)", min_value=50, max_value=250, step=1, value=None)
    bp_diastolic = st.number_input("Diastolic BP (mmHg)", min_value=30, max_value=150, step=1, value=None)
    heart_rate = st.number_input("Heart Rate (bpm)", min_value=30, max_value=220, step=1, value=None)
    oxygen_saturation = st.number_input("Oxygen Saturation (%)", min_value=50, max_value=100, step=1, value=None)

    if st.button("Submit", use_container_width=True):
        age = "Unknown" if age is None else age
        pain_level = "Unknown" if pain_level is None else pain_level
        bp_systolic = "Unknown" if bp_systolic is None else bp_systolic
        bp_diastolic = "Unknown" if bp_diastolic is None else bp_diastolic
        heart_rate = "Unknown" if heart_rate is None else heart_rate
        oxygen_saturation = "Unknown" if oxygen_saturation is None else oxygen_saturation

        patient_data = {
            "name": name if name else "Unknown",
            "age": age,
            "description": description if description else "Unknown",
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
                 + ". Give a number from 1 through 5, where 1 is a life threatening injury that requires intervention, and 5 is not life-threatening in any way. Then, give a ONE sentence (LESS THAN 10 WORDS) description of why. Seperate the number from the description with a semi colon (for example, \"1;Patient is entering cardiac arrest and needs AED.\" No extra punctuation or extra words. Only a number that is 1, 2, 3, 4, or 5 and a description that is ONE sentence and 10 words or less. DO NOT use a semi colon anywhere else in the response. Do not give explicit medical advice.")

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": query,
                }
            ],
            model="llama-3.3-70b-versatile",
        )

        response = chat_completion.choices[0].message.content
        triage_level = response.split(";")[0]
        triage_color = get_triage_color(triage_level)
        triage_description = response.split(";")[1]

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

        st.markdown(
            """
            <style>
            .css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob,
            .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137,
            .viewerBadge_text__1JaDK {
                display: none;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        import streamlit as st

        hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            footer:after {
                content: '';
                visibility: visible;
                display: block;
                position: relative;
                padding: 0px;
                top: 0px;
            }
            </style>
        """
        st.markdown(hide_streamlit_style, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
