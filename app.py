import streamlit as st
from openai import OpenAI

# === App Config ===
st.set_page_config(page_title="MagicStory Global", page_icon="🌍")

# ==========================================
# 🔒 VIP Gate System
# ==========================================
def check_password():
    if "ACCESS_CODE" not in st.secrets:
        return True # Bypass if no code set
    
    # UI is now in English for global users
    password = st.sidebar.text_input("🔑 VIP Access Code", type="password")
    
    if password == st.secrets["ACCESS_CODE"]:
        st.sidebar.success("✅ Access Granted!")
        return True
    else:
        st.warning("🔒 VIP Content Locked")
        st.info("Please enter your Access Code in the sidebar.")
        st.stop()

check_password()
# ==========================================

# === Main Interface (English) ===
st.title("🌍 MagicStory Global")
st.subheader("Create Personalized Audiobooks for Kids")

# === Language Selector (關鍵升級：語言選單) ===
language = st.selectbox(
    "Select Story Language / 選擇故事語言", 
    ["English", "Traditional Chinese (繁體中文)", "Japanese (日本語)", "Spanish (Español)", "French (Français)"]
)

# Auto-detect API Key
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("OpenAI API Key", type="password")

# User Inputs (English UI)
col1, col2 = st.columns(2)
with col1:
    child_name = st.text_input("Child's Name", "Alex")
    companion = st.text_input("Companion (e.g., Dinosaur)", "Blue Dragon")
with col2:
    mission = st.text_input("Adventure/Mission", "Going to the Moon")
    # Voice selection
    voice_option = st.selectbox("Voice Style", ["nova (Gentle Female)", "alloy (Neutral)", "echo (Deep Male)", "shimmer (Bright Female)"])

# === Core Logic ===
if st.button("✨ Generate Magic Story", type="primary"):
    if not api_key:
        st.error("Error: API Key not found.")
    else:
        try:
            client = OpenAI(api_key=api_key)
            
            # 1. Text Generation (Multi-language Support)
            with st.spinner(f'Writing story in {language}...'):
                # 這裡的 Prompt 改成英文指令，但要求 AI 輸出成「用戶選的語言」
                prompt = f"""
                Write a warm, bedtime story for a 5-year-old child.
                Child's Name: {child_name}
                Companion: {companion}
                Adventure: {mission}
                
                Requirements:
                1. Length: Around 300 words.
                2. Language: Write the story ONLY in {language}.
                3. Tone: Fun, engaging, and educational.
                """
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]
                )
                story_text = response.choices[0].message.content
            
            st.success("Story created! Generating illustration...")
            st.markdown(f"### 📖 The Adventure of {child_name}")
            st.write(story_text)
            
            # 2. Image Generation (DALL-E 3)
            with st.spinner('Drawing illustration...'):
                # 繪圖提示詞維持英文，效果最好
                img_prompt = f"Children's book illustration, {child_name} and {companion} adventure: {mission}. Style: Pixar animation style, warm lighting, high quality."
                img_response = client.images.generate(
                    model="dall-e-3", prompt=img_prompt, size="1024x1024", quality="standard", n=1
                )
                st.image(img_response.data[0].url)

            # 3. Audio Generation (TTS)
            with st.spinner('Recording audio...'):
                voice_code = voice_option.split(" ")[0]
                audio_res = client.audio.speech.create(
                    model="tts-1", voice=voice_code, input=story_text
                )
                st.audio(audio_res.content)
                
        except Exception as e:
            st.error(f"Error: {e}")
