import streamlit as st
import os
import json
import hashlib
import random

DATA_DIR = "user_data"
os.makedirs(DATA_DIR, exist_ok=True)

def hash_pwd(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def load_user(username):
    path = os.path.join(DATA_DIR, f"{username}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_user(username, data):
    path = os.path.join(DATA_DIR, f"{username}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def register(username, pwd):
    if load_user(username):
        return False
    data = {"password": hash_pwd(pwd), "unknown": [], "known": []}
    save_user(username, data)
    return True

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

st.set_page_config(page_title="Vocabulary Quiz", page_icon="📚", layout="centered")

if not st.session_state.logged_in:
    st.title("אפליקציית אוצר מילים")
    mode = st.radio("בחר פעולה", ["התחברות", "הרשמה"])
    u = st.text_input("שם משתמש")
    p = st.text_input("סיסמה", type="password")
    if st.button(mode):
        if mode == "הרשמה":
            if register(u, p):
                st.success("נרשמת בהצלחה, התחבר/י כעת")
            else:
                st.error("שם משתמש כבר קיים")
        else:
            user = load_user(u)
            if user and user["password"] == hash_pwd(p):
                st.session_state.logged_in = True
                st.session_state.username = u
                st.session_state.user_data = user
                st.experimental_rerun()
            else:
                st.error("פרטי התחברות שגויים")
    st.stop()

data = st.session_state.user_data
pages = ["משחק שאלון", "מילים לא ידועות", "מילים שאני כבר יודע", "הוספת מילים"]
selection = st.sidebar.selectbox("ניווט", pages)

if selection == "הוספת מילים":
    st.header("הוספת מילים")
    ew = st.text_input("מילה באנגלית")
    hw = st.text_input("תרגום לעברית")
    if st.button("הוסף"):
        if ew and hw:
            data["unknown"].append({"word": ew.strip(), "translation": hw.strip(), "correct": 0})
            save_user(st.session_state.username, data)
            st.experimental_rerun()
elif selection == "מילים לא ידועות":
    st.header("מילים לא ידועות")
    if data["unknown"]:
        for w in data["unknown"]:
            st.write(f'{w["word"]} - {w["translation"]} | ✓{w["correct"]}')
    else:
        st.info("אין מילים")
elif selection == "מילים שאני כבר יודע":
    st.header("מילים שאני כבר יודע")
    if data["known"]:
        for w in data["known"]:
            st.write(f'{w["word"]} - {w["translation"]}')
    else:
        st.info("אין מילים")
else:
    st.header("משחק שאלון")
    if len(data["unknown"]) < 10:
        st.warning("נדרש מינימום של 10 מילים כדי להתחיל לשחק")
    else:
        if "current_word" not in st.session_state:
            st.session_state.current_word = random.choice(data["unknown"])
        cw = st.session_state.current_word
        options = [cw["translation"]]
        pool = [w["translation"] for w in data["unknown"] if w["translation"] != cw["translation"]]
        if len(pool) >= 3:
            options.extend(random.sample(pool, 3))
        else:
            options.extend(random.sample(pool, len(pool)))
            kw = [w["translation"] for w in data["known"] if w["translation"] not in options]
            need = 4 - len(options)
            if kw:
                options.extend(random.sample(kw, min(need, len(kw))))
        random.shuffle(options)
        st.subheader(f'מה הפירוש של המילה: {cw["word"]}?')
        answer = st.radio("בחר תשובה", options, index=None)
        if st.button("שלח"):
            if answer == cw["translation"]:
                cw["correct"] += 1
                st.success("תשובה נכונה!")
                st.markdown('<style>body{background-color:#d4edda;}</style>', unsafe_allow_html=True)
                if cw["correct"] >= 5:
                    data["unknown"].remove(cw)
                    data["known"].append({"word": cw["word"], "translation": cw["translation"]})
            else:
                st.error(f'טעות. התשובה הנכונה היא: {cw["translation"]}')
                st.markdown('<style>body{background-color:#f8d7da;}</style>', unsafe_allow_html=True)
            save_user(st.session_state.username, data)
            if data["unknown"]:
                st.session_state.current_word = random.choice(data["unknown"])
            else:
                st.session_state.current_word = None
            st.experimental_rerun()
