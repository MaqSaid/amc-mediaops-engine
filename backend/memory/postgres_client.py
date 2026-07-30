import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "mediaops")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres_secure_password")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Tasks table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id VARCHAR(255) PRIMARY KEY,
            content TEXT NOT NULL,
            content_type VARCHAR(50) NOT NULL,
            source VARCHAR(255) NOT NULL,
            status VARCHAR(50) NOT NULL, -- 'running', 'pending_review', 'completed', 'failed'
            intelligence_pack JSONB,
            evaluation JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Traces/Logs table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS traces (
            id SERIAL PRIMARY KEY,
            task_id VARCHAR(255) REFERENCES tasks(task_id) ON DELETE CASCADE,
            node_name VARCHAR(100) NOT NULL,
            inputs JSONB,
            outputs JSONB,
            duration_ms FLOAT,
            tokens_used INT DEFAULT 0,
            cost FLOAT DEFAULT 0.0,
            error_message TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    conn.commit()
    cur.close()
    conn.close()

def create_task(task_id, content, content_type, source, status="running"):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (task_id, content, content_type, source, status) VALUES (%s, %s, %s, %s, %s)",
        (task_id, content, content_type, source, status)
    )
    conn.commit()
    cur.close()
    conn.close()

def update_task_status(task_id, status, intelligence_pack=None, evaluation=None):
    conn = get_db_connection()
    cur = conn.cursor()
    if intelligence_pack is not None and evaluation is not None:
        cur.execute(
            "UPDATE tasks SET status=%s, intelligence_pack=%s, evaluation=%s, updated_at=%s WHERE task_id=%s",
            (status, json.dumps(intelligence_pack), json.dumps(evaluation), datetime.utcnow(), task_id)
        )
    elif intelligence_pack is not None:
        cur.execute(
            "UPDATE tasks SET status=%s, intelligence_pack=%s, updated_at=%s WHERE task_id=%s",
            (status, json.dumps(intelligence_pack), datetime.utcnow(), task_id)
        )
    else:
        cur.execute(
            "UPDATE tasks SET status=%s, updated_at=%s WHERE task_id=%s",
            (status, datetime.utcnow(), task_id)
        )
    conn.commit()
    cur.close()
    conn.close()

def add_trace(task_id, node_name, inputs, outputs=None, duration_ms=0.0, tokens_used=0, cost=0.0, error_message=None):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO traces (task_id, node_name, inputs, outputs, duration_ms, tokens_used, cost, error_message)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            task_id,
            node_name,
            json.dumps(inputs) if inputs else None,
            json.dumps(outputs) if outputs else None,
            duration_ms,
            tokens_used,
            cost,
            error_message
        )
    )
    conn.commit()
    cur.close()
    conn.close()

def get_all_tasks():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM tasks ORDER BY created_at DESC")
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    # Handle datetime JSON serializable issues later or convert here
    for t in tasks:
        t['created_at'] = t['created_at'].isoformat()
        t['updated_at'] = t['updated_at'].isoformat()
    return tasks

def get_task(task_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM tasks WHERE task_id = %s", (task_id,))
    task = cur.fetchone()
    cur.close()
    conn.close()
    if task:
        task['created_at'] = task['created_at'].isoformat()
        task['updated_at'] = task['updated_at'].isoformat()
    return task

def get_task_traces(task_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM traces WHERE task_id = %s ORDER BY timestamp ASC", (task_id,))
    traces = cur.fetchall()
    cur.close()
    conn.close()
    for tr in traces:
        tr['timestamp'] = tr['timestamp'].isoformat()
    return traces
