import streamlit as st
import ollama
import whisper
import tempfile
import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

# ------------------ DB Setup ------------------
Base = declarative_base()

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True)
    instruction = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

@st.cache_resource
def get_session():
    engine = create_engine("sqlite:///notemind.db", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

session = get_session()

# ------------------ Whisper ------------------
@st.cache_resource
def load_whisper():
    return whisper.load_model("base")  # tiny, base, small, medium, large

whisper_model = load_whisper()

# ------------------ UI ------------------
st.title("🧠 NoteMind")
st.caption("Your personal memory for important instructions.")

# Upload audio
audio_file = st.file_uploader("🎤 Upload an instruction recording (mp3/wav/m4a)", type=["mp3", "wav", "m4a"])

instruction_text = ""

if audio_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        temp_file.write(audio_file.read())
        temp_path = temp_file.name

    with st.spinner("Transcribing audio..."):
        result = whisper_model.transcribe(temp_path)
        instruction_text = result["text"]
        st.success("✅ Transcription complete:")
        st.write(instruction_text)

# OR manual input
manual_text = st.text_area("✏️ Or type/paste instructions here:", value=instruction_text)

# Summarize
if st.button("Summarize & Save"):
    if manual_text.strip():
        with st.spinner("Summarizing with Ollama..."):
            response = ollama.chat(
                model="llama2",
                messages=[
                    {"role": "system", "content": "Summarize clearly into bullet points."},
                    {"role": "user", "content": manual_text}
                ]
            )
            summary = response['message']['content']
            
            # Save to DB
            new_note = Note(instruction=manual_text, summary=summary)
            session.add(new_note)
            session.commit()

            st.success("✅ Summary generated & saved:")
            st.write(summary)
    else:
        st.warning("Please provide instructions first.")

# View Saved Notes
st.subheader("📚 Saved Instructions")
notes = session.query(Note).order_by(Note.created_at.desc()).all()

for note in notes:
    with st.expander(f"🗓️ {note.created_at.strftime('%Y-%m-%d %H:%M:%S')}"):
        st.write("**Original Instruction:**")
        st.write(note.instruction)
        st.write("**Summary:**")
        st.write(note.summary)
