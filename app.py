import streamlit as st
from openai import OpenAI

# === 網頁設定 ===
st.set_page_config(page_title="MagicStory 魔法故事屋 VIP版", page_icon="🦄")

# ==========================================
# 🔒 VIP 門禁系統 (這段是新增的)
# ==========================================
def check_password():
    """檢查用戶輸入的密碼是否正確"""
    # 1. 如果後台沒設密碼，就直接放行 (避免您自己測試時卡住)
    if "ACCESS_CODE" not in st.secrets:
        return True
    
    # 2. 在側邊欄顯示密碼框
    password = st.sidebar.text_input("🔑 請輸入 VIP 通行碼", type="password")
    
    # 3. 比對密碼
    if password == st.secrets["ACCESS_CODE"]:
        st.sidebar.success("✅ 驗證成功！歡迎 VIP 會員")
        return True
    else:
        # 如果密碼還沒輸，或是輸錯
        st.warning("🔒 這是付費會員專屬區域")
        st.info("請在左側輸入通行碼來解鎖功能。")
        st.stop() # ⛔ 這裡最關鍵：直接卡住，不讓程式往下跑

# 執行檢查 (如果不通過，程式就會在這裡停住)
check_password()
# ==========================================


# === 下面才是原本的功能 (只有通過檢查才會執行) ===
st.title("🦄 MagicStory 魔法故事屋")
st.subheader("為您的孩子客製化專屬的有聲繪本")

# 自動取得 API Key
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    # 備用方案
    api_key = st.sidebar.text_input("OpenAI API Key", type="password")

col1, col2 = st.columns(2)
with col1:
    child_name = st.text_input("小朋友的名字", "小寶")
    companion = st.text_input("故事夥伴", "粉紅獨角獸")
with col2:
    mission = st.text_input("今天的冒險/任務", "去火星探險")
    voice_option = st.selectbox("說故事聲音", ["nova (溫柔女聲)", "alloy (中性)", "echo (沉穩男聲)"])

if st.button("✨ 開始創作有聲繪本", type="primary"):
    if not api_key:
        st.error("系統設定錯誤：找不到 API Key")
    else:
        try:
            client = OpenAI(api_key=api_key)
            
            # 1. 文字
            with st.spinner('AI 正在編故事...'):
                prompt = f"請為5歲的{child_name}和夥伴{companion}寫一個關於{mission}的溫馨睡前故事，繁體中文，350字以內。"
                response = client.chat.completions.create(
                    model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]
                )
                story_text = response.choices[0].message.content
            
            st.success("故事完成！正在繪圖...")
            st.write(story_text)
            
            # 2. 圖片 (DALL-E 3)
            with st.spinner('AI 畫家中...'):
                img_prompt = f"Children's book illustration, {child_name} and {companion} adventure: {mission}, warm style."
                img_response = client.images.generate(
                    model="dall-e-3", prompt=img_prompt, size="1024x1024", quality="standard", n=1
                )
                st.image(img_response.data[0].url)

            # 3. 語音
            with st.spinner('錄製聲音中...'):
                voice_code = voice_option.split(" ")[0]
                audio_res = client.audio.speech.create(
                    model="tts-1", voice=voice_code, input=story_text
                )
                st.audio(audio_res.content)
                
        except Exception as e:
            st.error(f"錯誤：{e}")
