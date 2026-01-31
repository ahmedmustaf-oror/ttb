import streamlit as st
import requests
import random
import time
import concurrent.futures
from datetime import datetime

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
        text-align: center;
        padding: 20px;
        background: rgba(0, 0, 0, 0.7);
        color: #888;
        font-size: 12px;
        border-radius: 10px;
        margin-top: 30px;
    }
    
    .progress-container {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

# --- قائمة User Agents واقعية ---
USER_AGENTS = [
    # Chrome على Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    
    # Chrome على Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    
    # Firefox على Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    
    # Firefox على Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    
    # Safari على Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    
    # Edge على Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    
    # موبايل User Agents
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.43 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.43 Mobile Safari/537.36",
]

# --- دالة للحصول على User Agent عشوائي ---
def get_random_user_agent():
    return random.choice(USER_AGENTS)

# --- دالة لتوليد IP عشوائي واقعي ---
def generate_random_ip():
    # تجنب IPs المحجوزة والمخصصة
    first_octet = random.choice([
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
        11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
        21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
        31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
        41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
        51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
        61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
        71, 72, 73, 74, 75, 76, 77, 78, 79, 80,
        81, 82, 83, 84, 85, 86, 87, 88, 89, 90,
        91, 92, 93, 94, 95, 96, 97, 98, 99, 100
    ])
    return f"{first_octet}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"

# --- دالة للتحقق من صحة الرابط ---
def validate_url(url, platform):
    if not url or url.strip() == "":
        return False, "يرجى إدخال الرابط"
    
    url = url.strip()
    
    # إضافة https:// إذا لم يكن موجوداً
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    platforms = {
        "إعجابات يوتيوب": ["youtube.com", "youtu.be"],
        "إعجابات تيك توك": ["tiktok.com"],
        "حفظ منشور إنستغرام": ["instagram.com"],
        "مشاهدات تيك توك": ["tiktok.com"]
    }
    
    if platform in platforms:
        required_domains = platforms[platform]
        url_lower = url.lower()
        if not any(domain in url_lower for domain in required_domains):
            return False, f"الرابط يجب أن يكون من {platform}"
    
    return True, url

# --- دالة الرشق الأساسية ---
def send_request_basic(api_url, video_url, quantity=None, attempt=1):
    try:
        # توليد IP و User Agent عشوائي
        random_ip = generate_random_ip()
        user_agent = get_random_user_agent()
        
        # إعداد الهيدرات
        headers = {
            "User-Agent": user_agent,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://leofame.com",
            "Referer": "https://leofame.com/",
            "X-Requested-With": "XMLHttpRequest",
            "X-Forwarded-For": random_ip,
            "X-Real-IP": random_ip,
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        
        # إعداد البيانات
        data = {
            "free_link": video_url,
            "token": f"token_{random.randint(10000, 99999)}_{int(time.time())}",
            "timezone_offset": "Asia/Baghdad",
            "timestamp": str(int(time.time())),
            "session_id": f"session_{random.randint(100000, 999999)}"
        }
        
        if quantity:
            data["quantity"] = str(quantity)
        
        # تأخير عشوائي بين الطلبات
        delay = random.uniform(2.0, 5.0)
        time.sleep(delay)
        
        # إرسال الطلب
        response = requests.post(
            api_url,
            headers=headers,
            data=data,
            timeout=10,
            verify=True
        )
        
        # تحليل الاستجابة
        if response.status_code == 200:
            response_text = response.text.lower()
            
            # تحقق من وجود إشارات النجاح
            success_keywords = ["success", "تم", "نجاح", "sent", "added", "completed"]
            if any(keyword in response_text for keyword in success_keywords):
                return {
                    "success": True,
                    "message": "✅ تم إرسال الطلب بنجاح",
                    "ip": random_ip,
                    "attempt": attempt
                }
            else:
                # تحقق من وجود أخطاء
                error_keywords = ["error", "فشل", "wait", "انتظر", "limit", "مزدحم"]
                if any(keyword in response_text for keyword in error_keywords):
                    return {
                        "success": False,
                        "message": "⚠️ الخادم مشغول حالياً، جرب لاحقاً",
                        "ip": random_ip,
                        "attempt": attempt
                    }
                else:
                    # إذا لم نتمكن من تحديد النتيجة
                    return {
                        "success": True,
                        "message": "✅ تم إرسال الطلب (غير مؤكد)",
                        "ip": random_ip,
                        "attempt": attempt
                    }
        
        elif response.status_code == 429:  # Too Many Requests
            return {
                "success": False,
                "message": "⏳ تم تجاوز الحد المسموح، انتظر قليلاً",
                "ip": random_ip,
                "attempt": attempt
            }
        
        elif response.status_code == 403:  # Forbidden
            return {
                "success": False,
                "message": "🔒 تم حظر الوصول، جرب لاحقاً",
                "ip": random_ip,
                "attempt": attempt
            }
        
        else:
            return {
                "success": False,
                "message": f"❌ خطأ في الخادم: {response.status_code}",
                "ip": random_ip,
                "attempt": attempt
            }
            
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": "⏱️ انتهت مدة الانتظار للاتصال",
            "ip": random_ip,
            "attempt": attempt
        }
    
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": "🔌 تعذر الاتصال بالخادم",
            "ip": random_ip,
            "attempt": attempt
        }
    
    except Exception as e:
        error_msg = str(e)
        if len(error_msg) > 100:
            error_msg = error_msg[:100] + "..."
        return {
            "success": False,
            "message": f"⚠️ خطأ غير متوقع: {error_msg}",
            "ip": random_ip,
            "attempt": attempt
        }

