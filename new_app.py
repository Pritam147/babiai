import streamlit as st
import requests
import uuid
import time


BASE_URL = "http://localhost:8000"

st.title("REFLEX AI")
st.set_page_config(layout="wide")

# ------------------ Helpers ------------------


def new_thread_id():
    return f"thread-{uuid.uuid4().hex[:8]}"


def get_threads():
    r = requests.get(url=f"{BASE_URL}/chat/threads")
    r.raise_for_status()
    return r.json()


def get_history(thread_id):
    r = requests.get(url=f"{BASE_URL}/chat/history/{thread_id}")
    r.raise_for_status()
    return r.json()["message"]


def stream_send_message(thread_id, message):
    with requests.post(
        url=f"{BASE_URL}/chat/{thread_id}",
        params={"message": message},
        stream=True,  # Enables chunked transfer
    ) as r:
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                yield chunk


# ------------------ Session State ------------------

if "current_thread" not in st.session_state:
    st.session_state.current_thread = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------ Sidebar ------------------

st.sidebar.title("🧵 Threads")

threads = get_threads()

# Case 1: No threads exist
if not threads:
    st.sidebar.info("No threads yet")

    if st.sidebar.button("➕ New Thread"):
        tid = new_thread_id()
        st.session_state.current_thread = tid
        st.session_state.messages = []
        st.rerun()

# Case 2: Threads exist
else:
    for thread_id in threads:
        is_active = thread_id == st.session_state.current_thread

        label = f"👉 {thread_id}" if is_active else thread_id

        if st.sidebar.button(label, key=thread_id):
            st.session_state.current_thread = thread_id
            st.session_state.messages = get_history(thread_id)
            st.rerun()

    st.sidebar.divider()

    # New thread button always available
    if st.sidebar.button("➕ New Thread"):
        tid = new_thread_id()
        st.session_state.current_thread = tid
        st.session_state.messages = []
        st.rerun()


# ------------------ Main Chat ------------------

if not st.session_state.current_thread:
    st.info("Select a thread from the sidebar")
    st.stop()

st.subheader(f"💬 {st.session_state.current_thread}")

# Render messages
for msg in st.session_state.messages:
    role = msg.get("type", "chat")

    if role == "human":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    elif role == "ai":
        if msg["content"]:
            with st.chat_message("assistant"):
                st.markdown(msg["content"])
    # elif role == "system":
    #     with st.chat_message("system"):
    #         st.write(msg["content"])

# ------------------ Chat Input ------------------

user_input = st.chat_input("Type a message")

if user_input:
    # 1. Display user message immediately
    st.session_state.messages.append({"type": "human", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Handle Assistant Response
    with st.chat_message("assistant"):
        # The spinner will wrap the request initialization
        with st.spinner("Thinking..."):

            def stream_request():
                with requests.post(
                    url=f"{BASE_URL}/chat/{st.session_state.current_thread}",
                    params={"message": user_input},
                    stream=True,  # Keeps connection open for tokens
                ) as r:
                    r.raise_for_status()
                    for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
                        if chunk:
                            yield chunk

            # We initialize the generator before passing it to write_stream
            gen = stream_request()

            # This 'peek' at the first token can be done, but st.write_stream
            # is smart enough to start as soon as data arrives.
            full_response = st.write_stream(gen)

    # 3. Save to history
    st.session_state.messages.append({"type": "ai", "content": full_response})
