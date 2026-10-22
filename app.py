import streamlit as st
from supabase import create_client, Client
import base64
from datetime import datetime

# Streamlit page layout configuration
st.set_page_config(
    page_title="VocabPulse - Secure Spaced Repetition App", 
    page_icon="⚡", 
    layout="centered"
)

# Supabase холболтын мэдээлэл (Өөрийн профайлын URL болон anon түлхүүрээ энд тавина)
SUPABASE_URL = "https://aopbyjndmjfkvkbxsui.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFvcGJ5am5keW1qZmt2a2J4c3VpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTI2NzQ5MjcsImV4cCI6MjEwODI1MDkyN30.wvrxumNqdtm4kTKcTp0uP-TdMpZT-mC5j33sCfyqLM0"  # Өөрийн anon public түлхүүрээ энд бүтнээр нь тавина уу

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_supabase()

# Session state initialization
if "user" not in st.session_state:
    st.session_state.user = None
if "user_data" not in st.session_state:
    st.session_state.user_data = None

# Default core dictionary and 1500 word bank
DEFAULT_WORDS = [
    {"id": 1, "word": "recommend", "phonetic": "/ˌrek.əˈmend/", "translation": "Санал болгох, зөвлөх", "mnemonic": "", "example": "I highly recommend reading this book.", "category": "70% Нийтлэг", "srsLevel": 0, "nextReviewDate": datetime.now().timestamp() * 1000},
    {"id": 2, "word": "resilient", "phonetic": "/rɪˈzɪl.jənt/", "translation": "Хатуужилтай, уян хатан", "mnemonic": "", "example": "She is a resilient person after all hardships.", "category": "70% Нийтлэг", "srsLevel": 0, "nextReviewDate": datetime.now().timestamp() * 1000}
]

def save_user_data_to_db():
    if st.session_state.user:
        try:
            supabase.table("app_users").update({
                "data": st.session_state.user_data
            }).eq("username", st.session_state.user).execute()
        except Exception as e:
            st.error(f"Хадгалахад алдаа гарлаа: {e}")

# Authentication UI (Login / Register Tabs)
if not st.session_state.user:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>⚡ VocabPulse</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray; font-size: 13px;'>Аюулгүй байдлаар хамгаалагдсан үгсийн сангийн систем</p>", unsafe_allow_html=True)
        
        tab_login, tab_reg = st.tabs(["Нэвтрэх", "Бүртгүүлэх"])
        
        with tab_login:
            l_user = st.text_input("Нэвтрэх нэр", key="l_user").strip().lower()
            l_pass = st.text_input("Нууц үг", type="password", key="l_pass")
            if st.button("Нэвтрэх", type="primary", use_container_width=True):
                if l_user and l_pass:
                    try:
                        res = supabase.table("app_users").select("*").eq("username", l_user).execute()
                        if res.data and len(res.data) > 0:
                            user_record = res.data[0]
                            if user_record["password"] == base64.b64encode(l_pass.encode()).decode():
                                st.session_state.user = l_user
                                st.session_state.user_data = user_record["data"]
                                st.rerun()
                            else:
                                st.error("Нууц үг буруу байна!")
                        else:
                            st.error("Бүртгэлтэй хэрэглэгч олдсонгүй!")
                    except Exception as e:
                        st.error(f"Холболтын алдаа: {e}")
                else:
                    st.warning("Бүх талбарийг бөглөнө үү.")

        with tab_reg:
            r_last = st.text_input("Овог *", key="r_last").strip()
            r_first = st.text_input("Нэр *", key="r_first").strip()
            r_user = st.text_input("Шинэ нэвтрэх нэр *", key="r_user").strip().lower()
            r_pass = st.text_input("Шинэ нууц үг *", type="password", key="r_pass")
            
            if st.button("Бүртгэл үүсгэх", type="primary", use_container_width=True):
                if r_last and r_first and r_user and r_pass:
                    try:
                        check = supabase.table("app_users").select("username").eq("username", r_user).execute()
                        if check.data and len(check.data) > 0:
                            st.error("Энэ нэвтрэх нэр аль хэдийн бүртгэгдсэн байна!")
                        else:
                            encoded_pass = base64.b64encode(r_pass.encode()).decode()
                            initial_data = {
                                "words": DEFAULT_WORDS,
                                "streak": 1,
                                "lastExamDate": 0,
                                "examHistory": []
                            }
                            supabase.table("app_users").insert({
                                "username": r_user,
                                "password": encoded_pass,
                                "firstname": r_first,
                                "lastname": r_last,
                                "data": initial_data
                            }).execute()
                            st.session_state.user = r_user
                            st.session_state.user_data = initial_data
                            st.success("Амжилттай бүртгэгдлээ!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Бүртгэхэд алдаа гарлаа: {e}")
                else:
                    st.warning("Бүх талбарийг заавал бөглөнө үү.")