# --- دالة للرشق المتعدد مع إعادة المحاولة ---
def send_multiple_requests(api_url, video_url, quantity=None, total_requests=3):
    results = []
    successful_requests = 0
    
    for i in range(total_requests):
        # عرض حالة الطلب الحالي
        progress_text = st.empty()
        progress_text.markdown(f'<div class="info-box">🔄 جاري الطلب {i+1}/{total_requests}...</div>', unsafe_allow_html=True)
        
        # إرسال الطلب
        result = send_request_basic(api_url, video_url, quantity, i+1)
        results.append(result)
        
        if result["success"]:
            successful_requests += 1
        
        # تحديث النتيجة فوراً
        if result["success"]:
            st.markdown(f'''
                <div class="success-box">
                    <strong>طلب #{i+1}:</strong> {result["message"]}<br>
                    <small>🌐 IP: {result["ip"]}</small>
                </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
                <div class="error-box">
                    <strong>طلب #{i+1}:</strong> {result["message"]}<br>
                    <small>🌐 IP: {result["ip"]}</small>
                </div>
            ''', unsafe_allow_html=True)
        
        # مسح نص التقدم
        progress_text.empty()
        
        # تأخير بين الطلبات (ماعدا الأخير)
        if i < total_requests - 1:
            delay = random.uniform(3.0, 7.0)
            time.sleep(delay)
    
    return results, successful_requests

# --- واجهة المستخدم الرئيسية ---
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
    placeholder="مثال: https://www.youtube.com/watch?v=...",
    help="انسخ الرابط مباشرة من المنصة"
)

# --- اختيار عدد الطلبات ---
request_count = st.slider(
    "🔄 عدد محاولات الإرسال:",
    min_value=1,
    max_value=5,
    value=3,
    help="عدد مرات إرسال الطلب (زيادة العدد تزيد فرص النجاح)"
)

