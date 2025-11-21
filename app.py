import streamlit as st
from groq import Groq

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Llama 4 Lab Controller", layout="wide")

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.image("https://www.cais.usc.edu/wp-content/uploads/2022/10/Meta-logo-e1667246992948.png", width=150)
    st.title("⚙️ Control Panel")
    
    # 1. API Key Input (Secure)
    api_key = st.text_input("Enter Groq API Key:", type="password")
    
    st.divider()

    # 2. Model Switcher
    st.subheader("🧠 Model Architecture")
    model_option = st.radio(
        "Choose your Brain:",
        ["Llama 4 Scout (Fast/Vision)", "Llama 4 Maverick (Smart/Deep)"],
        index=1
    )
    
    # Map friendly names to actual Groq Model IDs
    if "Scout" in model_option:
        selected_model = "meta-llama/llama-4-scout-17b-16e-instruct"
        st.info("Selected: Low Latency, Multimodal capable.")
    else:
        selected_model = "meta-llama/llama-4-maverick-17b-128e-instruct"
        st.info("Selected: High Reasoning, Deep Logic.")

    st.divider()

    # 3. Memory Toggle
    st.subheader("🧠 Memory State")
    memory_enabled = st.toggle("Enable Conversation Memory", value=True)
    if memory_enabled:
        st.success("Status: Remembering Context")
    else:
        st.error("Status: Amnesia Mode (Stateless)")

    st.divider()

    # 4. System Prompt Editor
    st.subheader("🎭 System Persona")
    default_prompt = "You are a helpful, witty assistant teaching AI concepts to students in Nigeria."
    system_prompt = st.text_area("Edit the Brain's Rules:", value=default_prompt, height=150)

    # Clear Chat Button
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# --- MAIN CHAT INTERFACE ---
st.title("💬 Meta Llama 4")

# Initialize Chat History in Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize Groq Client
if api_key:
    client = Groq(api_key=api_key)
else:
    st.warning("⚠️ Please enter your Groq API Key in the sidebar to start.")
    st.stop()

# Display Chat History on Screen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CHAT LOGIC ---
if prompt := st.chat_input("Type your message here..."):
    # 1. Add User Message to Visual History
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Construct the Payload based on Settings
    messages_payload = []

    # Always add the System Prompt first
    messages_payload.append({"role": "system", "content": system_prompt})

    if memory_enabled:
        # Pass EVERYTHING (History + New Message)
        # We skip the first item in session_state if we manually added system prompt elsewhere, 
        # but here session_state only has user/assistant turns.
        messages_payload.extend(st.session_state.messages)
    else:
        # Pass ONLY the System Prompt + CURRENT Message (Ignore history)
        # This proves the model is stateless without context
        messages_payload.append({"role": "user", "content": prompt})

    # 3. Generate Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            stream = client.chat.completions.create(
                model=selected_model,
                messages=messages_payload,
                temperature=0.7,
                max_tokens=1024,
                stream=True, 
            )
            
            # Stream the output to look cool
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
            # 4. Add Assistant Response to History
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Error calling API: {e}")