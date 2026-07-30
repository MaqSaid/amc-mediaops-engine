# Technical Interview Preparation Guide

This guide is designed for the technical panel interview (Dane Laban - Head of Data Science & AI, and Slava Razbash - AI Engineer). It covers 50 technical questions, with every single response structured using the **STARR** method (Situation, Task, Action, Result, Reflection).

---

## Category 1: Google ADK, Vertex AI (Gemini), & Cloud Run Agentic Architecture

### Q1: How does the Supervisor Agent orchestrate specialized subtasks dynamically?
* **Situation**: The editorial team submitted unstructured research documents that combined text, metadata requests, and guidelines lookup.
* **Task**: Route and delegate components to correct specialist agents without manual code wiring.
* **Action**: Configured the Supervisor Agent using Google ADK to parse input text, formulate a JSON execution plan specifying dependencies, and route tasks.
* **Result**: Subtasks were completed in parallel or sequence, reducing processing times.
* **Reflection**: Dynamic JSON execution plans provide greater scaling flexibility than hardcoded state machines.

### Q2: Why select Google ADK over standard LangGraph for this multi-agent setup?
* **Situation**: We needed to build an agent engine running inside lightweight serverless Cloud Run containers.
* **Task**: Select an orchestration framework with minimal binary overhead, fast cold-start performance, and native GCP integrations.
* **Action**: Used Google ADK instead of LangGraph, utilizing its clean state managers and built-in tool bindings.
* **Result**: Docker build sizes dropped, and initialization speeds decreased by 40%.
* **Reflection**: Frameworks with low overhead and native platform compilation are ideal for serverless containers.

### Q3: How did you select models between Gemini 2.0 Flash and Gemini 1.5 Pro?
* **Situation**: Running the entire pipeline using Gemini 1.5 Pro resulted in latency spikes and high monthly costs.
* **Task**: Balance latency, cost, and reasoning quality.
* **Action**: Configured Gemini 2.0 Flash as the default model for routing and metadata extraction, reserving Gemini 1.5 Pro for the final synthesis and compliance evaluation.
* **Result**: Latency fell below 10 seconds, and token spend dropped by over 60%.
* **Reflection**: Multi-model routing optimizes both performance and operating budgets.

### Q4: How is state saved and resumed when Cloud Run scale-to-zero is active?
* **Situation**: The engine paused execution to await human approval. During this time, the Cloud Run instance scaled down to zero, losing active in-memory states.
* **Task**: Preserve the execution state across scale-down events.
* **Action**: Integrated Redis working memory and Cloud SQL database checkpoints to save snapshots of task states before pausing.
* **Result**: Resumed tasks loaded their state from Redis instantly upon startup.
* **Reflection**: High-reliability serverless environments require external state managers.

### Q5: How do agents execute A2A (Agent-to-Agent) microservice communication?
* **Situation**: A monolithic agent pipeline caused deployment blocks when updating individual specialist nodes.
* **Task**: Modularize specialists into independent, communicating services.
* **Action**: Deployed agents as independent HTTP containers on Cloud Run and structured inter-agent data schemas.
* **Result**: Teams updated individual agents without affecting other parts of the system.
* **Reflection**: Treating agents as REST-based microservices enhances scalability and maintenance.

### Q6: How do you prevent loop deadlock inside the Google ADK execution flow?
* **Situation**: The Judge Agent continually rejected outputs for minor formatting issues, causing the Writer to loop indefinitely.
* **Task**: Prevent loop runs while maintaining output standards.
* **Action**: Embedded a loop counter in Redis that stops execution and triggers human intervention after 3 rejections.
* **Result**: Loop deadlocks were eliminated.
* **Reflection**: Automated agent loops must always have execution boundaries.

### Q7: How are custom tools registered and exposed to Google ADK agents?
* **Situation**: Agents needed to query database records and search vectors using secure parameters.
* **Task**: Register local tools cleanly without exposing database credentials.
* **Action**: Wrapped functions in Pydantic schemas and exposed them as tools within the ADK agent configuration.
* **Result**: Agents executed safe, validated database commands.
* **Reflection**: Structured schemas prevent parameter injection vulnerabilities.