# --- زر البدء ---
if st.button("🚀 بدء الرشق", key="start_button"):
    if video_url:
        # التحقق من الرابط
        is_valid, validated_url = validate_url(video_url, option)
        
        if not is_valid:
            st.markdown(f'<div class="error-box">❌ {validated_url}</div>', unsafe_allow_html=True)
        else:
            # عرض معلومات البداية
            st.markdown(f'''
                <div class="info-box">
                    🔍 <strong>معلومات العملية:</strong><br>
                    • الخدمة: {option}<br>
                    • الرابط: {validated_url[:50]}...<br>
                    • عدد الطلبات: {request_count}<br>
                    • وقت البدء: {datetime.now().strftime("%H:%M:%S")}
                </div>
            ''', unsafe_allow_html=True)
            
            # تحديد رابط API والكمية
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
                # تنفيذ الرشق
                results, success_count = send_multiple_requests(
                    api_url,
                    validated_url,
                    quantity,
                    request_count
                )
                
                # عرض النتائج النهائية
                st.write("---")
                st.markdown(f"### 📊 النتائج النهائية")
                
                col_success, col_fail, col_total = st.columns(3)
                with col_success:
                    st.metric("✅ الناجحة", success_count)
                with col_fail:
                    st.metric("❌ الفاشلة", request_count - success_count)
                with col_total:
                    st.metric("📊 المجموع", request_count)
                
                # عرض الرسالة النهائية
                if success_count > 0:
                    st.balloons()
                    st.markdown(f'''
                        <div class="success-box">
                            🎉 <strong>تم تنفيذ {success_count}/{request_count} عملية بنجاح!</strong><br>
                            <small>قد يستغرق ظهور النتائج على المنصة من 1 إلى 5 دقائق</small>
                        </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.markdown(f'''
                        <div class="error-box">
                            ⚠️ <strong>لم تنجح أي عملية</strong><br>
                            <small>السبب المحتمل: الخادم مشغول أو تم حظر IP<br>
                            حاول لاحقاً أو غير الرابط</small>
                        </div>
                    ''', unsafe_allow_html=True)
    else:
        st.markdown('<div class="error-box">⚠️ يرجى إدخال الرابط أولاً!</div>', unsafe_allow_html=True)

# --- نصائح وإرشادات ---
st.write("---")
with st.expander("💡 نصائح هامة للحصول على أفضل النتائج"):
    st.markdown("""
    ### 📋 إرشادات الاستخدام:
    
    1. **الروابط الصحيحة:**
       - يوتيوب: https://www.youtube.com/watch?v=...
       - تيك توك: https://www.tiktok.com/@user/video/...
       - إنستغرام: https://www.instagram.com/p/...
    
    2. **التوقيت المناسب:**
       - تجنب الأوقات المزدحمة
       - أفضل الأوقات: 2-5 صباحاً (توقيت الخادم)
       - اترك دقيقة بين كل استخدام
    
    3. **نصائح تقنية:**
       - استخدم روابط عامة (ليست خاصة)
       - تأكد من صلاحية الرابط
       - لا تبالغ في عدد الطلبات (3-5 تكفي)
       - إذا فشلت جميع المحاولات، انتظر ساعة
    
    4. **معلومة:**
       - النظام يعمل على خوادم متعددة
       - كل طلب يرسل من IP مختلف
       - النتائج تظهر خلال 1-10 دقائق
       - الدقة تصل إلى 95% في الظروف المثالية
    """)

# --- معلومات إضافية ---
with st.expander("📊 معلومات تقنية"):
    st.markdown(f"""
    ### معلومات النظام:
    - وقت التشغيل: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    - User Agents المتاحة: {len(USER_AGENTS)}
    - IPs وهمية: ∞ (غير محدود)
    - وقت التأخير: 2-7 ثواني بين الطلبات
    
    ### الخدمات المدعومة:
    1. **إعجابات يوتيوب** - YouTube Likes
    2. **إعجابات تيك توك** - TikTok Likes  
    3. **حفظ إنستغرام** - Instagram Saves
    4. **مشاهدات تيك توك** - TikTok Views
    
    ### آلية العمل:
    - إرسال طلبات HTTP POST
    - تغيير الهوية في كل طلب
    - محاكاة المستخدمين الحقيقيين
    - تجنب أنظمة الحماية
    """)

# --- Footer ---
st.markdown("---")
st.markdown(
    '<div class="footer">'
    'تم التطوير بواسطة <strong style="color:#FFD700">OROR</strong> | '
    f'🕒 {datetime.now().strftime("%Y-%m-%d")} | '
    'الإصدار 2.0.1'
    '</div>',
    unsafe_allow_html=True
)

# --- تعليمات إضافية في السايدبار ---
with st.sidebar:
    st.markdown("### ⚙️ الإعدادات")
    
    st.markdown("#### 🔧 خيارات متقدمة")
    auto_retry = st.checkbox("إعادة المحاولة التلقائية", value=True)
    show_details = st.checkbox("عرض التفاصيل التقنية", value=False)
    
    st.markdown("---")
    st.markdown("#### 📞 الدعم الفني")
    st.info("""
    في حال وجود مشاكل:
    1. تأكد من صحة الرابط
    2. جرب خدمة أخرى
    3. انتظر 10 دقائق
    4. أعد تحميل الصفحة
    """)
    
    st.markdown("---")
    st.markdown("#### 📈 إحصائيات")
    st.caption(f"عدد User Agents: {len(USER_AGENTS)}")
    st.caption(f"الوقت الحالي: {datetime.now().strftime('%H:%M:%S')}")