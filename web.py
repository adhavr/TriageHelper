import streamlit as st
from PIL import Image
from groq import Groq
import base64
import io
from streamlit_cookies_controller import CookieController
import time

# Initialize CookieController
cookie_name = 'triage_assist'
controller = CookieController(key='cookies')

# Mock user database (replace with a real database in production)
USERS = {
    "doctor1": {"password": "password1"},
    "doctor2": {"password": "password2"},
}

# Initialize Groq client
def get_groq_client():
    return Groq(api_key=st.secrets["API_KEY"])

# Function to encode the image
def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# Function to analyze the image
def analyze_image(image):
    base64_image = encode_image(image)
    client = get_groq_client()
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "A person has come to the hospital and this is an image of them. Give a 2-5 sentence description of the injury/ailment/sickness that has led them to come to the hospital. A medical professional should be able to use your description in order to make decisions. If it is not clear what you see, say that. It is better to be not specific than wrong."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        model="llama-3.2-11b-vision-preview",
    )
    return chat_completion.choices[0].message.content

# Function to get triage color
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

# Check login state on page load
if 'login_ok' not in st.session_state:
    # Check the contents of the cookie
    cookie_username = controller.get(f'{cookie_name}_username')
    cookie_password = controller.get(f'{cookie_name}_password')

    if cookie_username and cookie_password:
        st.session_state.login_ok = True
        st.session_state.username = cookie_username
        st.session_state.password = cookie_password
        st.success(f'Welcome back {st.session_state.username}!')
    else:
        st.session_state.login_ok = False

# Login Page
def login_page():
    st.title("🔐 Login to TriageAssist")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        st.session_state.username = username
        st.session_state.password = password
        authenticate()

# Authenticate user
def authenticate():
    username = st.session_state.username
    password = st.session_state.password

    user_info = USERS.get(username, {})
    if user_info and user_info.get("password") == password:
        # Save to cookie
        controller.set(f'{cookie_name}_username', username, max_age=80*60*60)
        controller.set(f'{cookie_name}_password', password, max_age=80*60*60)
        st.session_state.login_ok = True
        st.rerun()
    else:
        st.error("Wrong username/password.")

# Logout Function
def logout():
    # Remove cookies to log out
    controller.remove(f'{cookie_name}_username')
    controller.remove(f'{cookie_name}_password')
    st.session_state.login_ok = False
    st.session_state.username = None
    st.session_state.password = None
    st.rerun()

