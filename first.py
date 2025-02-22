import streamlit as st
import psycopg2
import openai
import numpy as np
from sentence_transformers import SentenceTransformer

# Load Embedding Model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Database Connection
DB_PARAMS = {
    "dbname": "demodb",
    "user": "postgres",
    "password": "Vivek@123",
    "host": "localhost",
    "port": "5432"
}

# Connect to PostgreSQL
def connect_db():
    return psycopg2.connect(**DB_PARAMS)

# Function to Convert Natural Language to SQL using OpenAI
def generate_sql_query(user_query):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an SQL expert. Convert user queries into safe SQL queries for PostgreSQL."},
            {"role": "user", "content": user_query}
        ]
    )
    return response["choices"][0]["message"]["content"].strip()

# Function to Execute SQL Query
def execute_query(sql_query):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(sql_query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# Function for Vector Search
def vector_search(user_query, table, column):
    query_embedding = model.encode([user_query])[0]
    sql_query = f"""
    SELECT {column}, (embedding <-> %s) AS distance
    FROM {table} ORDER BY distance ASC LIMIT 5;
    """
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(sql_query, (query_embedding.tolist(),))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# Streamlit UI
st.title("🔍 Natural Language Search Interface")
user_query = st.text_input("Enter your search query:")
if st.button("Search"):
    try:
        sql_query = generate_sql_query(user_query)
        results = execute_query(sql_query)
        st.write("### Query Results:")
        st.dataframe(results)
    except Exception as e:
        st.error(f"Error: {e}")
