import streamlit as st
import google.generativeai as genai
import json
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Dev Connect AI", page_icon="🌐", layout="wide")

# --- MOCK DATABASE (The "Real World" Population) ---
developers = [
    {"id": 1, "name": "Alice Chen", "role": "Frontend Architect", "stack": "React, TypeScript, Tailwind", "bio": "Obsessed with pixel-perfect UI. I hate backend logic. If it doesn't look good, it doesn't work.", "avatar": "🎨", "style": "Visual & Creative"},
    {"id": 2, "name": "Bob Smith", "role": "Backend Specialist", "stack": "Python, Django, PostgreSQL", "bio": "I optimize queries for fun. Frontend CSS scares me. I build robust APIs that never crash.", "avatar": "⚙️", "style": "Logical & Blunt"},
    {"id": 3, "name": "Charlie Kim", "role": "Fullstack Founder", "stack": "Node.js, MongoDB, AWS", "bio": "Shipping MVPs in 48 hours. I value speed over code quality. Let's just launch it.", "avatar": "🚀", "style": "Energetic & Fast"},
    {"id": 4, "name": "Dana White", "role": "AI Engineer", "stack": "PyTorch, HuggingFace, LangChain", "bio": "Fine-tuning LLMs and building RAG pipelines. I speak in vectors and embeddings.", "avatar": "🧠", "style": "Academic & Complex"},
    {"id": 5, "name": "Evan Wright", "role": "DevOps Engineer", "stack": "Docker, Kubernetes, Terraform", "bio": "If you deploy manually, we can't be friends. I automate everything.", "avatar": "🐳", "style": "Strict & Organized"},
    {"id": 6, "name": "Fiona Gallagher", "role": "Mobile Dev", "stack": "Flutter, Dart, Firebase", "bio": "Building cross-platform apps. I care about touch interactions and 60fps performance.", "avatar": "📱", "style": "User-Focused"},
    {"id": 7, "name": "Greg House", "role": "Cybersecurity", "stack": "Kali Linux, Penetration Testing", "bio": "I break things to make them stronger. Your API keys are probably leaked already.", "avatar": "🔒", "style": "Paranoid & Careful"},
    {"id": 8, "name": "Hannah Lee", "role": "Game Developer", "stack": "Unity, C#, Shader Graph", "bio": "Making indie games. I know 3D math and physics engines. Gamers are the toughest users.", "avatar": "🎮", "style": "Playful & Technical"},
    {"id": 9, "name": "Ian Malcolm", "role": "Data Scientist", "stack": "R, Pandas, Tableau", "bio": "Data tells a story. I clean messy datasets and find hidden trends.", "avatar": "📊", "style": "Analytical"},
    {"id": 10, "name": "Jack Sparrow", "role": "Blockchain Dev", "stack": "Solidity, Rust, Web3.js", "bio": "Building decentralized apps. Code is law. WAGMI.", "avatar": "⛓️", "style": "Crypto-Native"},
    {"id": 11, "name": "Karen Page", "role": "Project Manager", "stack": "Jira, Agile, Scrum", "bio": "I keep developers on track. No, we cannot add that feature in this sprint.", "avatar": "📅", "style": "Organized & Pushy"},
    {"id": 12, "name": "Leo Messi", "role": "Junior Dev", "stack": "HTML, CSS, JavaScript", "bio": "Just graduated bootcamp! Eager to learn everything. Looking for a mentor.", "avatar": "🎓", "style": "Curious & Humble"}
]

# --- SESSION STATE ---
if "messages" not in st.session_state: st.session_state.messages = []
if "user_profile" not in st.session_state: st.session_state.user_profile = None
if "selected_match" not in st.session_state: st.session_state.selected_match = None

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Google API Key:", type="password")
    
    selected_model = "gemini-1.5-flash"
    if api_key:
        try:
            genai.configure(api_key=api_key)
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if models:
                if "models/gemini-1.5-flash" in models:
                    selected_model = "models/gemini-1.5-flash"
                else:
                    selected_model = models[0]
                st.success(f"✅ Online: {selected_model}")
        except:
            st.error("❌ Key Error")
            
    st.markdown("---")
    st.caption(f"👥 Community Members: **{len(developers)}**")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# --- AI FUNCTIONS ---
def find_best_match(user_bio):
    model = genai.GenerativeModel(selected_model)
    prompt = f"""
    Act as a CTO matchmaker.
    User Bio: "{user_bio}"
    Community Database: {json.dumps(developers)}
    
    Task: Select the ONE best person from the database to work with this user.
    Return JSON only: {{"name": "Name from DB", "reason": "Why"}}
    """
    try:
        response = model.generate_content(prompt)
        clean = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except:
        return {"name": "Error", "reason": "AI busy."}