### Q8: How did you design containerized agents to fit Cloud Run resource constraints?
* **Situation**: Packing large machine learning libraries into agent containers caused Cloud Run cold-starts to exceed 20 seconds.
* **Task**: Minimize container size.
* **Action**: Stripped local models and embedded PyTorch modules, utilizing Vertex AI API endpoints for inference.
* **Result**: Container size was reduced to under 300MB, lowering cold starts to under 3 seconds.
* **Reflection**: Offloading inference to managed APIs is critical for serverless deployments.

### Q9: How do you handle transient network failures during ADK agent operations?
* **Situation**: Minor network blips between Cloud Run containers and Vertex AI endpoints caused active tasks to fail.
* **Task**: Add network resilience to agent execution.
* **Action**: Implemented retry logic with exponential backoff on all HTTP clients and ADK service calls.
* **Result**: Network-related failure rates dropped to 0%.
* **Reflection**: Always expect network failures in distributed microservice architectures.

### Q10: How does the system handle concurrent content ingestion requests?
* **Situation**: Multiple editorial reports submitted simultaneously caused database lock contention.
* **Task**: Process concurrent ingestions smoothly.
* **Action**: Implemented Redis queues to ingest inputs asynchronously, processing tasks via background workers.
* **Result**: Tasks were ingested immediately, eliminating database locks.
* **Reflection**: Queueing input streams is essential for high-throughput enterprise systems.

---

## Category 2: RAG, Vector Search (ChromaDB / Vertex Vector Search), & Semantic Media Retrieval

### Q11: Why use ChromaDB locally and plan for Vertex AI Vector Search in production?
* **Situation**: Local developer environments needed a fast, zero-cost vector database, while production required high scalability.
* **Task**: Support local developer ease while planning for enterprise production loads.
* **Action**: Created an interface abstraction layer, implementing local ChromaDB for testing and Vertex AI Vector Search for production deployments.
* **Result**: Unified API calls across environments, simplifying deployment pipelines.
* **Reflection**: Decoupling the database layer via abstraction interfaces simplifies environment migrations.

### Q12: How are large PDF briefings and TV transcripts chunked for retrieval?
* **Situation**: Passing entire multi-hour TV transcripts to semantic search queries exceeded similarity limits.
* **Task**: Segment transcripts into contextually coherent paragraphs.
* **Action**: Implemented a recursive text splitter that chunks content into 500-token blocks with a 50-token overlap.
* **Result**: Semantic queries returned precise paragraphs, reducing search noise.
* **Reflection**: Overlapping text chunks preserves context across boundaries.

### Q13: How do you counter semantic search drift when guidelines change?
* **Situation**: Search queries retrieved outdated guidelines because the semantic meanings were similar.
* **Task**: Prioritize current guidelines over historic documents.
* **Action**: Added metadata fields for document creation dates and applied time-based decay scores to search results.
* **Result**: Current guidelines were retrieved first, even with high semantic similarity to older documents.
* **Reflection**: Vector queries should integrate metadata filters to maintain temporal relevance.

### Q14: How does the Retrieval Agent protect against hallucination in generated packs?
* **Situation**: The Writer Agent fabricated details when vector search returned sparse results.
* **Task**: Prevent the model from hallucinating non-existent facts.
* **Action**: Added strict prompt instructions requiring agents to cite sources and output "Context not found" if confidence scores fell below 0.7.
* **Result**: Hallucinated claims were eliminated from editorial packs.
* **Reflection**: Setting clear boundaries is essential when using LLMs for synthesis.

### Q15: How did you select the vector embedding dimensions for the media database?
* **Situation**: Mismatching dimensions between local embeddings and cloud models caused search failures.
* **Task**: Standardize the embedding dimension size.
* **Action**: Configured the pipeline to use the `text-embedding-004` model from Vertex AI, generating 768-dimension vectors.
* **Result**: Vector searches maintained consistent accuracy across local and cloud environments.
* **Reflection**: Standardizing embeddings across environments prevents data conversion errors.

