import streamlit as st
from PIL import Image
from groq import Groq
import base64
import io
from streamlit_cookies_controller import CookieController
import time
import joblib
import pandas as pd

st.set_page_config(page_title="Triage Assist", layout="centered")

# Cache the model and scaler loading to avoid reloading on every interaction
@st.cache_resource
def load_model_and_scaler():
    voting_model = joblib.load('voting_model.pkl')
    scaler = joblib.load('scaler.pkl')
    feature_names = joblib.load('feature_names.pkl')
    return voting_model, scaler, feature_names

# Load the model and scaler once
voting_model, scaler, feature_names = load_model_and_scaler()

def get_groq_client():
    return Groq(api_key="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")

# Cache the image encoding function to avoid redundant computations
@st.cache_data
def encode_image(image):
    """
    Converts a PIL.Image object to a base64-encoded string.
    """
    buffered = io.BytesIO()  # Create a bytes buffer
    image.save(buffered, format="JPEG")  # Save the image to the buffer in JPEG format
    return base64.b64encode(buffered.getvalue()).decode('utf-8')  # Encode to base64

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

def map_sex(sex):
    if sex == "Male":
        return 1
    elif sex == "Female":
        return 2
    else:
        return 0  # Default value for "No Selection"

def map_transport(transport):
    if transport == "Walk":
        return 1
    elif transport == "Public Ambulance":
        return 2
    elif transport == "Private Vehicle":
        return 3
    elif transport == "Private Ambulance":
        return 4
    else:
        return 0  # Default value for "No Selection"

def map_consciousness(consciousness):
    if consciousness == "Alert":
        return 1
    elif consciousness == "Verbal Response":
        return 2
    elif consciousness == "Pain Response":
        return 3
    elif consciousness == "Unresponsive":
        return 4
    else:
        return 0  # Default value

def map_pain(pain_level):
    """
    Map pain level to 1 or 2 based on the slider value.
    """
    return 2 if pain_level >= 3 else 1

def map_injury(description):
    """
    Map injury to 1 or 2 based on the presence of the phrase "injur".
    """
    return 2 if "injur" in description.lower() else 1

def convert_to_celsius(temp, unit):
    """
    Convert temperature to Celsius.
    """
    if unit == "Fahrenheit (°F)":
        return (temp - 32) * 5 / 9  # Convert Fahrenheit to Celsius
    else:
        return temp  # Already in Celsius

def predict_with_ml_model(input_data):
    """
    Predicts the triage level using the machine learning model.
    """
    # Scale the input data
    input_data_scaled = scaler.transform(input_data)
    # Make the prediction
    prediction = voting_model.predict(input_data_scaled)
    return prediction[0] + 1

