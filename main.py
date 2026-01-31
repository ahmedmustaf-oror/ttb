import streamlit as st
import requests
import random
import time
from fake_useragent import UserAgent
import concurrent.futures
from datetime import datetime
import json

# --- إعدادات الصفحة والتصميم ---
st.set_page_config(
    page_title="OROR | خدمات رشق احترافية",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# تحميل CSS مخصص
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
        min-height: 100vh;
    }
    
    @keyframes glow {
        0% { box-shadow: 0 0 5px #FFD700; }
        50% { box-shadow: 0 0 20px #FFD700, 0 0 30px #FF4500; }
        100% { box-shadow: 0 0 5px #FFD700; }
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    .user-avatar {
        display: block;
        margin: auto;
        border: 4px solid #FFD700;
        border-radius: 50%;
        animation: glow 2s infinite, float 3s ease-in-out infinite;
        margin-bottom: 20px;
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 15px;
        background: linear-gradient(45deg, #FFD700, #FF8C00, #FF4500);
        color: black;
        font-weight: bold;
        font-size: 18px;
        border: none;
        height: 4em;
        transition: all 0.3s ease;
        margin-top: 10px;
        position: relative;
        overflow: hidden;
    }
    
    .stButton>button:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 10px 25px rgba(255, 69, 0, 0.5);
    }
    
    .stButton>button::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: 0.5s;
    }
    
    .stButton>button:hover::after {
        left: 100%;
    }
    
    .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(0, 0, 0, 0.5);
        border: 2px solid #FFD700;
        border-radius: 10px;
        color: white;
    }
    
    .stTextInput>div>div>input {
        background-color: rgba(0, 0, 0, 0.5);
        color: #FFD700;
        border: 2px solid #FFD700;
        border-radius: 10px;
        text-align: center;
        font-size: 16px;
        padding: 12px;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #FF4500;
        box-shadow: 0 0 10px rgba(255, 69, 0, 0.5);
    }
    
    .success-box {
        background: linear-gradient(45deg, rgba(0,255,0,0.1), rgba(0,200,0,0.2));
        border-left: 5px solid #00FF00;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .error-box {
        background: linear-gradient(45deg, rgba(255,0,0,0.1), rgba(200,0,0,0.2));
        border-left: 5px solid #FF0000;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .info-box {
        background: linear-gradient(45deg, rgba(0,191,255,0.1), rgba(30,144,255,0.2));
        border-left: 5px solid #1E90FF;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .stat-box {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        text-align: center;
        border: 1px solid rgba(255, 215, 0, 0.3);
    }
    
    .header-text {
        background: linear-gradient(45deg, #FFD700, #FF8C00, #FF4500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 2.5em;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .subheader-text {
        color: #888;
        text-align: center;
        font-size: 1.2em;
        margin-bottom: 30px;
    }
    
    .footer {
        position: fixed;
        bottom: 0;
        width: 100%;
        text-align: center;
        padding: 10px;
        background: rgba(0, 0, 0, 0.7);
        color: #888;
        font-size: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# --- تهيئة UserAgent ---
ua = UserAgent()

# --- دالة لتوليد IP عشوائي واقعي ---
def generate_random_ip():
    # توليد IPs واقعية (ليست في النطاقات المحجوزة)
    first_octet = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 
                                11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
    return f"{first_octet}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"

# --- دالة للتحقق من صحة الرابط ---
def validate_url(url, platform):
    if not url:
        return False, "يرجى إدخال الرابط"
    
    url = url.strip().lower()
    
    platforms = {
        "إعجابات يوتيوب": ["youtube.com", "youtu.be"],
        "إعجابات تيك توك": ["tiktok.com"],
        "حفظ منشور إنستغرام": ["instagram.com"],
        "مشاهدات تيك توك": ["tiktok.com"]
    }
    
    if platform in platforms:
        required_domains = platforms[platform]
        if not any(domain in url for domain in required_domains):
            return False, f"الرابط يجب أن يكون من {platform}"
    
    # التحقق من تنسيق الرابط العام
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    return True, url

# --- دالة الرشق المحسنة ---
def send_request_enhanced(url, link, quantity=None, attempt=1, max_attempts=3):
    try:
        # توليد بيانات وهمية واقعية
        random_ip = generate_random_ip()
        
        headers = {
            "User-Agent": ua.random,
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": "https://leofame.com",
            "Referer": "https://leofame.com/",
            "X-Requested-With": "XMLHttpRequest",
            "X-Forwarded-For": random_ip,
            "Client-IP": random_ip,
            "CF-Connecting-IP": random_ip,
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache"
        }
        
        # بيانات POST مختلفة حسب الخدمة
        data = {
            "token": f"fake_token_{random.randint(100000, 999999)}",
            "timezone_offset": "Asia/Baghdad",
            "free_link": link,
            "timestamp": str(int(time.time())),
            "request_id": f"{random.randint(1000000000, 9999999999)}"
        }
        
        if quantity:
            data["quantity"] = str(quantity)
        
        # تأخير ذكي مع تقدم عشوائي
        delay = random.uniform(2.5, 6.5)
        time.sleep(delay)
        
        # إرسال الطلب مع timeout
        response = requests.post(
            url,
            headers=headers,
            data=data,
            timeout=15,
            allow_redirects=True,
            verify=False  # قد تحتاج إلى True في بيئة إنتاج
        )
        
        # تحليل الاستجابة
        if response.status_code == 200:
            try:
                json_response = response.json()
                if "error" in json_response or "wait" in str(json_response).lower():
                    if attempt < max_attempts:
                        # إعادة المحاولة بعد تأخير أطول
                        time.sleep(random.uniform(5, 10))
                        return send_request_enhanced(url, link, quantity, attempt + 1, max_attempts)
                    else:
                        return {
                            "success": False,
                            "message": "تم الوصول لحد المحاولات. جرب لاحقاً.",
                            "ip": random_ip
                        }
                else:
                    return {
                        "success": True,
                        "message": f"✅ تم الإرسال بنجاح",
                        "ip": random_ip,
                        "attempts": attempt
                    }
            except:
                # إذا لم يكن JSON، تحقق من النص
                if "success" in response.text.lower() or "تم" in response.text:
                    return {
                        "success": True,
                        "message": f"✅ تم تنفيذ الطلب بنجاح",
                        "ip": random_ip,
                        "attempts": attempt
                    }
                else:
                    return {
                        "success": False,
                        "message": "⚠️ استجابة غير متوقعة من الخادم",
                        "ip": random_ip
                    }
        elif response.status_code == 429:
            # الكثير من الطلبات
            wait_time = random.randint(30, 60)
            return {
                "success": False,
                "message": f"⏳ تم اكتشاف كثرة الطلبات. انتظر {wait_time} ثانية",
                "ip": random_ip,
                "wait_time": wait_time
            }
        else:
            return {
                "success": False,
                "message": f"❌ خطأ في الخادم: {response.status_code}",
                "ip": random_ip
            }
            
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": "⏱️ انتهت مدة الانتظار",
            "ip": random_ip
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": "🔌 خطأ في الاتصال بالخادم",
            "ip": random_ip
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"⚠️ خطأ غير متوقع: {str(e)[:50]}",
            "ip": random_ip
        }

# --- دالة للرشق المتعدد ---
def multi_send_request(url, link, quantity=None, count=1):
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for i in range(count):
            future = executor.submit(
                send_request_enhanced,
                url, link, quantity
            )
            futures.append(future)
            # تأخير بين الطلبات
            time.sleep(random.uniform(1, 3))
        
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result(timeout=30)
                results.append(result)
            except:
                results.append({
                    "success": False,
                    "message": "انتهت مهلة التنفيذ",
                    "ip": "غير معروف"
                })
    
    return results

# --- واجهة المستخدم ---
st.markdown(f'''
    <img src="https://c.top4top.io/p_3677ytx7u0.jpg" 
         class="user-avatar" width="180">
    <div class="header-text">OROR | خدمات رشق احترافية</div>
    <div class="subheader-text">أدوات متقدمة لتعزيز المحتوى على المنصات الاجتماعية</div>
''', unsafe_allow_html=True)

st.write("---")

# --- إحصائيات العرض ---
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="stat-box">🎯 دقة عالية</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="stat-box">⚡ سرعة فائقة</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="stat-box">🔒 أمان تام</div>', unsafe_allow_html=True)

st.write("---")

# --- اختيار الخدمة ---
option = st.selectbox(
    "📱 اختر الخدمة المطلوبة:",
    ["إعجابات يوتيوب", "إعجابات تيك توك", "حفظ منشور إنستغرام", "مشاهدات تيك توك"],
    help="اختر نوع الخدمة التي تريدها"
)

# --- إدخال الرابط ---
video_url = st.text_input(
    "🔗 ضع الرابط هنا:",
    placeholder="https://www.youtube.com/watch?v=... أو https://www.tiktok.com/@...",
    help="انسخ الرابط مباشرة من المنصة"
)

# --- اختيار عدد الطلبات ---
request_count = st.slider(
    "🔄 عدد محاولات الإرسال:",
    min_value=1,
    max_value=10,
    value=3,
    help="عدد مرات إرسال الطلب (زيادة العدد تزيد فرص النجاح)"
)

# --- زر البدء ---
if st.button("🚀 بدء الرشق", key="start_button"):
    if video_url:
        with st.spinner('🔍 جاري التحقق من الرابط...'):
            is_valid, validated_url = validate_url(video_url, option)
            
            if not is_valid:
                st.markdown(f'<div class="error-box">{validated_url}</div>', unsafe_allow_html=True)
            else:
                # عرض معلومات العملية
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # تحديد رابط API حسب الخدمة
                api_urls = {
                    "إعجابات يوتيوب": "https://leofame.com/free-youtube-likes?api=1",
                    "إعجابات تيك توك": "https://leofame.com/free-tiktok-likes?api=1",
                    "حفظ منشور إنستغرام": "https://leofame.com/free-instagram-saves?api=1",
                    "مشاهدات تيك توك": "https://leofame.com/ar/free-tiktok-views?api=1"
                }
                
                quantities = {
                    "إعجابات يوتيوب": None,
                    "إعجابات تيك توك": None,
                    "حفظ منشور إنستغرام": "30",
                    "مشاهدات تيك توك": "200"
                }
                
                api_url = api_urls.get(option)
                quantity = quantities.get(option)
                
                if not api_url:
                    st.markdown('<div class="error-box">❌ رابط API غير متوفر لهذه الخدمة</div>', unsafe_allow_html=True)
                else:
                    # تنفيذ الرشق المتعدد
                    status_text.markdown('<div class="info-box">⚡ جاري تنفيذ الطلبات...</div>', unsafe_allow_html=True)
                    
                    results = multi_send_request(
                        api_url,
                        validated_url,
                        quantity,
                        request_count
                    )
                    
                    # عرض النتائج
                    success_count = sum(1 for r in results if r.get("success"))
                    failed_count = len(results) - success_count
                    
                    # تحديث شريط التقدم
                    progress_bar.progress(100)
                    
                    # عرض النتائج التفصيلية
                    st.write("---")
                    st.markdown(f"### 📊 نتائج التنفيذ")
                    
                    for i, result in enumerate(results, 1):
                        if result.get("success"):
                            st.markdown(f'''
                                <div class="success-box">
                                    <strong>✅ الطلب #{i}:</strong> {result.get("message")}<br>
                                    <small>🌐 IP: {result.get("ip", "غير معروف")}</small>
                                </div>
                            ''', unsafe_allow_html=True)
                        else:
                            st.markdown(f'''
                                <div class="error-box">
                                    <strong>❌ الطلب #{i}:</strong> {result.get("message")}<br>
                                    <small>🌐 IP: {result.get("ip", "غير معروف")}</small>
                                </div>
                            ''', unsafe_allow_html=True)
                    
                    # عرض الإحصائيات النهائية
                    st.write("---")
                    col_success, col_failed = st.columns(2)
                    with col_success:
                        st.metric("✅ الطلبات الناجحة", success_count)
                    with col_failed:
                        st.metric("❌ الطلبات الفاشلة", failed_count)
                    
                    if success_count > 0:
                        st.balloons()
                        st.markdown('<div class="success-box">🎉 تم تنفيذ العمليات بنجاح! قد يستغرق ظهور النتائج بعض الدقائق.</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="error-box">⚠️ لم تنجح أي عملية. جرب لاحقاً أو تأكد من الرابط.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="error-box">⚠️ يرجى إدخال الرابط أولاً!</div>', unsafe_allow_html=True)

# --- نصائح وإرشادات ---
st.write("---")
with st.expander("💡 نصائح هامة للحصول على أفضل النتائج"):
    st.markdown("""
    1. **تأكد من صحة الرابط** - نسخ الرابط مباشرة من المنصة
    2. **استخدم روابط عامة** - وليس روابط خاصة
    3. **لا تبالغ في العدد** - 3-5 محاولات كافية عادة
    4. **انتظر بين المحاولات** - النظام يعمل تلقائياً
    5. **تحقق من النتائج** - بعد 5-10 دقائق من التنفيذ
    6. **للمشاكل الفنية** - حاول تغيير الرابط أو الانتظار ساعة
    """)

# --- Footer ---
st.markdown("---")
st.markdown(
    '<div class="footer">'
    'تم التطوير بواسطة <strong style="color:#FFD700">OROR</strong> | '
    f'🕒 آخر تحديث: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    '</div>',
    unsafe_allow_html=True
)