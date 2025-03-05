from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
import psycopg2
import numpy as np
from query_jobs import find_jobs_based_on_skills
from dotenv import load_dotenv
from pydantic import BaseModel

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

# Create FastAPI app
app = FastAPI()

# CORS middleware to allow the frontend to communicate with the backend
origins = [
    "http://localhost:5173",  # Assuming Vite is running on this port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows frontend to access backend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class JobQuery(BaseModel):
    job_description: str

def get_embedding(text):
    """Generates OpenAI embeddings."""
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

@app.post("/find_candidates")
def find_candidates(query: JobQuery):
    """Finds the best candidates based on job description embeddings."""
    job_embedding = get_embedding(query.job_description)
    embedding_str = "[" + ",".join(map(str, job_embedding)) + "]"

    cur.execute(
        f"""
        SELECT id, candidate_name, qualifications, certifications, experience
        FROM resumes
        ORDER BY resume_embedding <=> '{embedding_str}'::vector
        LIMIT 1
        """
    )
    candidates = cur.fetchall()

    # Prepare the response with candidate details
    top_candidates = [
        {
            "name": row[1],
            "qualifications": row[2],
            "certifications": row[3],
            "experience": row[4],
        }
        for row in candidates
    ]
    return {"candidates": top_candidates}

@app.post("/find_jobs")
def find_jobs(query: JobQuery):
    """Finds the best job matches based on the candidate's qualifications."""
    suitable_jobs = find_jobs_based_on_skills(query.job_description)  # Call function from query_job.py
    return {"jobs": suitable_jobs}