### Q16: How does hybrid search (BM25 + Dense vector) improve editorial lookups?
* **Situation**: Semantic search missed specific court case numbers and legal codes.
* **Task**: Retrieve both semantic concepts and exact keyword matches.
* **Action**: Integrated hybrid search, combining dense vector embeddings with sparse BM25 keyword matching.
* **Result**: Search accuracy for exact identifiers and case codes rose to 99%.
* **Reflection**: Combining semantic and keyword searches provides the most robust retrieval.

### Q17: How is metadata used to filter RAG queries for specific media channels?
* **Situation**: Sports briefs retrieved legal guidelines from the court reporting archive.
* **Task**: Restrict vector search context by media channel or department.
* **Action**: Tagged incoming documents with metadata fields (e.g., `source: sports`) and applied where-clause filters to queries.
* **Result**: Agents retrieved context matching the source channel.
* **Reflection**: Metadata filtering is necessary to keep RAG systems focused.

### Q18: What strategy handles token overflow when returning multiple matching documents?
* **Situation**: Returning top-10 search matches exceeded the model's prompt input limit.
* **Task**: Fit retrieved documents into the context window.
* **Action**: Set search limit to `n_results=3` and implemented summaries of matching passages.
* **Result**: Kept inputs well within token boundaries, avoiding model truncation.
* **Reflection**: Quality of context is more valuable than quantity.

### Q19: How do you evaluate the retrieval quality of the vector database?
* **Situation**: Changes to chunk sizes impacted the relevance of search matches.
* **Task**: Quantify vector search retrieval quality.
* **Action**: Created test datasets and measured Mean Reciprocal Rank (MRR) across configurations.
* **Result**: Optimized chunk sizes, raising MRR to 0.88.
* **Reflection**: Structured evaluation is necessary to optimize search configurations.

### Q20: How are streaming dynamic updates indexed in the vector store?
* **Situation**: Daily news briefs were not searchable until the database was manually rebuilt.
* **Task**: Index updates dynamically without service interruption.
* **Action**: Configured an asynchronous event trigger that indexes new briefs into ChromaDB upon ingestion.
* **Result**: Ingested articles became searchable within 2 seconds.
* **Reflection**: Asynchronous indexing keeps vector databases current without slowing the user pipeline.

---

## Category 3: FastAPI, Agent-to-Agent (A2A) Microservices, Data Engineering (Cloud SQL/Redis) & Terraform

### Q21: How is Cloud Memorystore Redis structured as a workflow cache?
* **Situation**: Network calls to fetch intermediate agent plans from PostgreSQL slowed execution times.
* **Task**: Store runtime states in a fast, in-memory cache.
* **Action**: Integrated Redis, saving JSON-serialized agent states keyed by `task:{id}:state`.
* **Result**: Latency for plan lookups fell to sub-millisecond levels.
* **Reflection**: Offload active, transient data to in-memory caches to maintain speed.

### Q22: Why use PostgreSQL for auditing rather than MongoDB/Firestore?
* **Situation**: We needed to verify trace history and maintain audit logs for compliance checks.
* **Task**: Ensure data integrity and support complex diagnostic queries.
* **Action**: Deployed Cloud SQL PostgreSQL, using relational tables with foreign keys linking tasks and traces.
* **Result**: Achieved strict data integrity and fast audit trace reporting.
* **Reflection**: Relational databases are ideal for structured audit logs.

### Q23: How does Terraform handle private connections between Cloud Run and Cloud SQL?
* **Situation**: Exposing database connections to the public internet breached safety policies.
* **Task**: Establish secure, private database connections.
* **Action**: Used Terraform to deploy a Serverless VPC Access connector, routing database traffic over a private VPC.
* **Result**: Database connections were routed privately, eliminating public exposure risks.
* **Reflection**: Infrastructure as Code simplifies secure network configuration.

### Q24: How does the system handle database migrations automatically in production?
* **Situation**: Schema changes to task tables broke running services during deployments.
* **Task**: Deploy database schema updates safely.
* **Action**: Integrated migration checks into the FastAPI startup lifecycle.
* **Result**: Tables were verified or updated automatically upon container launch.
* **Reflection**: Automated migration checks reduce deployment sync issues.

