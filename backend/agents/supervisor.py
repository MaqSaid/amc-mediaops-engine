import json
import logging
from backend.agents.base_agent import BaseAgent

logger = logging.getLogger("SupervisorAgent")

class SupervisorAgent(BaseAgent):
    def __init__(self):
        system_instructions = (
            "You are the Lead Editorial Supervisor for the Australian Media Channel.\n"
            "Your job is to analyze incoming raw content briefs, transcripts, or notes, "

            "and decompose the workflow into a structured JSON execution plan.\n"
            "Identify the subtasks, the assigned specialists ('retrieval', 'metadata', 'writer'), "
            "and any dependencies.\n"
            "Return JSON only in the following format:\n"
            "{\n"
            '  "subtasks": [\n'
            '    {"id": 1, "task": "detailed task description", "specialist": "retrieval", "dependencies": []},\n'
            '    {"id": 2, "task": "detailed task description", "specialist": "metadata", "dependencies": [1]},\n'
            '    {"id": 3, "task": "detailed task description", "specialist": "writer", "dependencies": [2]}\n'
            "  ]\n"
            "}"
        )
        super().__init__("Supervisor", system_instructions)

    async def create_plan(self, content: str, content_type: str, source: str) -> tuple[dict, str]:
        prompt = (
            f"Analyze the following incoming content:\n"
            f"Content Type: {content_type}\n"
            f"Source: {source}\n"
            f"Content:\n{content}\n\n"
            f"Decompose this into specific actions for the retrieval, metadata, and writer specialists."
        )
        res_dict = await self.chat(prompt, schema="Plan")
        response = res_dict["content"]
        engine = res_dict["engine"]
        
        # Clean response if markdown blocks are returned
        clean_response = response.strip()
        if clean_response.startswith("```json"):
            clean_response = clean_response[7:]
        if clean_response.endswith("```"):
            clean_response = clean_response[:-3]
        clean_response = clean_response.strip()
        
        try:
            plan = json.loads(clean_response)
            return plan, engine
        except Exception as e:
            logger.error(f"Failed to parse Supervisor JSON plan: {e}. Raw response: {response}")
            return {
                "subtasks": [
                    {"id": 1, "task": f"Retrieve relevant historical archives matching content: {content[:50]}", "specialist": "retrieval", "dependencies": []},
                    {"id": 2, "task": "Extract metadata tags, categories, and risks", "specialist": "metadata", "dependencies": [1]},
                    {"id": 3, "task": "Generate the final Editorial Intelligence Pack", "specialist": "writer", "dependencies": [2]}
                ]
            }, engine

