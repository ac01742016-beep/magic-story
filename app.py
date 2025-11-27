import streamlit as st
from openai import OpenAI

# === 網頁設定 ===
st.set_page_config(page_title="MagicStory 魔法故事屋 v2.0", page_icon="🦄")
st.title("🦄 MagicStory 魔法故事屋 v2.0")
st.subheader("為您的孩子客製化專屬的有聲繪本")

# === 自動取得鑰匙 (支援本地與雲端) ===
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("請輸入 OpenAI API Key", type="password")

# === 主畫面：輸入故事元素 ===
col1, col2 = st.columns(2)
with col1:
    child_name = st.text_input("小朋友的名字", "小寶")
    companion = st.text_input("故事夥伴 (如：機器貓)", "粉紅獨角獸")
with col2:
    mission = st.text_input("今天的冒險/任務", "去火星探險")
    voice_option = st.selectbox("選擇說故事聲音", ["nova (溫柔女聲)", "alloy (中性)", "echo (沉穩男聲)", "shimmer (清亮女聲)"])

# === 核心邏輯 ===
if st.button("✨ 開始創作有聲繪本", type="primary"):
    if not api_key:
        st.error("🔑 尚未設定 API Key！")
    else:
        try:
            client = OpenAI(api_key=api_key)
            
            # --- 階段一：文字生成 ---
            with st.spinner('正在編寫故事中... (AI 思考中)'):
                story_prompt = f"請為5歲的{child_name}和夥伴{companion}寫一個關於{mission}的溫馨睡前故事，繁體中文，350字以內。語氣要生動有趣。"
                
                response_text = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": story_prompt}]
                )
                story_text = response_text.choices[0].message.content
            
            # 顯示故事文字
            st.success("故事寫好了！接下來繪製插圖...")
            st.markdown(f"### 📖 {child_name} 的冒險")
            st.write(story_text)
            
            # --- 階段二：(新增!) 圖片生成 DALL-E 3 ---
            # 我們設計一個專門給畫家的提示詞，要求溫馨的繪本風格
            image_prompt = f"A warm, whimsical children's book illustration showing {child_name} (a young child) and a {companion} on an adventure: {mission}. Style: Studio Ghibli animation, gentle colors, magical atmosphere."
            
            with st.spinner('正在繪製插圖... (DALL-E 畫家中，約需 10-15 秒)'):
                response_image = client.images.generate(
                    model="dall-e-3",
                    prompt=image_prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                image_url = response_image.data[0].url
            
            # 顯示圖片
            st.image(image_url, caption=f"{child_name} 與 {companion} 的冒險瞬間")

            # --- 階段三：語音生成 ---
            with st.spinner('正在錄製聲音... (最後一步!)'):
                voice_code = voice_option.split(" ")[0]
                response_audio = client.audio.speech.create(
                    model="tts-1",
                    voice=voice_code,
                    input=story_text
                )
                
                # 播放聲音
                st.markdown("### 🎧 點擊播放有聲書")
                st.audio(response_audio.content)
                
        except Exception as e:
            st.error(f"發生錯誤（可能是餘額不足或網路問題）：{e}")
