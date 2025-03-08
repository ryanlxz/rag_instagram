import streamlit as st
import ollama
import requests
import json

query_url = "http://localhost:8000/query"

st.set_page_config(page_title="Chat with a Star Wars expert", page_icon="🦜")
st.title("_Chat_ with :blue[A Star Wars Expert] 🤖")
with st.sidebar:
    # Returns the list of ollama models available in ollama on the device
    models_ollama = ollama.list()["models"]
    # extract name and size of the model (in GB)
    model_name = [m["name"] for m in models_ollama]
    model_size = [float(m["size"]) for m in models_ollama]
    name_detail = zip(model_name, model_size)
    # Sort the models based on their size, in ascending order. Faster (smaller models) first
    name_detail = sorted(name_detail, key=lambda x: x[1])
    model_info = [f"{name}  Size: {size/(10**9):.2f}GB" for name, size in name_detail]
    st.caption(
        "You will see here the models downloaded from Ollama. For installing ollama: https://ollama.com/download.  \nFor the models available: https://ollama.com/library.  \n⚠️ Remember: Heavily quantized models will perform slightly worse but much faster."
    )

    # Add a textbox to start the chat
    user_input = st.text_input("Start Chat:")
    if st.button("🐻"):
        if user_input:
            # st.session_state.chat_started = True
            response = requests.post(
                url=query_url, params={"query": user_input}, stream=True
            )
            for line in response.iter_lines():
                if line:
                    st.write(line.decode("utf-8"))
