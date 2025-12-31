import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
import datetime
import time

# --- IMPORTS (Voice, SMS, DB) ---
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
import io
from twilio.rest import Client
import pymongo
# -----------------------------------

# -----------------------------------------------------------------------------
# 1. APP CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Agri-Smart BD | এআই মূল্য পূর্বাভাস",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Enhanced Professional Dashboard Design
st.markdown("""
    <style>
    /* Main background with gradient */
    .main {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        background-attachment: fixed;
    }
    
    /* Content area styling */
    .block-container {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin-top: 1rem;
    }
    
    /* Headers */
    h1 {
        color: #1a1a1a !important;
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    h2, h3 {
        color: #2c3e50 !important;
        font-weight: 600 !important;
    }
    
    /* All text elements */
    p, span, div, label, .stMarkdown {
        color: #1a1a1a !important;
    }
    
    /* Metric styling with gradient backgrounds */
    [data-testid="stMetricValue"] {
        color: #1a1a1a !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #2c3e50 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    [data-testid="stMetricDelta"] {
        color: #1a1a1a !important;
    }
    
    /* Cards effect for metrics */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    [data-testid="stMetric"] [data-testid="stMetricLabel"],
    [data-testid="stMetric"] [data-testid="stMetricValue"],
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #ffffff !important;
    }
    
    /* Success/Info/Warning boxes */
    .stSuccess, .stInfo, .stWarning {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        border-left: 5px solid #28a745 !important;
    }
    
    .stSuccess > div, .stInfo > div, .stWarning > div {
        color: #1a1a1a !important;
        font-weight: 500 !important;
    }
    
    .stInfo {
        border-left-color: #17a2b8 !important;
    }
    
    .stWarning {
        border-left-color: #ffc107 !important;
    }
    
    /* Selectbox and input styling */
    .stSelectbox label, .stTextInput label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    /* Selectbox dropdown styling */
    .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid #11998e !important;
        border-radius: 8px !important;
    }
    
    /* Selectbox selected value */
    .stSelectbox [data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #1a1a1a !important;
    }
    
    /* Dropdown menu options list */
    [data-baseweb="popover"] {
        background-color: #ffffff !important;
    }
    
    [data-baseweb="menu"] {
        background-color: #ffffff !important;
    }
    
    /* Individual dropdown options */
    [role="option"] {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    
    /* Dropdown option on hover */
    [role="option"]:hover {
        background-color: #11998e !important;
        color: #ffffff !important;
    }
    
    /* Selected option in dropdown */
    [aria-selected="true"] {
        background-color: #38ef7d !important;
        color: #ffffff !important;
    }
    
    /* Radio buttons */
    .stRadio label {
        color: #1a1a1a !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f5132 0%, #198754 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stRadio label {
        color: #ffffff !important;
    }
    
    /* Divider */
    hr {
        border-color: rgba(0,0,0,0.1) !important;
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        transition: transform 0.2s;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.3);
    }
    
    /* Footer styling */
    footer {
        color: #1a1a1a !important;
    }
    
    /* Plotly charts */
    .js-plotly-plot {
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    /* Login Box Styling */
    .login-box {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. DATABASE CONNECTION (MONGODB)
# -----------------------------------------------------------------------------
# NOTE: Replace this URI with your actual MongoDB Connection String
# Example: "mongodb+srv://<username>:<password>@cluster0.xyz.mongodb.net/?retryWrites=true&w=majority"
# For Hackathon demo without setup, I will use a local list fallback if connection fails.

MONGO_URI = "mongodb+srv://admin:admin123@cluster0.xyz.mongodb.net/?retryWrites=true&w=majority" 

@st.cache_resource
def init_connection():
    try:
        # Connect to MongoDB
        # client = pymongo.MongoClient(MONGO_URI) # Uncomment this when you have real URI
        # return client
        return None # Returning None for demo purpose (In-memory mock)
    except:
        return None

client = init_connection()

# Mock Database for Demo (If MongoDB is not connected)
# Use cache_resource to persist across reruns
@st.cache_resource
def get_mock_db():
    return []

mock_db = get_mock_db()

def get_user(phone):
    """Fetch user from DB"""
    # Real Mongo Implementation:
    # db = client.agri_smart
    # return db.users.find_one({"phone": phone})
    
    # Mock Implementation:
    for user in mock_db:
        if user['phone'] == phone:
            return user
    return None

def create_user(name, phone, district):
    """Insert new user to DB"""
    user_data = {"name": name, "phone": phone, "district": district}
    
    # Real Mongo Implementation:
    # db = client.agri_smart
    # db.users.insert_one(user_data)
    
    # Mock Implementation:
    mock_db.append(user_data)
    return True

# -----------------------------------------------------------------------------
# 3. DATA LOADING FUNCTIONS
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        price_df = pd.read_csv('bd_crop_price_data.csv')
        prod_df = pd.read_csv('bd_crop_production_data.csv')
        soil_df = pd.read_csv('bd_soil_analysis_data.csv')
        price_df['Price_Date'] = pd.to_datetime(price_df['Price_Date'])
        return price_df, prod_df, soil_df
    except FileNotFoundError:
        return None, None, None

price_df, prod_df, soil_df = load_data()

# Dictionaries (Translation)
district_translation = {
    'Dhaka': 'ঢাকা', 'Chittagong': 'চট্টগ্রাম', 'Rajshahi': 'রাজশাহী', 'Khulna': 'খুলনা',
    'Barisal': 'বরিশাল', 'Sylhet': 'সিলেট', 'Rangpur': 'রংপুর', 'Mymensingh': 'ময়মনসিংহ',
    'Comilla': 'কুমিল্লা', 'Gazipur': 'গাজীপুর', 'Narayanganj': 'নারায়ণগঞ্জ', 'Tangail': 'টাঙ্গাইল',
    'Jamalpur': 'জামালপুর', 'Bogra': 'বগুড়া', 'Pabna': 'পাবনা', 'Jessore': 'যশোর',
    'Dinajpur': 'দিনাজপুর', 'Faridpur': 'ফরিদপুর', 'Kushtia': 'কুষ্টিয়া', 'Noakhali': 'নোয়াখালী',
    'Brahmanbaria': 'ব্রাহ্মণবাড়িয়া', 'Feni': 'ফেনী', 'Lakshmipur': 'লক্ষ্মীপুর', 'Chandpur': 'চাঁদপুর',
    'Kishoreganj': 'কিশোরগঞ্জ', 'Netrokona': 'নেত্রকোনা', 'Sherpur': 'শেরপুর', 'Habiganj': 'হবিগঞ্জ',
    'Moulvibazar': 'মৌলভীবাজার', 'Sunamganj': 'সুনামগঞ্জ', 'Narsingdi': 'নরসিংদী', 'Munshiganj': 'মুন্সিগঞ্জ',
    'Manikganj': 'মানিকগঞ্জ', 'Gopalganj': 'গোপালগঞ্জ', 'Madaripur': 'মাদারীপুর', 'Shariatpur': 'শরীয়তপুর',
    'Rajbari': 'রাজবাড়ী', 'Magura': 'মাগুরা', 'Jhenaidah': 'ঝিনাইদহ', 'Narail': 'নড়াইল',
    'Satkhira': 'সাতক্ষীরা', 'Bagerhat': 'বাগেরহাট', 'Pirojpur': 'পিরোজপুর', 'Jhalokati': 'ঝালকাঠি',
    'Patuakhali': 'পটুয়াখালী', 'Barguna': 'বরগুনা', 'Sirajganj': 'সিরাজগঞ্জ', 'Natore': 'নাটোর',
    'Chapainawabganj': 'চাঁপাইনবাবগঞ্জ', 'Naogaon': 'নওগাঁ', 'Joypurhat': 'জয়পুরহাট', 'Gaibandha': 'গাইবান্ধা',
    'Kurigram': 'কুড়িগ্রাম', 'Lalmonirhat': 'লালমনিরহাট', 'Nilphamari': 'নীলফামারী', 'Panchagarh': 'পঞ্চগড়',
    'Thakurgaon': 'ঠাকুরগাঁও', 'Coxs Bazar': 'কক্সবাজার', 'Bandarban': 'বান্দরবান', 'Rangamati': 'রাঙ্গামাটি',
    'Khagrachari': 'খাগড়াছড়ি', 'Meherpur': 'মেহেরপুর', 'Chuadanga': 'চুয়াডাঙ্গা', 'Cumilla': 'কুমিল্লা'
}
crop_translation = {
    'Rice': 'ধান', 'Wheat': 'গম', 'Jute': 'পাট', 'Potato': 'আলু', 'Onion': 'পেঁয়াজ',
    'Garlic': 'রসুন', 'Lentil': 'ডাল', 'Mustard': 'সরিষা', 'Tomato': 'টমেটো',
    'Eggplant': 'বেগুন', 'Cabbage': 'বাঁধাকপি', 'Cauliflower': 'ফুলকপি', 'Chili': 'মরিচ',
    'Cucumber': 'শসা', 'Pumpkin': 'কুমড়া', 'Bitter Gourd': 'করলা', 'Bottle Gourd': 'লাউ',
    'Okra': 'ঢেঁড়স', 'Spinach': 'পালং শাক', 'Coriander': 'ধনিয়া', 'Maize': 'ভুট্টা',
    'Sugarcane': 'আখ', 'Tea': 'চা', 'Mango': 'আম', 'Banana': 'কলা', 'Jackfruit': 'কাঁঠাল',
    'Papaya': 'পেঁপে', 'Guava': 'পেয়ারা', 'Lychee': 'লিচু', 'Pineapple': 'আনারস',
    'Bajra': 'বাজরা', 'Barley': 'যব', 'Chilli': 'মরিচ', 'Citrus': 'লেবুজাতীয় ফল',    
    'Cotton': 'তুলা', 'Cumin': 'জিরা', 'Fennel': 'মৌরি', 'Fenugreek': 'মেথি',
    'Gram': 'ছোলা', 'Oilseeds': 'তেলবীজ', 'Opium': 'আফিম', 'Pomegranate': 'ডালিম', 'Pulses': 'ডালশস্য' 
}
soil_translation = {
    'Clay': 'কর্দম মাটি', 'Loamy': 'দোআঁশ মাটি', 'Sandy': 'বেলে মাটি', 'Silt': 'পলি মাটি',
    'Clay Loam': 'কর্দম দোআঁশ', 'Sandy Loam': 'বেলে দোআঁশ', 'Silty Clay': 'পলি কর্দম',
    'Silty Loam': 'পলি দোআঁশ', 'Peat': 'পিট মাটি', 'Chalky (Calcareous)': 'চুনযুক্ত মাটি',
    'Nitrogenous': 'নাইট্রোজেন সমৃদ্ধ', 'Black lava soil': 'কালো লাভা মাটি'
}
def translate_bn(text, translation_dict):
    return translation_dict.get(text, text)
def to_bengali_number(number):
    bengali_digits = {'0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪', '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯', '.': '.'}
    return ''.join(bengali_digits.get(char, char) for char in str(number))

# -----------------------------------------------------------------------------
# 4. AUTHENTICATION LOGIC (TOP RIGHT)
# -----------------------------------------------------------------------------
if 'user' not in st.session_state:
    st.session_state.user = None

# Create a Top Bar Layout
col_logo, col_auth = st.columns([3, 1])

with col_logo:
    st.title("🌾 Agri-Smart BD")

# Auth UI Logic
with col_auth:
    if st.session_state.user:
        # If Logged In
        st.markdown(f"👤 **{st.session_state.user['name']}**")
        if st.button("Logout"):
            st.session_state.user = None
            st.rerun()
    else:
        # If Not Logged In
        with st.popover("🔐 Login / Sign Up"):
            tab1, tab2 = st.tabs(["Login", "Sign Up"])
            
            with tab1:
                st.subheader("লগইন করুন")
                login_phone = st.text_input("মোবাইল নম্বর", key="login_phone")
                if st.button("Login", type="primary"):
                    user = get_user(login_phone)
                    if user:
                        st.session_state.user = user
                        st.success("লগইন সফল!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("নম্বরটি নিবন্ধিত নয়। অনুগ্রহ করে সাইন আপ করুন।")
            
            with tab2:
                st.subheader("নিবন্ধন করুন")
                reg_name = st.text_input("নাম")
                reg_phone = st.text_input("মোবাইল নম্বর", key="reg_phone")
                
                # District List
                district_list = sorted(price_df['District_Name'].unique())
                district_display = {dist: translate_bn(dist, district_translation) for dist in district_list}
                reg_district_bn = st.selectbox("জেলা নির্বাচন করুন", options=list(district_display.values()))
                reg_district = [k for k, v in district_display.items() if v == reg_district_bn][0]
                
                if st.button("Sign Up", type="primary"):
                    if reg_name and reg_phone:
                        existing = get_user(reg_phone)
                        if existing:
                            st.warning("এই নম্বরটি ইতিমধ্যে নিবন্ধিত।")
                        else:
                            create_user(reg_name, reg_phone, reg_district)
                            st.session_state.user = {"name": reg_name, "phone": reg_phone, "district": reg_district}
                            st.success("নিবন্ধন সফল!")
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.warning("সব তথ্য পূরণ করুন।")

# -----------------------------------------------------------------------------
# 5. MAIN APP CONTENT (Protected or Public)
# -----------------------------------------------------------------------------
# You can choose to hide the whole app if not logged in, or just show it.
# For this request, I will show the app but personalize it if logged in.

if price_df is None:
    st.error("🚨 ডেটাসেট পাওয়া যায়নি!")
    st.stop()

# Helpers
def voice_to_text(audio_bytes):
    r = sr.Recognizer()
    try:
        audio_file = sr.AudioFile(io.BytesIO(audio_bytes))
        with audio_file as source:
            audio_data = r.record(source)
        text = r.recognize_google(audio_data, language='bn-BD')
        return text
    except:
        return None

def send_sms_alert(to_number, message_body):
    try:
        account_sid = st.secrets.get("TWILIO_ACCOUNT_SID", "")
        auth_token = st.secrets.get("TWILIO_AUTH_TOKEN", "")
        from_number = st.secrets.get("TWILIO_PHONE_NUMBER", "")
        
        if not all([account_sid, auth_token, from_number]):
            return False, "Twilio credentials not configured"
        
        client = Client(account_sid, auth_token)
        message = client.messages.create(body=message_body, from_=from_number, to=to_number)
        return True, message.sid
    except Exception as e:
        return False, str(e)

def get_market_insights(df, current_district, current_crop, days_ahead=7):
    # (Same simplified logic as before)
    insights = {'best_crops_in_district': [], 'best_districts_for_crop': []}
    
    dist_data = df[df['District_Name'] == current_district]
    if not dist_data.empty:
        for crop in dist_data['Crop_Name'].unique():
            crop_df = dist_data[dist_data['Crop_Name'] == crop].sort_values('Price_Date')
            if len(crop_df) > 5:
                try:
                    current_p = crop_df.iloc[-1]['Price_Tk_kg']
                    insights['best_crops_in_district'].append((crop, current_p))
                except: continue
        insights['best_crops_in_district'].sort(key=lambda x: x[1], reverse=True)
        insights['best_crops_in_district'] = insights['best_crops_in_district'][:3]

    crop_data = df[df['Crop_Name'] == current_crop]
    if not crop_data.empty:
        for dist in crop_data['District_Name'].unique():
            dist_df = crop_data[crop_data['District_Name'] == dist].sort_values('Price_Date')
            if len(dist_df) > 5:
                try:
                    current_p = dist_df.iloc[-1]['Price_Tk_kg']
                    insights['best_districts_for_crop'].append((dist, current_p))
                except: continue
        insights['best_districts_for_crop'].sort(key=lambda x: x[1], reverse=True)
        insights['best_districts_for_crop'] = insights['best_districts_for_crop'][:3]
        
    return insights

def get_crop_reasoning(soil_record, crop, yield_val):
    """
    Generate reasoning for why a crop is recommended based on soil conditions
    """
    soil_type = soil_record['Soil_Type']
    ph = soil_record['pH_Level']
    nitrogen = soil_record['Nitrogen_Content_kg_ha']
    organic = soil_record['Organic_Matter_Percent']
    
    reasoning = f"এই অঞ্চলে {crop} চাষের ঐতিহাসিক সাফল্য রয়েছে। "
    
    # pH-based reasoning
    if 6.0 <= ph <= 7.5:
        reasoning += "মাটির পিএইচ স্তর আদর্শ পরিসরে রয়েছে যা এই ফসলের জন্য উপযুক্ত। "
    elif ph < 6.0:
        reasoning += "মাটি কিছুটা অম্লীয় তবে এই ফসল তাতে মানানসই হতে পারে। "
    else:
        reasoning += "মাটি ক্ষারীয় প্রকৃতির, তবে এই ফসল তাতে ভালো জন্মায়। "
    
    # Nitrogen content reasoning
    if nitrogen > 150:
        reasoning += "উচ্চ নাইট্রোজেন সামগ্রী ফসলের বৃদ্ধিতে সহায়ক। "
    elif nitrogen > 100:
        reasoning += "মাঝারি নাইট্রোজেন স্তর পর্যাপ্ত। "
    else:
        reasoning += "নাইট্রোজেন সার প্রয়োগ বিবেচনা করুন। "
    
    # Organic matter reasoning
    if organic > 2.0:
        reasoning += f"উচ্চ জৈব পদার্থ ({organic:.1f}%) মাটির উর্বরতা নিশ্চিত করে। "
    
    # Yield-based reasoning
    reasoning += f"ঐতিহাসিক তথ্য অনুযায়ী, গড় ফলন {yield_val:.1f} কুইন্টাল/হেক্টর অর্জন করা সম্ভব।"
    
    return reasoning

# --- Sidebar ---
st.sidebar.markdown("**এআই চালিত কৃষি বুদ্ধিমত্তা**")
menu = st.sidebar.radio("মডিউল নির্বাচন করুন:", ["📊 মূল্য পূর্বাভাস (এআই)", "💰 সেরা বাজার খুঁজুন", "🌱 মাটি ও ফসল পরামর্শদাতা"])

# -----------------------------------------------------------------------------
# MODULE 1: AI PRICE FORECASTING
# -----------------------------------------------------------------------------
if menu == "📊 মূল্য পূর্বাভাস (এআই)":
    st.markdown("### মেশিন লার্নিং ব্যবহার করে ৩০ দিনের আগাম মূল্যের পূর্বাভাস।")
    
    # Auto-select district if logged in
    district_list = sorted(price_df['District_Name'].unique())
    district_display = {dist: translate_bn(dist, district_translation) for dist in district_list}
    district_options_list = list(district_display.values())
    
    # Session State Logic for District
    if 'selected_district_val' not in st.session_state:
        # Default to User's District if logged in
        if st.session_state.user:
            user_dist_bn = translate_bn(st.session_state.user['district'], district_translation)
            if user_dist_bn in district_options_list:
                st.session_state.selected_district_val = user_dist_bn
            else:
                st.session_state.selected_district_val = district_options_list[0]
        else:
            st.session_state.selected_district_val = district_options_list[0]

    # Voice Input
    c1, c2 = st.columns([1, 4])
    with c1:
        audio = mic_recorder(start_prompt="🎤 বলুন", stop_prompt="🛑 থামুন", key='recorder', format="wav", use_container_width=True)
    
    voice_text = ""
    if audio:
        with st.spinner("প্রসেস হচ্ছে..."):
            voice_text = voice_to_text(audio['bytes'])
        if voice_text:
            st.success(f"🗣️ আপনি বলেছেন: **'{voice_text}'**")
            for dist_bn in district_options_list:
                if dist_bn in voice_text:
                    st.session_state.selected_district_val = dist_bn
                    st.toast(f"✅ জেলা শনাক্ত হয়েছে: {dist_bn}")
                    break
    
    st.divider()

    # Inputs
    col1, col2 = st.columns(2)
    with col1:
        selected_district_bn = st.selectbox("📍 জেলা নির্বাচন করুন", options=district_options_list, key='selected_district_val')
        selected_district = [k for k, v in district_display.items() if v == selected_district_bn][0]
    
    with col2:
        available_crops = sorted(price_df[price_df['District_Name'] == selected_district]['Crop_Name'].unique())
        crop_display = {crop: translate_bn(crop, crop_translation) for crop in available_crops}
        crop_options_list = list(crop_display.values())
        
        crop_index = 0
        if voice_text:
            for i, crop_bn in enumerate(crop_options_list):
                if crop_bn in voice_text:
                    crop_index = i
                    break
        
        selected_crop_bn = st.selectbox("🌽 ফসল নির্বাচন করুন", options=crop_options_list, index=crop_index, format_func=lambda x: x)
        selected_crop = [k for k, v in crop_display.items() if v == selected_crop_bn][0]

    # Analysis & Prediction
    filtered_df = price_df[(price_df['District_Name'] == selected_district) & (price_df['Crop_Name'] == selected_crop)].sort_values('Price_Date')

    if len(filtered_df) > 10:
        # Feature Engineering
        filtered_df['Date_Ordinal'] = filtered_df['Price_Date'].map(datetime.datetime.toordinal)
        filtered_df['Month'] = filtered_df['Price_Date'].dt.month
        filtered_df['Week'] = filtered_df['Price_Date'].dt.isocalendar().week
        filtered_df['Year'] = filtered_df['Price_Date'].dt.year
        
        X = filtered_df[['Date_Ordinal', 'Month', 'Week', 'Year']]
        y = filtered_df['Price_Tk_kg']
        model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        model.fit(X, y)
        
        last_date = filtered_df['Price_Date'].max()
        future_dates = [last_date + datetime.timedelta(days=i) for i in range(1, 31)]
        future_data = pd.DataFrame({'Price_Date': future_dates})
        future_data['Date_Ordinal'] = future_data['Price_Date'].map(datetime.datetime.toordinal)
        future_data['Month'] = future_data['Price_Date'].dt.month
        future_data['Week'] = future_data['Price_Date'].dt.isocalendar().week
        future_data['Year'] = future_data['Price_Date'].dt.year
        
        # Get predictions with confidence intervals
        predictions = model.predict(future_data[['Date_Ordinal', 'Month', 'Week', 'Year']])
        
        # Calculate confidence intervals using tree predictions
        tree_predictions = np.array([tree.predict(future_data[['Date_Ordinal', 'Month', 'Week', 'Year']]) for tree in model.estimators_])
        std_predictions = tree_predictions.std(axis=0)
        
        future_data['Predicted_Price'] = predictions
        future_data['Upper_Bound'] = predictions + 1.96 * std_predictions
        future_data['Lower_Bound'] = predictions - 1.96 * std_predictions
        
        # Plot with confidence intervals
        st.subheader(f"মূল্য প্রবণতা: {translate_bn(selected_crop, crop_translation)}")
        fig = go.Figure()
        
        # Historical data
        fig.add_trace(go.Scatter(
            x=filtered_df['Price_Date'], 
            y=filtered_df['Price_Tk_kg'], 
            mode='lines', 
            name='ঐতিহাসিক', 
            line=dict(color='#1f77b4', width=2)
        ))
        
        # Predicted data
        fig.add_trace(go.Scatter(
            x=future_data['Price_Date'], 
            y=future_data['Predicted_Price'], 
            mode='lines', 
            name='পূর্বাভাস', 
            line=dict(color='#00cc96', width=2)
        ))
        
        # Confidence interval upper bound
        fig.add_trace(go.Scatter(
            x=future_data['Price_Date'],
            y=future_data['Upper_Bound'],
            mode='lines',
            name='উর্ধ্ব সীমা',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Confidence interval lower bound with fill
        fig.add_trace(go.Scatter(
            x=future_data['Price_Date'],
            y=future_data['Lower_Bound'],
            mode='lines',
            name='নিম্ন সীমা',
            line=dict(width=0),
            fillcolor='rgba(0, 204, 150, 0.2)',
            fill='tonexty',
            showlegend=True,
            hoverinfo='skip'
        ))
        
        fig.update_layout(
            xaxis_title='তারিখ',
            yaxis_title='মূল্য (৳/কেজি)',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)

        current_price = filtered_df.iloc[-1]['Price_Tk_kg']
        avg_price = predictions.mean()
        trend = "উর্ধ্বমুখী 📈" if avg_price > current_price else "নিম্নমুখী 📉"
        
        m1, m2, m3 = st.columns(3)
        m1.metric("বর্তমান মূল্য", f"৳ {to_bengali_number(f'{current_price:.2f}')}")
        m2.metric("গড় পূর্বাভাস", f"৳ {to_bengali_number(f'{avg_price:.2f}')}")
        m3.metric("প্রবণতা", trend)

        # SMS Alert Section (Personalized)
        st.markdown("---")
        st.subheader("📲 স্মার্ট এসএমএস অ্যালার্ট")
        
        c_sms1, c_sms2 = st.columns([2, 1])
        with c_sms1:
            # Autofill phone number if logged in
            default_phone = st.session_state.user['phone'] if st.session_state.user else "+18777804236"
            phone_number = st.text_input("মোবাইল নম্বর", value=default_phone)
        
        with c_sms2:
            st.write("")
            st.write("")
            send_btn = st.button("🚀 পাঠান", type="primary", use_container_width=True)
            
        if send_btn:
            # Login check enforcement (Optional, but adds value)
            if not st.session_state.user:
                st.warning("⚠️ অনুগ্রহ করে এসএমএস পেতে লগইন করুন।")
            else:
                with st.spinner("অ্যালার্ট জেনারেট হচ্ছে..."):
                    insights = get_market_insights(price_df, selected_district, selected_crop)
                    
                    msg = f"সতর্কতা: {selected_district_bn}তে {selected_crop_bn} ৳{int(current_price)}।"
                    if insights['best_districts_for_crop']:
                        top_dist, top_price = insights['best_districts_for_crop'][0]
                        if top_price > current_price:
                            d_bn = translate_bn(top_dist, district_translation)
                            msg += f" বেশি দাম: {d_bn}তে ৳{int(top_price)}।"
                        else:
                            msg += " এখানের দামই সেরা।"
                    msg += " -AgriSmart"
                    msg = msg[:158]
                    
                    success, response = send_sms_alert(phone_number, msg)
                    if success:
                        st.success("✅ এসএমএস পাঠানো হয়েছে!")
                        st.balloons()
                    else:
                        st.error(f"❌ ব্যর্থ: {response}")

# -----------------------------------------------------------------------------
# MODULE 2: BEST MARKET FINDER
# -----------------------------------------------------------------------------
elif menu == "💰 সেরা বাজার খুঁজুন":
    st.title("💰 সেরা বাজার খুঁজুন")
    st.divider()

    all_crops = sorted(price_df['Crop_Name'].unique())
    all_crops_display = {crop: translate_bn(crop, crop_translation) for crop in all_crops}
    target_crop_bn = st.selectbox("🔍 ফসল নির্বাচন করুন", options=list(all_crops_display.values()))
    target_crop = [k for k, v in all_crops_display.items() if v == target_crop_bn][0]

    transport_cost = st.number_input("পরিবহন খরচ (টাকা/কেজি)", min_value=0.0, value=2.0)

    latest_date = price_df['Price_Date'].max()
    recent_data = price_df[(price_df['Crop_Name'] == target_crop) & (price_df['Price_Date'] >= latest_date - datetime.timedelta(days=60))]
    market_data = recent_data.sort_values('Price_Date').groupby('District_Name').tail(1).copy()

    if not market_data.empty:
        market_data['Net_Profit'] = market_data['Price_Tk_kg'] - transport_cost
        best_market = market_data.sort_values('Net_Profit', ascending=False).iloc[0]
        
        # Enhanced Net Profit Visualization with highlighted card
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; 
                    border-radius: 15px; 
                    box-shadow: 0 10px 25px rgba(0,0,0,0.3);
                    text-align: center;
                    margin: 1rem 0;'>
            <h2 style='color: white; margin: 0; font-size: 1.5rem;'>🏆 সেরা বাজার</h2>
            <h1 style='color: #FFD700; margin: 0.5rem 0; font-size: 2.5rem;'>{translate_bn(best_market['District_Name'], district_translation)}</h1>
            <h3 style='color: white; margin: 0;'>নিট লাভ: ৳{to_bengali_number(f"{best_market['Net_Profit']:.2f}")}/কেজি</h3>
            <p style='color: rgba(255,255,255,0.9); margin-top: 1rem;'>মূল্য: ৳{to_bengali_number(f"{best_market['Price_Tk_kg']:.2f}")} | পরিবহন: ৳{to_bengali_number(f"{transport_cost:.2f}")}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("📊 সকল জেলার তুলনা")
        fig = px.bar(
            market_data.sort_values('Net_Profit', ascending=True), 
            x='Net_Profit', 
            y='District_Name', 
            orientation='h', 
            color='Net_Profit', 
            color_continuous_scale='Greens',
            labels={'Net_Profit': 'নিট লাভ (৳/কেজি)', 'District_Name': 'জেলা'}
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------------------
# MODULE 3: SOIL ADVISOR
# -----------------------------------------------------------------------------
elif menu == "🌱 মাটি ও ফসল পরামর্শদাতা":
    st.title("🌱 ফসল পরামর্শদাতা")
    st.divider()

    soil_districts = sorted(soil_df['District_Name'].unique())
    soil_district_display = {dist: translate_bn(dist, district_translation) for dist in soil_districts}
    
    # Auto-select if logged in
    default_idx = 0
    if st.session_state.user:
        u_dist = translate_bn(st.session_state.user['district'], district_translation)
        vals = list(soil_district_display.values())
        if u_dist in vals:
            default_idx = vals.index(u_dist)

    target_district_bn = st.selectbox("📍 অবস্থান নির্বাচন করুন", options=list(soil_district_display.values()), index=default_idx)
    target_district = [k for k, v in soil_district_display.items() if v == target_district_bn][0]

    soil_record = soil_df[soil_df['District_Name'] == target_district].iloc[0]
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("মাটি", translate_bn(soil_record['Soil_Type'], soil_translation))
    c2.metric("পিএইচ", to_bengali_number(f"{soil_record['pH_Level']:.2f}"))
    c3.metric("নাইট্রোজেন", f"{to_bengali_number(f'{soil_record['Nitrogen_Content_kg_ha']:.1f}')}")
    c4.metric("জৈব", f"{to_bengali_number(f'{soil_record['Organic_Matter_Percent']:.1f}')}%")

    st.subheader("🌾 সুপারিশকৃত ফসল")
    dist_prod = prod_df[prod_df['District_Name'] == target_district]
    top_crops = dist_prod.groupby('Crop_Name')['Yield_Quintals_per_Ha'].mean().sort_values(ascending=False).head(5)

    # Enhanced crop recommendations with reasoning
    for idx, (crop, yield_val) in enumerate(top_crops.items(), 1):
        # Get reasoning based on soil conditions
        reasoning = get_crop_reasoning(soil_record, crop, yield_val)
        
        with st.expander(f"#{idx} {translate_bn(crop, crop_translation)} - ঐতিহাসিক ফলন: {to_bengali_number(f'{yield_val:.1f}')} কুইন্টাল/হেক্টর"):
            st.markdown(f"**কেন এই ফসলটি উপযুক্ত:**")
            st.write(reasoning)

# Footer
st.markdown("<br><hr><div style='text-align: center; color: #555;'>Agri-Smart BD | Built for AI Build-a-thon 2025</div>", unsafe_allow_html=True)