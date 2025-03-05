import openai
import os
import psycopg2
import numpy as np
from dotenv import load_dotenv
import PyPDF2

# Load environment variables
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)
cur = conn.cursor()

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    return text

def get_embedding(text):
    """Generates OpenAI embeddings."""
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def update_embedding(table, text_column, embedding_column, id_column):
    """Updates missing embeddings in the given table."""
    cur.execute(f"SELECT {id_column}, {text_column} FROM {table} WHERE {embedding_column} IS NULL")
    records = cur.fetchall()

    if not records:
        print(f"✅ All {table} embeddings are up-to-date.")
        return

    print(f"🚀 Generating embeddings for {len(records)} records in {table}...")

    for record_id, text in records:
        if text:  # Ensure text is not None or empty
            embedding = get_embedding(text)
            cur.execute(
                f"""UPDATE {table}
                    SET {embedding_column} = %s::vector
                    WHERE {id_column} = %s""",
                (np.array(embedding).tolist(), record_id)
            )
    
    conn.commit()
    print(f"✅ Successfully updated embeddings for {table}.")

# Run updates
try:
    update_embedding("job_descriptions", "job_summary", "job_embedding", "id")
    update_embedding("resumes", "summary", "resume_embedding", "id")
finally:
    cur.close()
    conn.close()
    print("🔌 Database connection closed.")