# Main App
def main_app():
    st.set_page_config(page_title="Triage Assist", layout="centered")

    # Initialize session state for triage requests
    if "triage_requests" not in st.session_state:
        st.session_state.triage_requests = []

    # Sidebar for previous triage requests
    st.sidebar.title("📋 Previous Triage Requests")
    if st.session_state.triage_requests:
        # Sort triage requests by priority (1 at the top)
        sorted_requests = sorted(st.session_state.triage_requests, key=lambda x: int(x["triage_level"]))
        for i, request in enumerate(sorted_requests):
            with st.sidebar.expander(f"Triage {i + 1}: Level {request['triage_level']}"):
                st.write(f"**Description:** {request['description']}")
                st.write(f"**Triage Level:** {request['triage_level']}")
                st.write(f"**Reason:** {request['triage_description']}")
                if st.button(f"Resolve Triage {i + 1}", key=f"resolve_{i}"):
                    st.session_state.triage_requests.pop(i)
                    st.rerun()
    else:
        st.sidebar.write("No triage requests yet.")

    # Logout button
    if st.sidebar.button("Logout"):
        logout()

    # Main content
    st.title("🏥 TriageAssist")
    st.write("Enter patient details below to determine their triage status.")

    # Input Fields
    name = st.text_input("Name of patient", placeholder="Optional, will not affect results")
    age = st.number_input("Age", min_value=0, max_value=120, step=1, value=None)
    description = st.text_area("Patient Description",
                               placeholder="Describe symptoms, conditions, or any relevant details.")
    pain_level = st.slider("Pain Level (0-10)", 0, 10, 0)
    bp_systolic = st.number_input("Systolic BP (mmHg)", min_value=50, max_value=250, step=1, value=None)
    bp_diastolic = st.number_input("Diastolic BP (mmHg)", min_value=30, max_value=150, step=1, value=None)
    heart_rate = st.number_input("Heart Rate (bpm)", min_value=30, max_value=220, step=1, value=None)
    oxygen_saturation = st.number_input("Oxygen Saturation (%)", min_value=50, max_value=100, step=1, value=None)

    sex = st.radio("Sex", ["Male", "Female", "No Selection"], index=2)

    consciousness = st.radio("Consciousness", ["Alert", "Verbal Response", "Pain Response", "Unresponsive"], index=0)

    transport = st.radio("Mode of Transport", ["Walk", "Public Ambulance", "Private Vehicle", "Private Ambulance", "No Selection"], index=4)

    # Image Upload or Capture
    option = st.radio(
        "Choose an option:",
        ("Upload a photo", "Take a photo"),
        horizontal=True,
    )

    image = None

    if option == "Upload a photo":
        st.write("Upload a photo:")
        image_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        if image_file is not None:
            image = Image.open(image_file)
    else:
        st.write("Take a photo:")
        camera_image = st.camera_input("Take a photo", label_visibility="collapsed")
        if camera_image is not None:
            image = Image.open(camera_image)

    if st.button("Submit", use_container_width=True):
        # Handle empty inputs
        age = "Unknown" if age is None else age
        pain_level = "Unknown" if pain_level is None else pain_level
        bp_systolic = "Unknown" if bp_systolic is None else bp_systolic
        bp_diastolic = "Unknown" if bp_diastolic is None else bp_diastolic
        heart_rate = "Unknown" if heart_rate is None else heart_rate
        oxygen_saturation = "Unknown" if oxygen_saturation is None else oxygen_saturation
        sex = "Unknown" if sex is None else sex
        consciousness = "Unknown" if consciousness is None else consciousness
        transport = "Unknown" if transport is None else transport

        image_description = "No image provided."
        if image is not None:
            image_description = analyze_image(image)

        patient_data = {
            "age": age,
            "description": description if description else "Unknown",
            "pain_level": pain_level,
            "bp_systolic": bp_systolic,
            "bp_diastolic": bp_diastolic,
            "heart_rate": heart_rate,
            "oxygen_saturation": oxygen_saturation,
            "sex": sex,
            "consciousness": consciousness,
            "transport": transport,
            "image_description": image_description,
        }

        query = ("Give the triage level based on the following info. Description: " + str(patient_data["description"])
                 + ", Description of the image of the patient: " + str(patient_data["image_description"])
                 + ", Pain Level: " + str(patient_data["pain_level"])
                 + ", BP: " + str(patient_data["bp_systolic"]) + "/" + str(patient_data["bp_diastolic"])
                 + ", Heart Rate: " + str(patient_data["heart_rate"])
                 + ", Oxygen Saturation: " + str(patient_data["oxygen_saturation"])
                 + ", Sex: " + str(patient_data["sex"])
                 + ", Consciousness: " + str(patient_data["consciousness"])
                 + ", Mode of Transport: " + str(patient_data["transport"])
                 + ". Give a number from 1 through 5, where 1 is a life threatening injury that requires intervention, and 5 is not life-threatening in any way. Then, give a ONE sentence (LESS THAN 10 WORDS) description of why. Separate the number from the description with a semi colon (for example, \"1;Patient is entering cardiac arrest and needs AED.\" No extra punctuation or extra words. Only a number that is 1, 2, 3, 4, or 5 and a description that is ONE sentence and 10 words or less. DO NOT use a semi colon anywhere else in the response. Do not give explicit medical advice.")

        client = get_groq_client()

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

        # Add triage request to session state
        st.session_state.triage_requests.append({
            "triage_level": triage_level,
            "description": description,
            "triage_description": triage_description,
        })

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
            f"""
                    <div style="
                        text-align: center;
                        font-size: 16px;
                        color: #666666;
                        margin-top: 10px;
                    ">
                        {triage_description}
                    </div>
                    """,
            unsafe_allow_html=True,
        )

        # Display entered details for confirmation
        st.subheader("Patient Details")
        st.json(patient_data)

# App Entry Point
def main():
    time.sleep(1)
    if not st.session_state["login_ok"]:
        cookie_username = controller.get(f'{cookie_name}_username')
        cookie_password = controller.get(f'{cookie_name}_password')

        if cookie_username and cookie_password:
            st.session_state.login_ok = True
            main_app()
        else:
            login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()
