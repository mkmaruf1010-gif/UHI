import streamlit as st

import geemap.foliumap as geemap
from streamlit_folium import st_folium
import json

# ১. প্রোডাকশন-রেডি সিকিউর অথেন্টিকেশন (Streamlit Secrets ব্যবহার করে)
@st.cache_resource
def authenticate_ee():
    try:
        # Streamlit Cloud-এর Secrets থেকে ক্রেডেনশিয়াল রিড করা
        ee_secrets = st.secrets["gcp_service_account"]
        credentials = ee.ServiceAccountCredentials(
            ee_secrets["client_email"], 
            key_data=ee_secrets["private_key"]
        )
        ee.Initialize(credentials=credentials)
    except Exception as e:
        # লোকাল কম্পিউটারে টেস্ট করার জন্য ব্যাকআপ অপশন
        ee.Initialize()

authenticate_ee()

# ২. ওয়েব ইন্টারফেস ডিজাইন
st.set_page_config(layout="wide")
st.title("🛰️ আরবান হিট আইল্যান্ড (UHI) মিটিগেশন সিমুলেটর")
st.sidebar.header("🛠️ সিমুলেশন প্যারামিটার")

# বাস্তব ভিত্তিক স্লাইডার রেঞ্জ
ndvi_change = st.sidebar.slider("সবুজায়ন বৃদ্ধি (Δ NDVI)", 0.00, 0.40, 0.05, step=0.01)
albedo_change = st.sidebar.slider("ছাদের রিফ্লেক্টিভিটি বৃদ্ধি (Δ Albedo)", 0.00, 0.30, 0.00, step=0.01)

# ৩. রিগ্রেশন মডেল থেকে প্রাপ্ত কো-অফিসিয়েন্ট (বাস্তব রিসার্চের মান অনুযায়ী পরিবর্তনযোগ্য)
# উদাহরণস্বরূপ: ১ ইউনিট NDVI বাড়লে তাপমাত্রা ৫.৪ ডিগ্রি কমে, ১ ইউনিট অ্যালবেডো বাড়লে ৩.২ ডিগ্রি কমে
BETA_1 = -5.42 
BETA_2 = -3.25

# ৪. ম্যাপ এবং ডেটা প্রসেসিং (স্টাডি এরিয়া: ঢাকা)
Map = geemap.Map(center=[23.8103, 90.4125], zoom=11)

point = ee.Geometry.Point([90.4125, 23.8103])
# ২০২৫ সালের ল্যান্ডস্যাট ৮ ইমেজারি ব্যবহার
landsat = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2") \
    .filterBounds(point) \
    .filterDate('2025-01-01', '2025-12-31') \
    .filter(ee.Filter.lt('CLOUD_COVER', 10)) \
    .median()

# বেসলাইন LST ক্যালকুলেশন (Celsius)
base_lst = landsat.select('ST_B10').multiply(0.00341802).add(149.0).subtract(273.15)

# ৫. সিমুলেশন ম্যাথ (Live Predictive Modeling)
# ΔLST = (BETA_1 * ΔNDVI) + (BETA_2 * ΔAlbedo)
lst_reduction = ee.Image(ndvi_change).multiply(BETA_1).add(ee.Image(albedo_change).multiply(BETA_2))
simulated_lst = base_lst.add(lst_reduction) # যেহেতু বিটা মান নেগেটিভ, তাই যোগ করলেই তাপমাত্রা কমবে

# ৬. ভিজ্যুয়ালাইজেশন
vis_params = {
    'min': 22, 
    'max': 42, 
    'palette': ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
}

Map.addLayer(base_lst, vis_params, 'Baseline LST (Original)')
Map.addLayer(simulated_lst, vis_params, 'Simulated LST (Mitigated)')
Map.add_colorbar(vis_params, label="Temperature (°C)")

# স্ট্রীমলিটে ম্যাপ রেন্ডার
st_folium(Map, width=900, height=550)
