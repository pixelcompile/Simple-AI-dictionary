import streamlit as st
from openai import OpenAI
import nltk
from nltk.stem import WordNetLemmatizer
from dotenv import load_dotenv
import os
import requests

nltk.download('wordnet', quiet=True)
lemmatizer = WordNetLemmatizer()

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Easy E-E Dictionary", page_icon="📘")
st.title("📘 Easy E-E Dictionary")
st.write("Easily understand English words — designed for beginners!")

# Get lemma (base form)
def get_base_form(word):
    return lemmatizer.lemmatize(word.lower(), pos='v')

# GPT query
def get_gpt_output(word):
    prompt = f"""
        Explain the word "{word}" in the following format:

        📘 Word: {word.capitalize()}
        📖 Part of Speech: (N for noun, V for verb, etc.)
        🔊 Pronunciation (IPA): 
        🔤 Simple Meaning: 
        🟢 Synonyms: 
        🔢 Singular: (only if noun)
        🔢 Plural: (only if noun)
        🔁 Past Simple: (only if verb)
        🔁 Past Participle: (only if verb)
        💬 Example:

        Use beginner-level English. Do not write anything outside this format.
        """

    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            input=[{"role": "user", "content": prompt}]
        )
        return response.output_text
    except Exception as e:
        return f"❌ Error: {e}"

# Format output to rules
def format_output(raw, base_word):
    lines = raw.strip().split('\n')
    part_of_speech = ""
    result = []

    # First pass: get part of speech
    for line in lines:
        if line.startswith("📖 Part of Speech:"):
            part_of_speech = line.split(":")[1].strip().upper()

    for line in lines:
        if line.startswith("📘 Word:"):
            result.append(f"📘 Word: {base_word.capitalize()}")
        elif line.startswith("📖"):
            result.append(line)
        elif line.startswith("🔊"):
            result.append(line)
        elif line.startswith("🔤"):
            content = line.split(":", 1)[1].strip()
            result.append(f"🔤 Simple Meaning: **{content}**")
        elif line.startswith("🟢"):
            result.append(line)
        elif line.startswith("💬"):
            content = line.split(":", 1)[1].strip()
            result.append(f"💬 Example: *{content}*")
        elif line.startswith("🔁") and part_of_speech == "V":
            result.append(line)
        elif line.startswith("🔢") and part_of_speech == "N":
            result.append(line)

    return "\n".join(result)

def fetch_image(word):
    url = f"https://api.unsplash.com/search/photos?query={word}&client_id={UNSPLASH_ACCESS_KEY}&per_page=1"
    try:
        response = requests.get(url)
        data = response.json()
        if data["results"]:
            image_url = data["results"][0]["urls"]["small"]
            return image_url
    except Exception as e:
        print("Image fetch error:", e)
    return None

# UI Input
word = st.text_input("Enter an English word to explain:")

if word.strip():  # Trigger when user presses Enter
    with st.spinner("🔎 Looking up..."):
        base = get_base_form(word)
        gpt_output = get_gpt_output(word)
        formatted = format_output(gpt_output, base)
        image_url = fetch_image(base)

        st.markdown("---")
        st.markdown(formatted)
        if image_url:
            st.image(image_url, caption=f"Illustration of '{base}'", use_column_width=True)
        st.markdown("---")