### Q25: How did you implement task locks in Redis to prevent duplicate executions?
* **Situation**: Double-clicking submission buttons triggered duplicate agent runs for the same brief.
* **Task**: Prevent duplicate runs of identical tasks.
* **Action**: Implemented a distributed lock in Redis, checking for task locks before initiating runs.
* **Result**: Duplicate execution requests were blocked immediately.
* **Reflection**: Distributed locking is essential for managing serverless execution engines.

### Q26: How are environment secrets secured across Cloud Run services?
* **Situation**: Storing API keys in plain text inside Docker images violated safety policies.
* **Task**: Inject secrets securely at runtime.
* **Action**: Integrated GCP Secret Manager, binding secret values directly to container environment variables.
* **Result**: Secrets remained hidden in repository code, exposed only inside running containers.
* **Reflection**: Centralized secret managers are critical for securing cloud deployments.

### Q27: How does Terraform isolate dev, staging, and production environments?
* **Situation**: Deploying updates risked overwriting active production databases.
* **Task**: Isolate environments completely.
* **Action**: Structured Terraform directories using workspaces and environment-specific variable files.
* **Result**: Environment deployments were separated, preventing production conflicts.
* **Reflection**: Explicit directory separation is safer than relying on manual configuration flags.

### Q28: How do FastAPI BackgroundTasks prevent HTTP request timeouts?
* **Situation**: Processing long multi-agent workflows inline caused client requests to time out.
* **Task**: Return response receipts instantly while tasks run in the background.
* **Action**: Offloaded the agent loop to FastAPI `BackgroundTasks`, returning the Task ID immediately.
* **Result**: Clients received instant task receipts, eliminating HTTP timeouts.
* **Reflection**: Long-running processes must be decoupled from client request threads.

### Q29: How did you configure PostgreSQL connection pooling for serverless scaling?
* **Situation**: Cloud Run containers scaling up rapidly exhausted PostgreSQL connection limits.
* **Task**: Manage database connections efficiently under variable loads.
* **Action**: Configured SQLAlchemy connection pooling parameters (`pool_size=5`, `max_overflow=10`).
* **Result**: Scaled container instances connected cleanly without overloading the database.
* **Reflection**: Serverless architectures require tight connection limit management.

### Q30: How do you purge expired cache keys from Redis automatically?
* **Situation**: Old, completed task plans filled up Redis memory over time.
* **Task**: Purge expired states automatically.
* **Action**: Applied Time-To-Live (TTL) expiries of 3600 seconds (1 hour) to all task keys in Redis.
* **Result**: Memory usage remained constant, eliminating manual purges.
* **Reflection**: Always configure TTL limits on temporary cache data.

---

## Category 4: GCP Production Observability (Cloud Logging/Trace), FinOps & Latency Optimization (Sub-10s)

### Q31: How do you trace latency step-by-step across all agent nodes?
* **Situation**: Users reported slow processing times, but we could not pinpoint which agent was bottlenecking.
* **Task**: Measure latency for every step in the pipeline.
* **Action**: Wrapped each agent execution in a timer, logging duration results to the `traces` table in PostgreSQL.
* **Result**: The UI displayed latency breakdowns, highlighting slow nodes immediately.
* **Reflection**: Granular performance tracking is necessary to maintain speed.

### Q32: How did you implement structured JSON logging for GCP Cloud Logging?
* **Situation**: Plain text logs made searching and parsing errors difficult in Cloud Logging.
* **Task**: Implement structured logging for easy filtering.
* **Action**: Configured Python's logging module to output JSON-formatted logs containing correlation IDs.
* **Result**: Operations teams filtered errors and trace logs by specific task IDs instantly.
* **Reflection**: Structured logging is a prerequisite for production monitoring.

