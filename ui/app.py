"""FaultLens RAG - Streamlit UI.

Run with:  uv run streamlit run ui/app.py
The FastAPI service must be running on API_URL (default http://localhost:8000).
"""

import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

MODELS = [
    "SB 2000HF",
    "SB 2500HF",
    "SB 3000HF",
    "SB 3000TL",
    "SB 4000TL",
    "SB 5000TL",
    "Fronius Symo 10.0-3-M",
    "Fronius Symo 15.0-3-M",
    "Fronius Symo 17.5-3-M",
    "Fronius Symo 20.0-3-M",
    "Fronius Symo 24.0-3-M",
    "Other / free text",
]

# ---------------------------------------------------------------------------
# Page config - narrow layout feels like a phone on desktop too
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="FaultLens",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.title("⚡ FaultLens")
st.caption("Inverter fault assistant - ask in plain English or enter an event code.")

# ---------------------------------------------------------------------------
# Input form
# ---------------------------------------------------------------------------
with st.form("ask_form"):
    model_choice = st.selectbox("Inverter model", MODELS)
    if model_choice == "Other / free text":
        model_value = st.text_input("Enter model name")
    else:
        model_value = model_choice

    question = st.text_input(
        "Question or event code",
        placeholder="e.g. Event 34  or  What does the red LED mean?",
    )
    submitted = st.form_submit_button("Ask", use_container_width=True, type="primary")

# ---------------------------------------------------------------------------
# Call the API when the form is submitted
# ---------------------------------------------------------------------------
if submitted and question.strip():
    with st.spinner("Thinking…"):
        try:
            resp = requests.post(
                f"{API_URL}/ask",
                json={"question": question, "model": model_value or None},
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            st.session_state["last_answer"] = data
            st.session_state["last_question"] = question
            st.session_state["feedback"] = None
        except requests.exceptions.ConnectionError:
            st.error("Could not reach the API. Is the FastAPI server running?")
            st.stop()
        except requests.exceptions.HTTPError as e:
            st.error(f"API error: {e}")
            st.stop()

# ---------------------------------------------------------------------------
# Display the answer stored in session state
# ---------------------------------------------------------------------------
answer = st.session_state.get("last_answer")

if answer is None:
    st.stop()

if answer.get("abstained"):
    st.warning(
        "I could not find a reliable answer for this query in the available manuals. "
        "Please check the event code and inverter model, or consult the full manual."
    )
    st.stop()

# Safety warnings - always first so they're not missed on a small screen
if answer.get("safety"):
    for warning in answer["safety"]:
        st.error(f"⚠️ {warning}")

st.subheader(answer.get("diagnosis", ""))

if answer.get("causes"):
    with st.expander("Possible causes", expanded=True):
        for cause in answer["causes"]:
            st.markdown(f"- {cause}")

if answer.get("steps"):
    with st.expander("Resolution steps", expanded=True):
        for i, step in enumerate(answer["steps"], 1):
            st.markdown(f"**{i}.** {step}")

# Citations and page images
if answer.get("citations"):
    st.divider()
    st.markdown("**Sources**")
    for cit in answer["citations"]:
        label = f"{cit['ref']} - {cit['doc_id']} p.{cit['page']}"
        with st.expander(label):
            img_url = f"{API_URL}{cit['page_image_url']}"
            try:
                img_resp = requests.get(img_url, timeout=10)
                if img_resp.status_code == 200:
                    st.image(img_resp.content, use_container_width=True)
                else:
                    st.caption(f"Page image not available ({img_resp.status_code})")
            except requests.exceptions.ConnectionError:
                st.caption("Page image not available (API unreachable)")

# ---------------------------------------------------------------------------
# Feedback buttons - POST to /feedback when clicked
# ---------------------------------------------------------------------------
st.divider()
st.markdown("**Was this helpful?**")
col1, col2 = st.columns(2)


def _send_feedback(vote: str) -> None:
    if st.session_state.get("feedback"):
        return
    st.session_state["feedback"] = vote
    try:
        requests.post(
            f"{API_URL}/feedback",
            json={
                "trace_id": answer["trace_id"],
                "question": st.session_state.get("last_question", ""),
                "vote": vote,
            },
            timeout=5,
        )
    except requests.exceptions.RequestException:
        pass


with col1:
    if st.button("👍 Yes", use_container_width=True):
        _send_feedback("up")
with col2:
    if st.button("👎 No", use_container_width=True):
        _send_feedback("down")

if st.session_state.get("feedback") == "up":
    st.success("Thanks for the feedback!")
elif st.session_state.get("feedback") == "down":
    st.info("Thanks - we'll use this to improve the system.")
