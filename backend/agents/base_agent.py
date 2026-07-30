import os
import json
import logging
import asyncio
from typing import Optional, AsyncGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BaseAgent")

# Try importing Antigravity SDK
try:
    from google.antigravity import Agent as AGYAgent
    from google.antigravity import LocalAgentConfig, CapabilitiesConfig
    HAS_AGY_SDK = True
except ImportError:
    HAS_AGY_SDK = False
    logger.warning("google-antigravity SDK not found. Will use Vertex AI/OpenAI direct API fallback.")

# Try importing Gemini & Vertex AI
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

# Try importing OpenAI
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

class BaseAgent:
    def __init__(self, name: str, system_instructions: str):
        self.name = name
        self.system_instructions = system_instructions
        
    async def chat(self, prompt: str, schema = None) -> dict:
        """Sends prompt to the agent. Returns a dict with 'content' and 'engine' metadata."""
        logger.info(f"Agent [{self.name}] processing request.")
        
        # 1. Try Antigravity SDK Agent
        if HAS_AGY_SDK:
            try:
                config = LocalAgentConfig(
                    system_instructions=self.system_instructions,
                    capabilities=CapabilitiesConfig()
                )
                async with AGYAgent(config) as agent:
                    response = await agent.chat(prompt)
                    full_text = ""
                    async for token in response:
                        full_text += token
                    return {"content": full_text, "engine": "Google ADK (Antigravity SDK)"}
            except Exception as e:
                logger.error(f"Antigravity SDK execution failed: {e}. Falling back to Direct API.")
        
        # 2. Try OpenAI Direct Fallback (if API key present)
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key != "mock-key-for-local-runs" and HAS_HTTPX:
            try:
                async with httpx.AsyncClient() as client:
                    headers = {
                        "Authorization": f"Bearer {openai_key}",
                        "Content-Type": "application/json"
                    }
                    data = {
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": self.system_instructions},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.2
                    }
                    if schema:
                        data["response_format"] = {"type": "json_object"}
                        
                    res = await client.post("https://api.openai.com/v1/chat/completypes", headers=headers, json=data, timeout=30.0)
                    if res.status_code == 200:
                        return {
                            "content": res.json()["choices"][0]["message"]["content"],
                            "engine": "OpenAI API (Fallback)"
                        }
                    else:
                        logger.error(f"OpenAI fallback returned status: {res.status_code} - {res.text}")
            except Exception as ex:
                logger.error(f"OpenAI API fallback failed: {ex}")

        # 3. Try Vertex AI / Gemini Direct Fallback
        gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if HAS_GEMINI and gemini_api_key:
            try:
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=self.system_instructions
                )
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: model.generate_content(prompt)
                )
                return {"content": response.text, "engine": "Vertex AI (Gemini Fallback)"}
            except Exception as ex:
                logger.error(f"Gemini API fallback failed: {ex}")

        # 4. Final local rule-based fallback to guarantee execution in offline/CI environments
        logger.warning(f"All LLM APIs failed or unconfigured. Performing local heuristic completion for {self.name}.")
        return {
            "content": self._heuristic_fallback(prompt, schema),
            "engine": "Local Heuristic Engine (Failsafe)"
        }


    def _heuristic_fallback(self, prompt: str, schema=None) -> str:
        """Returns valid JSON mock content when external APIs are not connected."""
        if schema:
            if "executive_summary" in prompt or "EditorialIntelligencePack" in prompt:
                return json.dumps({
                    "executive_summary": f"This is an automated editorial summary of: '{prompt[:100]}...'. Analyzed under offline safety heuristics.",
                    "key_themes": ["Editorial Review", "Regulatory Standards", "Broadcast Media"],
                    "metadata_tags": ["Australia", "Nine Network", "Compliance"],
                    "editorial_risk_flags": ["Defamation Precautionary Check Recommended"],
                    "suggested_headlines": ["Broadcasting Standards Under Inspection", "Media Compliance Review 2026"]
                })
            elif "factuality_score" in prompt or "JudgeEvaluation" in prompt:
                # If content mentions risk or defamation, set compliance to False to demonstrate HITL flow!
                requires_hitl = "risk" in prompt.lower() or "defamation" in prompt.lower() or "trial" in prompt.lower() or "contempt" in prompt.lower()
                return json.dumps({
                    "factuality_score": 7 if requires_hitl else 9,
                    "policy_compliance": not requires_hitl,
                    "feedback": "Offline Heuristic Review: Compliance review triggered due to high-risk keywords." if requires_hitl else "Passed heuristic compliance checks.",
                    "requires_human_review": requires_hitl
                })
            elif "subtasks" in prompt:
                return json.dumps({
                    "subtasks": [
                        {"id": 1, "task": "Retrieve guidelines", "specialist": "retrieval"},
                        {"id": 2, "task": "Extract metadata", "specialist": "metadata"},
                        {"id": 3, "task": "Synthesize pack", "specialist": "writer"}
                    ]
                })
        return f"Mock response from {self.name} for prompt: {prompt[:50]}..."
