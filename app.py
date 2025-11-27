import streamlit as st
from openai import OpenAI

# === 網頁設定 ===
st.set_page_config(page_title="MagicStory 魔法故事屋", page_icon="🦄")

st.title("🦄 MagicStory 魔法故事屋")
st.subheader("為您的孩子客製化專屬的睡前故事")

# === 側邊欄：設定 API Key ===
with st.sidebar:
    st.markdown("### ⚙️ 設定")
    # 這裡讓您輸入 Key，這樣比較安全，不會把 Key 寫死在程式碼裡
    api_key = st.text_input("請輸入 OpenAI API Key", type="password")
    st.markdown("[按這裡取得 API Key](https://platform.openai.com/api-keys)")

# === 主畫面：輸入故事元素 ===
col1, col2 = st.columns(2)
with col1:
    child_name = st.text_input("小朋友的名字", "小寶")
    companion = st.text_input("故事夥伴 (如：機器貓)", "粉紅獨角獸")
with col2:
    mission = st.text_input("今天的冒險/任務", "去火星探險")
    voice_option = st.selectbox("選擇說故事聲音", ["nova (溫柔女聲)", "alloy (中性)", "echo (沉穩男聲)", "shimmer (清亮女聲)"])

# === 核心邏輯 ===
if st.button("✨ 開始生成故事", type="primary"):
    if not api_key:
        st.error("請先在左側輸入您的 OpenAI API Key 喔！")
    else:
        try:
            client = OpenAI(api_key=api_key)
            
            # 1. 生成文字
            with st.spinner('正在編寫故事中... (AI 思考中)'):
                prompt = f"請為5歲的{child_name}和夥伴{companion}寫一個關於{mission}的溫馨睡前故事，繁體中文，300字以內。語氣要生動有趣。"
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                story_text = response.choices[0].message.content
                
            st.success("故事寫好了！")
            st.markdown(f"### 📖 {child_name} 的冒險")
            st.write(story_text)

            # 2. 生成語音
            with st.spinner('正在錄製聲音... (這可能需要幾秒鐘)'):
                voice_code = voice_option.split(" ")[0] # 取出 nova, alloy 等代碼
                response_audio = client.audio.speech.create(
                    model="tts-1",
                    voice=voice_code,
                    input=story_text
                )
                
                # 存成暫存檔並播放
                audio_file = "story_output.mp3"
                response_audio.stream_to_file(audio_file)
                
                st.markdown("### 🎧 點擊播放")
                st.audio(audio_file)
                
        except Exception as e:
            st.error(f"發生錯誤：{e}")