def chat_with_persona(user_msg, persona_name, file_context=None):
    # Find the persona data
    persona = next((p for p in developers if p["name"] == persona_name), None)
    if not persona: return "Error: User left."
    
    model = genai.GenerativeModel(selected_model)
    
    # Customize prompt if a file was attached
    file_instruction = ""
    if file_context:
        file_instruction = f"USER JUST SENT A FILE: {file_context}. React to receiving this file based on your personality (e.g. if image, comment on design; if code, comment on logic)."

    prompt = f"""
    ROLEPLAY INSTRUCTION:
    You are {persona['name']}.
    Role: {persona['role']}
    Bio: {persona['bio']}
    Personality: {persona['style']}
    Tech Stack: {persona['stack']}
    
    Current Chat Context: User said "{user_msg}"
    {file_instruction}
    
    Reply as {persona['name']}. 
    - Keep it short (under 40 words).
    - Be helpful but stay in character.
    - If you are "Blunt", be blunt. If "Humble", be humble.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "..."

# --- UI LAYOUT ---
st.title("🌐 Dev Connect Global")

# LOGIN SCREEN
if not st.session_state.user_profile:
    st.subheader("👋 Create Profile")
    with st.form("login"):
        name = st.text_input("Name")
        bio = st.text_area("Skills & Interests")
        if st.form_submit_button("Join Community") and api_key:
            st.session_state.user_profile = {"name": name, "bio": bio}
            st.rerun()

# MAIN DASHBOARD
else:
    # Top Bar
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"Logged in as **{st.session_state.user_profile['name']}**")
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.user_profile = None
            st.rerun()
    
    tab1, tab2, tab3 = st.tabs(["👥 Browse Community", "🤖 AI Matchmaker", "💬 Private Chat"])
    
    # --- TAB 1: BROWSE COMMUNITY ---
    with tab1:
        st.write("### Explore Profiles")
        cols = st.columns(3)
        for i, dev in enumerate(developers):
            with cols[i % 3]:
                with st.container(border=True):
                    st.write(f"### {dev['avatar']} {dev['name']}")
                    st.caption(f"**{dev['role']}**")
                    st.write(f"🛠 {dev['stack']}")
                    st.write(f"_{dev['bio']}_")
                    if st.button(f"Message {dev['name'].split()[0]}", key=f"btn_{dev['id']}"):
                        st.session_state.selected_match = dev
                        st.session_state.messages = [] 
                        st.toast(f"Started chat with {dev['name']}!", icon="💬")
    
    # --- TAB 2: AI MATCHMAKER ---
    with tab2:
        st.write("### Let AI Find Your Partner")
        if st.button("Analyze My Profile & Find Match", type="primary"):
            with st.spinner("AI is interviewing candidates..."):
                match_result = find_best_match(st.session_state.user_profile['bio'])
                if match_result.get("name") != "Error":
                    full_profile = next(d for d in developers if d["name"] == match_result["name"])
                    st.session_state.selected_match = full_profile
                    st.session_state.messages = []
                    st.balloons()
                    st.success(f"**Best Match:** {full_profile['name']}")
                    st.info(f"**AI Logic:** {match_result['reason']}")
                    st.button("Go to Chat ➡️")

    # --- TAB 3: MULTIMEDIA CHAT ROOM ---
    with tab3:
        if not st.session_state.selected_match:
            st.info("👈 Select a person from the **Browse** or **Matchmaker** tab to start chatting.")
        else:
            target = st.session_state.selected_match
            st.write(f"### 💬 Chat with {target['name']}")
            st.caption(f"Role: {target['role']} | Style: {target['style']}")
            
            # 1. Chat Container (History)
            chat_box = st.container(height=400)
            with chat_box:
                for msg in st.session_state.messages:
                    with st.chat_message(msg["role"]):
                        # Render Text
                        if "content" in msg and msg["content"]:
                            st.markdown(msg["content"])
                        
                        # Render Files (The New Feature)
                        if "file_data" in msg:
                            f_type = msg["file_type"]
                            f_name = msg["file_name"]
                            
                            if "image" in f_type:
                                st.image(msg["file_data"], caption=f_name)
                            elif "video" in f_type:
                                st.video(msg["file_data"])
                            else:
                                st.warning(f"📎 Attached File: {f_name}")

            # 2. File Uploader Section
            with st.expander("📎 Attach File (Image, Video, Code)", expanded=False):
                uploaded_file = st.file_uploader("Upload assets to share", accept_multiple_files=False)
                send_file = st.button("Send File")
            
            # 3. Text Input
            prompt = st.chat_input("Type your message...")

            # --- LOGIC TO HANDLE INPUTS ---
            
            # CASE A: User Sends a FILE
            if send_file and uploaded_file:
                # Add file to chat history
                st.session_state.messages.append({
                    "role": "user", 
                    "content": f"Shared a file: {uploaded_file.name}", 
                    "file_data": uploaded_file,
                    "file_type": uploaded_file.type,
                    "file_name": uploaded_file.name
                })
                st.rerun() # Refresh to show file immediately

            # CASE B: User Sends TEXT
            if prompt:
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                # Check if the PREVIOUS message was a file (to give context to AI)
                last_msg = st.session_state.messages[-2] if len(st.session_state.messages) > 1 else {}
                file_context = last_msg.get("file_name", None) if last_msg.get("role") == "user" else None

                with chat_box:
                    with st.chat_message("user"):
                        st.markdown(prompt)

                # AI Reply Logic
                with st.spinner(f"{target['name']} is typing..."):
                    reply = chat_with_persona(prompt, target['name'], file_context)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    with chat_box:
                        with st.chat_message("assistant", avatar=target['avatar']):
                            st.markdown(reply)