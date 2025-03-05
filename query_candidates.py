import psycopg2
import numpy as np
import os
import openai
from dotenv import load_dotenv
from process_pdfs import extract_text_from_pdf, get_embedding

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

def find_best_candidates(job_text):
    """Finds the best candidates based on job description embeddings."""
    
    # Generate embedding for the job text
    job_embedding = get_embedding(job_text)
    
    # Convert embedding to a string format PostgreSQL understands
    embedding_str = "[" + ",".join(map(str, job_embedding)) + "]"

    cur.execute(
        f"""
        SELECT id, summary, resume_embedding <=> '{embedding_str}'::vector AS similarity
        FROM resumes
        ORDER BY similarity ASC
        LIMIT 5
        """
    )
    
    return cur.fetchall()


# Load job description from a PDF and find best candidates
job_text = extract_text_from_pdf("./data/job_descriptions.pdf")
best_candidates = find_best_candidates(job_text)

# Print the results
print("Top matching candidates:")
for candidate in best_candidates:
    print(candidate)

# Close the database connection
cur.close()
conn.close()
