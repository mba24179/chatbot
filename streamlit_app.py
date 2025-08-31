import streamlit as st
from openai import OpenAI, RateLimitError, AuthenticationError
import re

# ---------------- CONFIG ----------------
# Store API key in Streamlit Secrets for security
OPENAI_API_KEY = st.secrets.get("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", None)
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# ---------------- HELPER FUNCTIONS ----------------
def safe_chatbot_call(user_input):
    """Try OpenAI API; if quota exceeded, return mock reply"""
    if not client:
        return "⚠️ No API key found. Running in demo mode."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
You are ChaufX Concierge, a premium chauffeur booking assistant.
1. Ride Booking: confirm with ✅ if pickup, drop, date, time provided.
2. FAQ: answer pricing, fleet, cancellation, payment policies politely and concisely.
"""
                },
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content

    except RateLimitError:
        # Demo fallback response
        return f"✅ (Demo Mode) Ride booked! Pickup: Connaught Place, Drop: Delhi Airport, Date: Tomorrow, Time: 8 AM.\nDriver: Rajesh Kumar 🚖, Car: Mercedes S-Class"
    except AuthenticationError:
        return "⚠️ Invalid API key. Please configure in Streamlit Secrets."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

def extract_booking_info(chat_response):
    pattern = r"Pickup: (.+)\nDrop: (.+)\nDate: (.+)\nTime: (.+)"
    match = re.search(pattern, chat_response)
    if match:
        return {
            "pickup": match.group(1).strip(),
            "drop": match.group(2).strip(),
            "date": match.group(3).strip(),
            "time": match.group(4).strip(),
            "user_name": "VIP Customer"
        }
    return None

# ---------------- STREAMLIT UI ----------------
st.set_page_config(page_title="ChaufX Concierge", page_icon="🚘")
st.title("🤖 ChaufX Concierge")
st.markdown("Your premium chauffeur booking assistant.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.chat_input("Type your message...")

if user_input:
    # Add user message
    st.session_state.chat_history.append(("You", user_input))

    # Get assistant response (real or mock)
    reply = safe_chatbot_call(user_input)
    st.session_state.chat_history.append(("ChaufX Concierge", reply))

    # Extract booking info
    booking_info = extract_booking_info(reply)
    if booking_info:
        confirmation = f"✅ Booking confirmed! Driver: Rajesh Kumar 🚖, Car: Mercedes S-Class"
        st.session_state.chat_history.append(("ChaufX Concierge", confirmation))

# Render chat
for role, msg in st.session_state.chat_history:
    if role == "You":
        st.chat_message("user").write(msg)
    else:
        st.chat_message("assistant").write(msg)