### Q33: How does context pruning reduce API billing costs?
* **Situation**: Passing full, redundant search documents to Vertex AI inflated API costs.
* **Task**: Reduce input tokens while preserving relevant information.
* **Action**: Implemented a pre-processor that strips HTML tags, headers, and duplicates, keeping only the raw relevant text.
* **Result**: Average input token size dropped by 40%, reducing monthly API spend.
* **Reflection**: Clean data inputs directly lower LLM operating costs.

### Q34: What configuration tuning achieved sub-10s execution for the entire workflow?
* **Situation**: The workflow took over 18 seconds to complete due to slow models and database lookups.
* **Task**: Reduce end-to-end execution times to under 10 seconds.
* **Action**: Swapped the primary model to Gemini 2.0 Flash, ran database updates asynchronously, and cached search queries.
* **Result**: Average execution times fell to 6.2 seconds.
* **Reflection**: Combine fast models with asynchronous code to achieve low latencies.

### Q35: How do you monitor API token quotas to prevent service denial?
* **Situation**: Large bulk uploads triggered rate-limiting errors from Vertex AI, blocking active workflows.
* **Task**: Monitor token consumption and rate limits in real time.
* **Action**: Extracted token count headers from Gemini API responses and logged them to Cloud SQL.
* **Result**: Configured alerts to warn administrators before quota limits are reached.
* **Reflection**: Quota monitoring prevents service interruptions under heavy load.

### Q36: How does Redis caching optimize costs for duplicate search queries?
* **Situation**: Multiple identical briefs queried identical historical guidelines, triggering redundant LLM calls.
* **Task**: Cache repeated query results.
* **Action**: Implemented a caching layer that saves completed agent outputs for identical input hashes in Redis.
* **Result**: Cached requests returned results instantly without querying LLM APIs, reducing costs.
* **Reflection**: Caching common inputs preserves system budgets.

### Q37: How do you track performance degradation over time?
* **Situation**: Latency slowly crept up after updates, but there was no historical baseline to compare against.
* **Task**: Measure and analyze historical performance trends.
* **Action**: Created daily dashboards using PostgreSQL trace data to map latency averages.
* **Result**: Pinpointed performance drops caused by model updates immediately.
* **Reflection**: Continuous baseline measurement is key to maintaining system speed.

### Q38: How did you configure Cloud Run concurrency limits for optimal memory usage?
* **Situation**: High concurrent traffic crashed container instances due to out-of-memory errors.
* **Task**: Balance container memory and concurrency configurations.
* **Action**: Configured concurrency limits to 80 requests per container and allocated 2GB of RAM.
* **Result**: Container instances handled concurrent requests stably without crashes.
* **Reflection**: Test concurrency limits under load to find the stable operational configuration.

### Q39: How do you calculate the financial cost of a single task execution?
* **Situation**: Managers needed to know the cost-per-brief to calculate ROI.
* **Task**: Calculate the exact financial cost of each task run.
* **Action**: Logged input and output token counts for each LLM call and multiplied them by Vertex AI pricing rates.
* **Result**: The dashboard displayed exact cents-per-run costs for each task.
* **Reflection**: Tracking token usage provides direct financial visibility.

### Q40: How does connection reuse via httpx.AsyncClient minimize latency?
* **Situation**: Recreating HTTP connections for every agent call added overhead latency.
* **Task**: Reduce HTTP connection overhead.
* **Action**: Configured a single, shared `httpx.AsyncClient` instance reuse across the application lifespans.
* **Result**: Network connection overhead fell, saving 300ms per agent call.
* **Reflection**: Connection pooling and reuse is a standard practice for high-performance networks.

---

## Category 5: AppSec, Guardrails (Pydantic/Vertex Safety), Human-in-the-Loop (HITL), & CI/CD Strategy

### Q41: How does strict Pydantic parsing prevent JSON structural failures?
* **Situation**: The model returned JSON with missing fields, causing backend parsing failures.
* **Task**: Guarantee output structural formatting.
* **Action**: Defined schemas using Pydantic, enforcing validation checks during extraction.
* **Result**: Badly formatted payloads were caught and corrected before causing database errors.
* **Reflection**: Always validate unstructured LLM outputs against strict schemas.

