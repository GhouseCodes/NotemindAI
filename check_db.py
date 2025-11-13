from sqlalchemy import create_engine, Column, Integer, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime

# Define database connection
engine = create_engine("sqlite:///notemind.db")
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# Define Note model
class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True)
    instruction = Column(Text)
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Make sure table exists
Base.metadata.create_all(engine)

# Query and display notes
notes = session.query(Note).all()
if notes:
    for note in notes:
        print(f"ID: {note.id}")
        print(f"Instruction: {note.instruction}")
        print(f"Summary: {note.summary}")
        print(f"Created At: {note.created_at}")
        print("-" * 40)
else:
    print("⚠️ No notes found in database.")

session.close()
