import streamlit as st
from supabase import create_client, Client
import base64
from datetime import datetime

st.set_page_config(page_title="VocabPulse Cloud", page_icon="⚡", layout="centered")

# Энд өөрийн Supabase мэдээллээ оруулна уу
SUPABASE_URL = "https://aopbyjndymjfkvkbxsui.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFvcGJ5am5keW1qZmt2a2J4c3VpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTI2NzQ5MjcsImV4cCI6MjEwODI1MDkyN30.wvrxumNqdtm4kTKcTp0uP-TdMpZT-mC5j33sCfyqLM0"

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_supabase()

if "user" not in st.session_state:
    st.session_state.user = None
if "user_data" not in st.session_state:
    st.session_state.user_data = None

def get_default_words():
    return {
        "words": [
            {"id": 1, "word": "recommend", "phonetic": "/ˌrek.əˈmend/", "translation": "Санал болгох, зөвлөх", "example": "I highly recommend reading this book."},
            {"id": 2, "word": "resilient", "phonetic": "/rɪˈzɪl.jənt/", "translation": "Хатуужилтай, уян хатан", "example": "She is a resilient person."}
        ],
        "streak": 1,
        "examHistory": []
    }

def save_user_data():
    if st.session_state.user:
        try:
            supabase.table("app_users").update({
                "data": st.session_state.user_data
            }).eq("username", st.session_state.user).execute()
        except Exception as e:
            st.error(f"Хадгалахад алдаа гарлаа: {e}")

if not st.session_state.user:
    st.title("⚡ VocabPulse Cloud")
    st.markdown("Хүссэн төхөөрөмжөөсөө нэвтэрч үгсийн сангаа удирдах систем")
    
    tab1, tab2 = st.tabs(["Нэвтрэх", "Бүртгүүлэх"])
    
    with tab1:
        l_user = st.text_input("Нэвтрэх нэр", key="l_user").strip().lower()
        l_pass = st.text_input("Нууц үг", type="password", key="l_pass")
        if st.button("Нэвтрэх", type="primary"):
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
                    st.error(f"Нэвтрэхэд алдаа гарлаа: {e}")
            else:
                st.warning("Бүх талбарыг бөглөнө үү.")

    with tab2:
        r_user = st.text_input("Шинэ нэвтрэх нэр", key="r_user").strip().lower()
        r_pass = st.text_input("Шинэ нууц үг", type="password", key="r_pass")
        r_first = st.text_input("Нэр").strip()
        r_last = st.text_input("Овог").strip()
        
        if st.button("Бүртгэл үүсгэх", type="primary"):
            if r_user and r_pass and r_first and r_last:
                try:
                    check = supabase.table("app_users").select("username").eq("username", r_user).execute()
                    if check.data and len(check.data) > 0:
                        st.error("Энэ нэвтрэх нэр аль хэдийн бүртгэгдсэн байна!")
                    else:
                        encoded_pass = base64.b64encode(r_pass.encode()).decode()
                        initial_data = get_default_words()
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
                st.warning("Бүх талбарыг бөглөнө үү.")
                
else:
    st.sidebar.title(f"👋 Сайн байна уу, @{st.session_state.user}!")
    if st.sidebar.button("Гарах"):
        st.session_state.user = None
        st.session_state.user_data = None
        st.rerun()
        
    menu = st.sidebar.radio("Цэс", ["📖 Цээжлэх (Flashcards)", "📝 Миний жагсаалт", "➕ Үг нэмэх"])
    words = st.session_state.user_data.get("words", [])
    
    if menu == "📖 Цээжлэх (Flashcards)":
        st.subheader("Марталтын муруйн давтамж")
        if not words:
            st.info("Таны үгсийн сан хоосон байна. Шинэ үг нэмнэ үү.")
        else:
            if "card_idx" not in st.session_state:
                st.session_state.card_idx = 0
            if st.session_state.card_idx >= len(words):
                st.session_state.card_idx = 0
                
            curr_w = words[st.session_state.card_idx]
            with st.container(border=True):
                st.markdown(f"### 🇬🇧 {curr_w['word']}")
                st.caption(curr_w.get('phonetic', ''))
                show_ans = st.checkbox("Орчуулга харах", key=f"chk_{curr_w['id']}")
                if show_ans:
                    st.success(f"**Монгол утга:** {curr_w['translation']}")
                    st.info(f"**Жишээ:** {curr_w.get('example', '')}")
            
            col1, col2 = st.columns(2)
            if col1.button("❌ Мартагдсан", use_container_width=True):
                st.session_state.card_idx = (st.session_state.card_idx + 1) % len(words)
                st.rerun()
            if col2.button("✅ Цээжилсэн", type="primary", use_container_width=True):
                st.session_state.card_idx = (st.session_state.card_idx + 1) % len(words)
                st.rerun()

    elif menu == "📝 Миний жагсаалт":
        st.subheader(f"Миний үгсийн сан ({len(words)})")
        for w in words:
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"**{w['word']}** — *{w['translation']}*")
                if c2.button("Устгах", key=f"del_{w['id']}"):
                    st.session_state.user_data["words"] = [x for x in words if x["id"] != w["id"]]
                    save_user_data()
                    st.rerun()

    elif menu == "➕ Үг нэмэх":
        st.subheader("Шинэ үг нэмэх")
        n_word = st.text_input("Англи үг").strip()
        n_trans = st.text_input("Монгол орчуулга").strip()
        n_exam = st.text_input("Жишээ өгүүлбэр").strip()
        
        if st.button("Жагсаалтад нэмэх", type="primary"):
            if n_word and n_trans:
                if any(w["word"].lower() == n_word.lower() for w in words):
                    st.warning("⚠️ Энэ үг аль хэдийн жагсаалтад байна!")
                else:
                    new_item = {
                        "id": int(datetime.now().timestamp() * 1000),
                        "word": n_word,
                        "translation": n_trans,
                        "example": n_exam if n_exam else f"Example with {n_word}."
                    }
                    st.session_state.user_data["words"].append(new_item)
                    save_user_data()
                    st.success("✨ Шинэ үг амжилттай нэмэгдлээ!")
            else:
                st.error("Үг болон орчуулгыг заавал бичнэ үү.")