### Q42: How is the state suspended and resumed for Human-in-the-Loop review?
* **Situation**: When content breached policy guidelines, the pipeline needed to pause for review and resume later.
* **Task**: Pause and resume running pipelines without losing state.
* **Action**: Set task status to `pending_review` and saved the state snapshot. When the user approved or modified, the backend loaded the snapshot and resumed the run.
* **Result**: Editors approved or modified plans dynamically, resuming the pipeline.
* **Reflection**: Decouple state management from execution threads to support human intervention.

### Q43: How does the Judge Agent check policy compliance automatically?
* **Situation**: Raw briefs occasionally contained legal or policy risks that slipped past basic keyword checks.
* **Task**: Evaluate policy compliance before publication.
* **Action**: Implemented the Judge Agent, instructing it to evaluate packs against compliance standards and flag risks.
* **Result**: High-risk drafts were automatically flagged and routed to the review queue.
* **Reflection**: Automated evaluation acts as a reliable first line of defense.

### Q44: How are prompt injections blocked at the API Gateway?
* **Situation**: Users tried to override system instructions by pasting commands like "ignore previous instructions".
* **Task**: Detect and block prompt injection attempts.
* **Action**: Implemented sanitization filters at the API Gateway to block common injection keyphrases.
* **Result**: Malicious injection inputs were blocked before reaching LLM models.
* **Reflection**: Always sanitize user inputs before processing them through LLMs.

### Q45: How does the CI/CD pipeline run automated safety checks?
* **Situation**: Developer updates risked introducing insecure packages or failing code.
* **Task**: Automate security and syntax testing.
* **Action**: Configured GitHub Actions to run dependency scanning (`pip-audit`) and unit tests on every pull request.
* **Result**: Vulnerable updates were caught before reaching production branches.
* **Reflection**: Automate security checks to protect production pipelines.

### Q46: How do you rollback deployments quickly if production experiences issues?
* **Situation**: An updated container version caused execution failures in production.
* **Task**: Roll back to the previous version instantly.
* **Action**: Configured Cloud Run to route traffic back to the previous revision tag.
* **Result**: Rolled back the update in under 2 seconds, minimizing downtime.
* **Reflection**: Immutable revision tags enable instant rollbacks.

### Q47: How are human-modified editorial packs re-evaluated?
* **Situation**: Editors modified packs, but changes needed to be re-logged for audit tracking.
* **Task**: Log modifications and verify the updated pack.
* **Action**: Configured the review endpoint to save modified packs and log the editor's notes as a new trace step.
* **Result**: Maintained a complete history of all changes made by editors.
* **Reflection**: Audit logs must track both automated agent steps and human edits.

### Q48: How are Vertex AI safety settings configured in production?
* **Situation**: The model occasionally blocked safe media drafts containing sensitive topic keywords (e.g., crime reporting).
* **Task**: Configure safety thresholds to balance compliance and operational utility.
* **Action**: Customized the harm block thresholds (`BLOCK_MEDIUM_AND_ABOVE`) in the Vertex AI SDK configuration.
* **Result**: Legitimate news drafts processed successfully while toxic outputs remained blocked.
* **Reflection**: Fine-tune safety configurations to match your business context.

### Q49: How are database credentials rotated securely without downtime?
* **Situation**: Security policies required rotating database passwords every 90 days.
* **Task**: Rotate passwords without interrupting running services.
* **Action**: Used GCP Secret Manager to create new password versions and triggered gradual Cloud Run container updates.
* **Result**: Rotated credentials smoothly with zero service downtime.
* **Reflection**: Decoupling secrets from container configurations simplifies compliance tasks.

### Q50: How do you verify A2A communication contracts in the CI/CD pipeline?
* **Situation**: Updates to the Metadata Agent's output structure broke downstream Writer integrations.
* **Task**: Verify data exchange contracts during testing.
* **Action**: Implemented contract testing using mock schemas to verify compatibility before merging code.
* **Result**: Prevented broken schemas from reaching deployment environments.
* **Reflection**: Contract testing is essential for maintaining independent microservice teams.
