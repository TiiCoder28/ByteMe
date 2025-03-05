# query_job.py
import openai
import psycopg2
import os
from dotenv import load_dotenv

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

def get_embedding(text):
    """Generates OpenAI embeddings."""
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def find_jobs_based_on_skills(job_description):
    """Finds jobs based on the candidate's qualifications, experience, and skills."""
    job_embedding = get_embedding(job_description)
    embedding_str = "[" + ",".join(map(str, job_embedding)) + "]"

    # Query the jobs in the database
    cur.execute(
        f"""
        SELECT name_of_job, experience_required, education_required, skills_required, preferred_qualifications
        FROM jobs
        ORDER BY job_embedding <=> '{embedding_str}'::vector
        LIMIT 5
        """
    )
    jobs = cur.fetchall()

    # Prepare the response with job details
    suitable_jobs = [
        {
            "name_of_job": row[0],
            "experience_required": row[1],
            "education_required": row[2],
            "skills_required": row[3],
            "preferred_qualifications": row[4],
        }
        for row in jobs
    ]
    
    return suitable_jobs