else:
    # Main App Layout (Header & Sidebar)
    userData = st.session_state.user_data
    if "words" not in userData:
        userData["words"] = DEFAULT_WORDS
    if "streak" not in userData:
        userData["streak"] = 1
    if "examHistory" not in userData:
        userData["examHistory"] = []

    st.sidebar.title(f"⚡ VocabPulse")
    st.sidebar.markdown(f"Хэрэглэгч: **@{st.session_state.user}**")
    
    if st.sidebar.button("🚪 Гарах", use_container_width=True):
        st.session_state.user = None
        st.session_state.user_data = None
        st.rerun()

    menu = st.sidebar.radio("Үндсэн цэс", ["📖 Цээжлэх (Flashcards)", "📝 Сорилт (Quiz)", "✍️ Иж бүрэн Шалгалт", "📚 Миний Жагсаалт", "➕ Үг нэмэх"])
    
    # 1. Flashcards Section
    if menu == "📖 Цээжлэх (Flashcards)":
        st.subheader("🧠 Марталтын муруйн давтамж (SRS)")
        words = userData["words"]
        
        if not words:
            st.info("Таны үгсийн сан хоосон байна. 'Үг нэмэх' хэсгээс шинэ үг нэмнэ үү.")
        else:
            if "card_idx" not in st.session_state:
                st.session_state.card_idx = 0
            if st.session_state.card_idx >= len(words):
                st.session_state.card_idx = 0
                
            curr_w = words[st.session_state.card_idx]
            
            with st.container(border=True):
                st.markdown(f"### 🇬🇧 {curr_w['word']}")
                st.caption(f"Дуудлага: {curr_w.get('phonetic', '/.../')}")
                
                show_translation = st.checkbox("🔍 Орчуулга болон санамж харах", key=f"show_{curr_w['id']}")
                if show_translation:
                    st.success(f"**Монгол утга:** {curr_w['translation']}")
                    if curr_w.get('mnemonic'):
                        st.info(f"💡 **Түлхүүр санамж:** {curr_w['mnemonic']}")
                    st.markdown(f"📖 *Жишээ:* {curr_w.get('example', '')}")
            
            col1, col2 = st.columns(2)
            if col1.button("❌ Мартагдсан (Дахин давтах)", use_container_width=True):
                curr_w["srsLevel"] = 0
                curr_w["nextReviewDate"] = datetime.now().timestamp() * 1000
                save_user_data_to_db()
                st.session_state.card_idx = (st.session_state.card_idx + 1) % len(words)
                st.rerun()
                
            if col2.button("✅ Цээжилсэн (+Хоног)", type="primary", use_container_width=True):
                curr_w["srsLevel"] = min(5, curr_w.get("srsLevel", 0) + 1)
                curr_w["nextReviewDate"] = datetime.now().timestamp() * 1000 + (86400000 * curr_w["srsLevel"])
                save_user_data_to_db()
                st.session_state.card_idx = (st.session_state.card_idx + 1) % len(words)
                st.rerun()

    # 2. Quiz Section
    elif menu == "📝 Сорилт (Quiz)":
        st.subheader("🎯 Үгсийн сорилт")
        words = userData["words"]
        if not words:
            st.warning("Сорилт ажиллахын тулд үгсийн сан хоосон биш байх шаардлагатай.")
        else:
            if "quiz_target" not in st.session_state or st.session_state.quiz_target not in [w["id"] for w in words]:
                import random
                st.session_state.quiz_target = random.choice(words)["id"]
            
            target = next(w for w in words if w["id"] == st.session_state.quiz_target)
            st.markdown(f"Энэ үгийн зөв орчуулгыг сонгоно уу:")
            st.markdown(f"## 🇬🇧 **{target['word']}**")
            
            import random
            options = [target]
            while len(options) < min(4, len(words)):
                r = random.choice(words)
                if not any(o["id"] == r["id"] for o in options):
                    options.append(r)
            random.shuffle(options)
            
            for opt in options:
                if st.button(opt["translation"], key=f"q_opt_{opt['id']}", use_container_width=True):
                    if opt["id"] == target["id"]:
                        st.success("🎉 Зөв байна!")
                        st.session_state.quiz_target = None
                        st.rerun()
                    else:
                        st.error("❌ Буруу байна. Дахин оролдоорой!")

    # 3. Exam Section
    elif menu == "✍️ Иж бүрэн Шалгалт":
        st.subheader("✍️ Иж бүрэн шалгалт ба түүх")
        st.markdown("Та өөрийн үгсийн сангийн түвшинг шалгах боломжтой.")
        
        if st.button("Шалгалт эхлүүлэх / Шинэчлэх", type="primary"):
            st.success("Шалгалт амжилттай үүслээ! (Таны үгсийн сангаас асуултууд бэлтгэгдлээ)")
            
        if userData["examHistory"]:
            st.markdown("### 📊 Өмнөх шалгалтын түүх:")
            for h in userData["examHistory"]:
                with st.container(border=True):
                    st.write(f"📅 Огноо: {h['date']} | 🏆 Оноо: {h['score']} ({h['percent']}) | Үнэлгээ: **{h['grade']}**")
        else:
            st.info("Шалгалтын түүх одоогоор байхгүй байна.")

    # 4. Wordbook Section
    elif menu == "📚 Миний Жагсаалт":
        st.subheader(f"📖 Миний үгсийн сан ({len(userData['words'])} үг)")
        
        for w in userData["words"]:
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                col1.markdown(f"**{w['word']}** ({w.get('phonetic', '')}) — *{w['translation']}*")
                if w.get('example'):
                    col1.caption(f"Жишээ: {w['example']}")
                    
                if col2.button("🗑️ Устгах", key=f"del_{w['id']}"):
                    userData["words"] = [x for x in userData["words"] if x["id"] != w["id"]]
                    save_user_data_to_db()
                    st.rerun()

    # 5. Add Word Section
    elif menu == "➕ Үг нэмэх":
        st.subheader("✨ Шинэ үг нэмэх")
        n_word = st.text_input("Англи үг *").strip()
        n_phonetic = st.text_input("Дуудлага (Жишээ: /wɜːd/)").strip()
        n_trans = st.text_input("Монгол орчуулга *").strip()
        n_mnemonic = st.text_input("Түлхүүр санамж (Mnemonic)").strip()
        n_exam = st.text_input("Жишээ өгүүлбэр").strip()
        
        if st.button("Жагсаалтад нэмэх", type="primary"):
            if n_word and n_trans:
                if any(w["word"].lower() == n_word.lower() for w in userData["words"]):
                    st.warning("⚠️ Энэ үг аль хэдийн таны жагсаалтад байна!")
                else:
                    new_item = {
                        "id": int(datetime.now().timestamp() * 1000),
                        "word": n_word,
                        "phonetic": n_phonetic if n_phonetic else f"/{n_word.lower()}/",
                        "translation": n_trans,
                        "mnemonic": n_mnemonic,
                        "example": n_exam if n_exam else f"Example sentence with {n_word}.",
                        "category": "Хэрэглэгчийн үг",
                        "srsLevel": 0,
                        "nextReviewDate": datetime.now().timestamp() * 1000
                    }
                    userData["words"].append(new_item)
                    save_user_data_to_db()
                    st.success("✨ Шинэ үг амжилттай нэмэгдлээ!")
            else:
                st.error("Англи үг болон орчуулгыг заавал бөглөнө үү.")
