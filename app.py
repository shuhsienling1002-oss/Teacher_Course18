import streamlit as st
import time
import os
import random
from gtts import gTTS
from io import BytesIO

# --- 0. 系統配置 ---
st.set_page_config(
    page_title="阿美語 - 時間與手錶", 
    page_icon="⌚", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# --- CSS 視覺魔法 (午夜星空與金色時刻風格) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&family=Noto+Sans+TC:wght@400;700&display=swap');

    /* 全局背景：深藍色午夜漸層 */
    .stApp { 
        background-color: #0D47A1;
        background-image: linear-gradient(135deg, #0a192f 0%, #112240 50%, #233554 100%);
        font-family: 'Noto Sans TC', sans-serif;
        color: #E6F1FF;
    }
    
    .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; }

    /* --- Header --- */
    .header-container {
        background: rgba(17, 34, 64, 0.8);
        border: 1px solid #64FFDA; /* 青綠色光邊 */
        box-shadow: 0 0 20px rgba(100, 255, 218, 0.1);
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        margin-bottom: 40px;
        backdrop-filter: blur(10px);
    }
    
    .main-title {
        font-family: 'Roboto Mono', monospace;
        color: #64FFDA; /* 螢光青 */
        font-size: 42px;
        font-weight: 700;
        letter-spacing: 4px;
        text-transform: uppercase;
        text-shadow: 0 0 10px rgba(100, 255, 218, 0.5);
        margin: 0;
    }
    
    .sub-title { color: #8892B0; font-size: 18px; margin-top: 10px; letter-spacing: 2px; }
    
    .teacher-tag { 
        display: inline-block; 
        margin-top: 20px; 
        padding: 5px 20px; 
        border: 1px solid #FFD700; 
        color: #FFD700; /* 金色 */
        border-radius: 0px; /* 方形邊角，更現代 */
        font-size: 12px; 
        letter-spacing: 1px;
    }

    /* --- Cards (單字卡 - 深色玻璃質感) --- */
    .word-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 20px 10px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
        height: 100%;
        margin-bottom: 15px;
        transition: transform 0.3s, border-color 0.3s;
    }
    
    .word-card h3 {
        color: #FFD700 !important; /* 金色標題 */
        font-family: 'Roboto Mono', monospace;
        font-weight: 700;
        margin: 0;
        padding-bottom: 8px;
        font-size: 20px;
    }

    .word-card:hover { 
        transform: translateY(-5px); 
        border-color: #64FFDA; 
        background: rgba(255, 255, 255, 0.1);
    }
    
    .icon-box { font-size: 32px; margin-bottom: 10px; opacity: 0.9; }
    .amis-word { font-size: 18px; color: #E6F1FF; margin-bottom: 5px; }
    .zh-word { font-size: 14px; color: #8892B0; }

    /* --- Sentences (句子框 - 科技感) --- */
    .sentence-box {
        background: #112240;
        border-left: 4px solid #FFD700; /* 金色左邊框 */
        padding: 20px;
        margin-bottom: 20px;
        border-radius: 5px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .sentence-amis { font-size: 18px; color: #64FFDA; font-weight: 500; margin-bottom: 8px; font-family: 'Roboto Mono', monospace; }
    .sentence-zh { font-size: 15px; color: #A8B2D1; }

    /* --- Buttons --- */
    .stButton>button { 
        width: 100%; 
        border-radius: 5px; 
        background: transparent; 
        border: 2px solid #64FFDA; 
        color: #64FFDA !important; 
        font-weight: bold; 
        transition: all 0.3s;
    }
    .stButton>button:hover { 
        background: rgba(100, 255, 218, 0.1); 
        box-shadow: 0 0 15px rgba(100, 255, 218, 0.4);
    }

    /* --- Tabs --- */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        color: #8892B0 !important; 
        background-color: transparent !important;
        border-bottom: 2px solid transparent !important;
        padding: 10px 0px;
        font-size: 16px;
    }
    .stTabs [aria-selected="true"] {
        color: #FFD700 !important;
        border-bottom: 2px solid #FFD700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 資料設定 (主題：Tuki 時間與手錶) ---
VOCABULARY = [
    {"amis": "Pinaay tu",   "zh": "多少了(問數量/時間)", "emoji": "❓", "file": "v_pinaay_tu"},
    {"amis": "anini",       "zh": "現在",             "emoji": "👇", "file": "v_anini"},
    {"amis": "siwa",        "zh": "九",               "emoji": "9️⃣", "file": "v_siwa"},
    {"amis": "satukien",    "zh": "戴手錶",           "emoji": "⌚", "file": "v_satukien"},
    {"amis": "kina",        "zh": "這(支)",           "emoji": "point", "file": "v_kina"},
    {"amis": "katangasaan", "zh": "已經到(時間)",      "emoji": "⏰", "file": "v_katangasaan"},
    {"amis": "nima",        "zh": "誰的",             "emoji": "👤", "file": "v_nima"},
    {"amis": "nipavelian",  "zh": "所給的",           "emoji": "🎁", "file": "v_nipavelian"},
    {"amis": "ina",         "zh": "媽媽",             "emoji": "👩‍👧", "file": "v_ina"},
]

SENTENCES = [
    {"amis": "U tuki nu maku kiniyan.", 
     "zh": "這支是我的手錶。", 
     "emoji": "⌚", "file": "s_u_tuki_nu_maku"},
     
    {"amis": "Pinaay tu ku tuki anini?", 
     "zh": "現在幾點了呢?", 
     "emoji": "🤔", "file": "s_pinaay_tu"},
     
    {"amis": "Siwaay tu ku tuki anini.", 
     "zh": "現在九點鐘了。", 
     "emoji": "🕘", "file": "s_siwaay_tu"},
     
    {"amis": "Satukien kina tuki.", 
     "zh": "這支手錶帶上。", 
     "emoji": "👋", "file": "s_satukien"},
     
    {"amis": "Katangasaan tu ku tuki.", 
     "zh": "時間已經到了。", 
     "emoji": "⌛", "file": "s_katangasaan"},
     
    {"amis": "U tuki nima kiniyan?", 
     "zh": "這是誰的手錶？", 
     "emoji": "🤷", "file": "s_u_tuki_nima"},
     
    {"amis": "U nipavelian ni ina kina a tuki.", 
     "zh": "這支手錶是我媽媽送給我的。", 
     "emoji": "💝", "file": "s_nipavelian"},
]

# 測驗題庫
QUIZ_DATA = [
    {"q": "______ tu ku tuki anini? / 現在幾點了?", "zh": "多少了", "ans": "Pinaay", "opts": ["Pinaay", "Siwa", "Nima"]},
    {"q": "U tuki ______ kiniyan? / 這是誰的手錶?", "zh": "誰的", "ans": "nima", "opts": ["nima", "ina", "anini"]},
    {"q": "______ / 九", "zh": "九", "ans": "siwa", "opts": ["siwa", "lima", "enem"]},
    {"q": "______ tu ku tuki. / 時間到了", "zh": "已經到", "ans": "Katangasaan", "opts": ["Katangasaan", "Satukien", "Pinaay"]},
    {"q": "U nipavelian ni ______ / 媽媽給的", "zh": "媽媽", "ans": "ina", "opts": ["ina", "ama", "vaki"]},
]

# --- 1.5 語音核心 ---
def play_audio(text, filename_base=None):
    if filename_base:
        extensions = ['m4a', 'mp3', 'wav']
        folders = ['audio', '.'] 
        for folder in folders:
            for ext in extensions:
                path = os.path.join(folder, f"{filename_base}.{ext}")
                if os.path.exists(path):
                    mime = 'audio/mp4' if ext == 'm4a' else 'audio/mp3'
                    st.audio(path, format=mime)
                    return 
        # 找不到檔案時的提示 (深色背景版)
        st.markdown(f"<span style='color:#FF5252; font-size:12px; background:rgba(0,0,0,0.5); padding:2px;'>🔇 缺音檔: {filename_base}</span>", unsafe_allow_html=True)
    else:
        try:
            speak_text = text.split('/')[0].strip()
            tts = gTTS(text=speak_text, lang='id') 
            fp = BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            st.audio(fp, format='audio/mp3')
        except:
            st.caption("🔇")

# --- 2. 測驗邏輯 ---
def init_quiz():
    st.session_state.score = 0
    st.session_state.current_q = 0
    
    # Q1: 聽力
    q1_target = random.choice(VOCABULARY)
    others = [v for v in VOCABULARY if v['amis'] != q1_target['amis']]
    q1_options = random.sample(others, 2) + [q1_target]
    random.shuffle(q1_options)
    st.session_state.q1_data = {"target": q1_target, "options": q1_options}

    # Q2: 填空
    q2_data = random.choice(QUIZ_DATA)
    random.shuffle(q2_data['opts'])
    st.session_state.q2_data = q2_data

    # Q3: 句子翻譯
    q3_target = random.choice(SENTENCES)
    other_sentences = [s['zh'] for s in SENTENCES if s['zh'] != q3_target['zh']]
    if len(other_sentences) < 2:
        q3_options = other_sentences + [q3_target['zh']] + ["時間還沒到"]
        q3_options = q3_options[:3]
    else:
        q3_options = random.sample(other_sentences, 2) + [q3_target['zh']]
    random.shuffle(q3_options)
    st.session_state.q3_data = {"target": q3_target, "options": q3_options}

if 'q1_data' not in st.session_state:
    init_quiz()

# --- 3. 介面呈現 ---
def show_learning_mode():
    st.markdown("<h3 style='color:#FFD700; text-align:center; margin-bottom:20px; font-family:Roboto Mono;'>VOCABULARY</h3>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    for idx, item in enumerate(VOCABULARY):
        with cols[idx % 3]:
            # 處理 emoji 顯示 (如果是 point 則換成手指)
            icon = "👇" if item['emoji'] == "point" else item['emoji']
            
            st.markdown(f"""
            <div class="word-card">
                <div class="icon-box">{icon}</div>
                <h3>{item['amis']}</h3>
                <div class="zh-word">{item['zh']}</div>
            </div>
            """, unsafe_allow_html=True)
            play_audio(item['amis'], filename_base=item['file'])
            st.write("") 

    st.markdown("---")
    st.markdown("<h3 style='color:#FFD700; text-align:center; margin-bottom:20px; font-family:Roboto Mono;'>SENTENCES</h3>", unsafe_allow_html=True)
    
    for item in SENTENCES:
        st.markdown(f"""
        <div class="sentence-box">
            <div class="sentence-amis">{item['emoji']} {item['amis']}</div>
            <div class="sentence-zh">{item['zh']}</div>
        </div>
        """, unsafe_allow_html=True)
        play_audio(item['amis'], filename_base=item['file'])

def show_quiz_mode():
    st.markdown("<h3 style='text-align: center; color: #64FFDA;'>TIME CHALLENGE</h3>", unsafe_allow_html=True)
    st.progress((st.session_state.current_q) / 3)
    st.write("")

    if st.session_state.current_q == 0:
        data = st.session_state.q1_data
        target = data['target']
        st.markdown(f"""
        <div class="word-card" style="border-color:#64FFDA; background:rgba(100,255,218,0.1);">
            <h3 style="color:#64FFDA !important;">🎧 聽音辨位</h3>
        </div>
        """, unsafe_allow_html=True)
        play_audio(target['amis'], filename_base=target['file'])
        st.write("")
        
        cols = st.columns(3)
        for idx, opt in enumerate(data['options']):
            with cols[idx]:
                if st.button(f"{opt['zh']}", key=f"q1_{idx}"):
                    if opt['amis'] == target['amis']:
                        st.balloons()
                        st.success("Correct! 答對了")
                        time.sleep(1)
                        st.session_state.score += 1
                        st.session_state.current_q += 1
                        st.rerun()
                    else:
                        st.error("Try Again")

    elif st.session_state.current_q == 1:
        data = st.session_state.q2_data
        st.markdown(f"""
        <div class="word-card" style="border-color:#FFD700;">
            <h3>🧩 填空/選擇</h3>
            <h2 style="color:#E6F1FF;">{data['q'].replace('______', '<span style="color:#FFD700">___</span>')}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(3)
        for i, opt in enumerate(data['opts']):
            with cols[i]:
                if st.button(opt, key=f"q2_{i}"):
                    if opt.lower() in data['ans'].lower() or data['ans'].lower() in opt.lower():
                        st.balloons()
                        st.success("Excellent!")
                        time.sleep(1)
                        st.session_state.score += 1
                        st.session_state.current_q += 1
                        st.rerun()
                    else:
                        st.error("Incorrect")

    elif st.session_state.current_q == 2:
        data = st.session_state.q3_data
        target = data['target']
        st.markdown(f"""
        <div class="word-card" style="border-color:#64FFDA;">
            <h3>🗣️ 翻譯挑戰</h3>
            <h3 style="color:#64FFDA !important;">{target['amis']}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        play_audio(target['amis'], filename_base=target['file'])
        
        for opt in data['options']:
            if st.button(opt):
                if opt == target['zh']:
                    st.balloons()
                    st.success("Perfect!")
                    time.sleep(1)
                    st.session_state.score += 1
                    st.session_state.current_q += 1
                    st.rerun()
                else:
                    st.error("Not quite")

    else:
        st.markdown(f"""
        <div class="word-card" style="border-color: #FFD700; background: rgba(255, 215, 0, 0.1);">
            <h1 style='color: #FFD700 !important;'>MISSION COMPLETE</h1>
            <p style='color: #E6F1FF;'>SCORE: {st.session_state.score} / 3</p>
            <div style='font-size: 60px;'>🏆</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("RESTART"):
            init_quiz()
            st.rerun()

# --- 4. 診斷工具 ---
def show_debug_info():
    st.markdown("---")
    st.markdown("<div style='text-align:center; color:#8892B0; font-size:12px;'>System Status: Online</div>", unsafe_allow_html=True)
    
    files_audio = []
    if os.path.exists("audio"):
        files_audio = [f for f in os.listdir('audio') if f.endswith('.m4a') or f.endswith('.mp3')]

    if not files_audio:
        st.info("💡 尚未偵測到音檔，請建立 audio 資料夾。")

# --- 主程式 ---
def main():
    st.markdown("""
    <div class="header-container">
        <h1 class="main-title">TUKI</h1>
        <div class="sub-title">手錶與時間</div>
        <div class="teacher-tag">講師：胡美芳 | 教材提供者：胡美芳</div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🕰️ 學習模式 (LEARN)", "🚀 時間挑戰 (QUIZ)"])
    
    with tab1:
        show_learning_mode()
    with tab2:
        show_quiz_mode()
        
    show_debug_info()

if __name__ == "__main__":
    main()
