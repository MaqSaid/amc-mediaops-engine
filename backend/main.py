import os
import uuid
import time
import asyncio
import logging
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Import memory/db clients
from memory.postgres_client import (
    init_db, create_task, update_task_status, add_trace,
    get_all_tasks, get_task, get_task_traces
)
from memory.redis_client import RedisClient
from seed_data.seed import seed_database

# Import agents
from agents.supervisor import SupervisorAgent
from agents.specialists import RetrievalAgent, MetadataAgent, WriterAgent
from agents.judge import JudgeAgent

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MediaOpsEngine")

app = FastAPI(title="Australian Media Channel MediaOps Agentic Workflow Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_client = RedisClient()

# Startup event
@app.on_event("startup")
def startup_event():
    logger.info("Initializing databases and starting up...")
    try:
        init_db()
        logger.info("PostgreSQL database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize PostgreSQL: {e}")
        
    try:
        seed_database()
        logger.info("ChromaDB seeding logic execution triggered.")
    except Exception as e:
        logger.error(f"Failed to run ChromaDB database seeding: {e}")


# Pydantic Schemas
class MediaInput(BaseModel):
    content: str
    content_type: str # 'article', 'transcript', 'brief'
    source: str

class EditorialIntelligencePack(BaseModel):
    executive_summary: str
    key_themes: List[str]
    metadata_tags: List[str]
    editorial_risk_flags: List[str]
    suggested_headlines: List[str]

class JudgeEvaluation(BaseModel):
    factuality_score: int
    policy_compliance: bool
    feedback: str
    requires_human_review: bool

class ReviewRequest(BaseModel):
    action: str # 'approve', 'modify', 'reject', 'take_over'
    modified_pack: Optional[Dict[str, Any]] = None
    feedback: Optional[str] = None

# Workflow Execution Core Loop
async def execute_agent_workflow(task_id: str, content: str, content_type: str, source: str):
    logger.info(f"Starting workflow execution for task: {task_id}")
    
    # Instantiate agents
    supervisor = SupervisorAgent()
    retrieval = RetrievalAgent()
    metadata_extractor = MetadataAgent()
    writer = WriterAgent()
    judge = JudgeAgent()

    try:
        # Step 1: Supervisor planning
        t0 = time.time()
        plan, sup_engine = await supervisor.create_plan(content, content_type, source)
        duration = (time.time() - t0) * 1000
        add_trace(task_id, f"Supervisor Planning [{sup_engine}]", {"content": content[:100]}, plan, duration)
        
        # Save plan to Redis working memory
        redis_client.set_state(task_id, {"plan": plan, "step": "planning"})

        # Step 2: Retrieval
        t0 = time.time()
        retrieved_context, ret_engine = await retrieval.retrieve_context("Retrieve guidelines and related articles", content)
        duration = (time.time() - t0) * 1000
        add_trace(task_id, f"Retrieval Specialist [{ret_engine}]", {"task": "document matching"}, {"context": retrieved_context}, duration)

        # Step 3: Metadata Extraction
        t0 = time.time()
        meta_data, meta_engine = await metadata_extractor.extract_metadata(content, retrieved_context)
        duration = (time.time() - t0) * 1000
        add_trace(task_id, f"Metadata Specialist [{meta_engine}]", {"content_length": len(content)}, meta_data, duration)

        # Step 4: Writer Synthesis
        t0 = time.time()
        intelligence_pack, writer_engine = await writer.generate_pack(content, retrieved_context, meta_data)
        duration = (time.time() - t0) * 1000
        add_trace(task_id, f"Writer Specialist [{writer_engine}]", {"metadata": meta_data}, intelligence_pack, duration)

        # Step 5: Judge Evaluation
        t0 = time.time()
        evaluation, judge_engine = await judge.evaluate_pack(content, intelligence_pack)
        duration = (time.time() - t0) * 1000
        add_trace(task_id, f"Judge Quality Evaluation [{judge_engine}]", {"pack": intelligence_pack}, evaluation, duration)


        # Cache step progress
        redis_client.set_state(task_id, {
            "intelligence_pack": intelligence_pack,
            "evaluation": evaluation,
            "step": "evaluation"
        })

        # Step 6: Route based on Judge Review
        if evaluation.get("requires_human_review", False):
            logger.info(f"Task {task_id} requires human review. Suspending execution.")
            update_task_status(task_id, "pending_review", intelligence_pack, evaluation)
        else:
            logger.info(f"Task {task_id} passed validation. Completing execution.")
            update_task_status(task_id, "completed", intelligence_pack, evaluation)
            redis_client.delete_state(task_id)

    except Exception as e:
        logger.error(f"Error executing agent workflow for task {task_id}: {e}")
        update_task_status(task_id, "failed")
        add_trace(task_id, "Workflow Failure", {}, {}, 0.0, error_message=str(e))

# REST API Routing
@app.post("/api/submit")
async def submit_content(media_input: MediaInput, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    try:
        create_task(task_id, media_input.content, media_input.content_type, media_input.source)
        background_tasks.add_task(
            execute_agent_workflow,
            task_id,
            media_input.content,
            media_input.content_type,
            media_input.source
        )
        return {"task_id": task_id, "status": "running"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks")
def list_tasks():
    try:
        return get_all_tasks()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/{task_id}")
def get_task_details(task_id: str):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    traces = get_task_traces(task_id)
    return {"task": task, "traces": traces}

@app.get("/api/review-queue")
def get_review_queue():
    try:
        all_tasks = get_all_tasks()
        return [t for t in all_tasks if t["status"] == "pending_review"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/review/{task_id}")
def submit_human_review(task_id: str, review_req: ReviewRequest):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task["status"] != "pending_review":
        raise HTTPException(status_code=400, detail="Task is not in pending_review status")

    action = review_req.action.lower()
    
    # Load original evaluation to update
    eval_data = task["evaluation"] or {}
    eval_data["requires_human_review"] = False
    eval_data["human_feedback"] = review_req.feedback
    eval_data["human_action"] = action
    
    final_pack = task["intelligence_pack"]
    
    if action == "approve":
        status = "completed"
    elif action == "modify" or action == "take_over":
        status = "completed"
        if review_req.modified_pack:
            final_pack = review_req.modified_pack
    elif action == "reject":
        status = "failed"
    else:
        raise HTTPException(status_code=400, detail=f"Invalid action: {action}")
        
    try:
        # Update the task status, final intelligence pack, and the evaluation results
        update_task_status(task_id, status, final_pack, eval_data)
        
        # Log HITL trace
        add_trace(
            task_id,
            f"Human-in-the-Loop ({action.upper()})",
            {"feedback": review_req.feedback, "action": action},
            {"final_pack": final_pack},
            0.0
        )
        
        # Clean Redis cache
        redis_client.delete_state(task_id)
        
        return {"status": "success", "task_status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