def calculate_recommended_triage(groq_triage_level, ml_triage_level):
    """
    Calculate the recommended triage level as a weighted average.
    """
    groq_weight = 0.75
    ml_weight = 0.25
    recommended_triage = groq_weight * float(groq_triage_level) + ml_weight * float(ml_triage_level)
    return round(recommended_triage)  # Round to the nearest integer

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
    st.title("🏥 TriageAssist")
    st.write("Enter patient details below to determine their triage status.")

    # Input Fields
    age = st.number_input("Age", min_value=0, max_value=120, step=1, value=None)

    sex_options = ["Male", "Female", "No Selection"]
    sex = st.radio("Sex", sex_options, index=2)  # Default to "No Selection"
    if sex == "No Selection":
        sex = None

    description = st.text_area("Patient Description",
                               placeholder="Describe symptoms, conditions, or any relevant details.")
    pain_level = st.slider("Pain Level (0-10)", 0, 10, 0)
    bp_systolic = st.number_input("Systolic BP (mmHg)", min_value=50, max_value=250, step=1, value=None)
    bp_diastolic = st.number_input("Diastolic BP (mmHg)", min_value=30, max_value=150, step=1, value=None)
    heart_rate = st.number_input("Heart Rate (bpm)", min_value=30, max_value=220, step=1, value=None)
    oxygen_saturation = st.number_input("Oxygen Saturation (%)", min_value=50, max_value=100, step=1, value=None)
    respiratory_rate = st.number_input("Respiratory Rate (bpm)", min_value=10, max_value=40, step=1, value=None)

    # Body Temperature Input with Toggle Slider for Unit Selection
    st.write("Body Temperature")
    col1, col2 = st.columns([1, 3])  # Split into two columns
    with col1:
        # Toggle slider for unit selection
        temp_unit = st.radio("Unit", ["Celsius (°C)", "Fahrenheit (°F)"], horizontal=True)
    with col2:
        # Number input for body temperature
        if temp_unit == "Celsius (°C)":
            body_temperature = st.number_input("Temperature (°C)", min_value=30.0, max_value=42.0, step=0.1, value=36.5)
        else:
            body_temperature = st.number_input("Temperature (°F)", min_value=86.0, max_value=107.6, step=0.1, value=97.7)

    # Consciousness Field
    consciousness_options = ["Alert", "Verbal Response", "Pain Response", "Unresponsive"]
    consciousness = st.radio("Consciousness", consciousness_options, index=0)

    # Mode of Transport Field
    transport_options = ["Walk", "Public Ambulance", "Private Vehicle", "Private Ambulance", "No Selection"]
    transport = st.radio("Mode of Transport", transport_options, index=4)
    if transport == "No Selection":
        transport = None

    # Image Upload or Capture
    option = st.radio(
        "Choose an option:",
        ("Upload a photo", "Take a photo"),
        horizontal=True,  # Display options horizontally
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
        age = 0 if age is None else age
        pain_level = 0 if pain_level is None else pain_level
        bp_systolic = 0 if bp_systolic is None else bp_systolic
        bp_diastolic = 0 if bp_diastolic is None else bp_diastolic
        heart_rate = 0 if heart_rate is None else heart_rate
        oxygen_saturation = 0 if oxygen_saturation is None else oxygen_saturation
        respiratory_rate = 0 if respiratory_rate is None else respiratory_rate
        body_temperature = 0 if body_temperature is None else body_temperature
        sex = "No Selection" if sex is None else sex
        consciousness = "Unknown" if consciousness is None else consciousness
        transport = "No Selection" if transport is None else transport

        # Convert body temperature to Celsius
        body_temperature_celsius = convert_to_celsius(body_temperature, temp_unit)

        image_description = "No image provided."
        if image is not None:
            image_description = analyze_image(image)

        # Create input data for the model
        input_data = pd.DataFrame({
            'Sex': [map_sex(sex)],
            'Age': [age],
            'Arrival mode': [map_transport(transport)],
            'Injury': [map_injury(description)],
            'Mental': [map_consciousness(consciousness)],
            'Pain': [map_pain(pain_level)],  # Updated pain mapping
            'SBP': [bp_systolic],
            'DBP': [bp_diastolic],
            'HR': [heart_rate],
            'RR': [respiratory_rate],
            'BT': [body_temperature_celsius],  # Use converted temperature
        })

        # Ensure the input data has the same columns as the training data
        input_data = input_data.reindex(columns=feature_names, fill_value=0)

        # Make the prediction using the machine learning model
        ml_triage_level = predict_with_ml_model(input_data)

        # Groq Prediction
        query = ("Give the triage level based on the following info. Description: " + str(description)
                 + ", Description of the image of the patient: " + str(image_description)
                 + ", Pain Level: " + str(pain_level)
                 + ", BP: " + str(bp_systolic) + "/" + str(bp_diastolic)
                 + ", Heart Rate: " + str(heart_rate)
                 + ", Oxygen Saturation: " + str(oxygen_saturation)
                 + ", Respiratory Rate: " + str(respiratory_rate)
                 + ", Body Temperature: " + str(body_temperature_celsius) + "°C"  # Display in Celsius
                 + ", Sex: " + str(sex)
                 + ", Consciousness: " + str(consciousness)
                 + ", Mode of Transport: " + str(transport)
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
        groq_triage_level = response.split(";")[0]
        groq_triage_description = response.split(";")[1]

        # Calculate the recommended triage level
        recommended_triage = calculate_recommended_triage(groq_triage_level, ml_triage_level)

        # Display Predictions
        st.subheader("Recommended Triage")
        recommended_triage_color = get_triage_color(str(recommended_triage))
        st.markdown(
            f"""
                    <div style="
                        background-color: {recommended_triage_color};
                        padding: 20px;
                        border-radius: 10px;
                        text-align: center;
                        font-size: 24px;
                        color: black;
                        font-weight: bold;
                    ">
                        Recommended Triage Level: {recommended_triage}
                    </div>
                    """,
            unsafe_allow_html=True,
        )

        
        st.subheader("Groq Prediction")
        groq_triage_color = get_triage_color(groq_triage_level)
        st.markdown(
            f"""
            <div style="
                background-color: {groq_triage_color};
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                font-size: 24px;
                color: black;
                font-weight: bold;
            ">
                Triage Level: {groq_triage_level}
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
                {groq_triage_description}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.subheader("Machine Learning Model Prediction")
        ml_triage_color = get_triage_color(str(ml_triage_level))
        st.markdown(
            f"""
            <div style="
                background-color: {ml_triage_color};
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                font-size: 24px;
                color: black;
                font-weight: bold;
            ">
                Triage Level: {ml_triage_level}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.session_state.triage_requests.append({
            "triage_level": recommended_triage,
            "description": description,
            "triage_description": groq_triage_description,
        })

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
