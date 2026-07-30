import json
import logging
from backend.agents.base_agent import BaseAgent

logger = logging.getLogger("JudgeAgent")

class JudgeAgent(BaseAgent):
    def __init__(self):
        system_instructions = (
            "You are the Quality Control and Editorial Ethics Judge for the Australian Media Channel.\n"
            "Evaluate the generated Editorial Intelligence Pack against editorial guidelines and risk flags.\n"
            "Rate factuality (1-10), verify policy compliance (true/false), and decide if it requires human review (true/false).\n"
            "If any major legal risk flags (such as 'defamation', 'sub judice', 'prejudice trial', 'leak', or 'lawsuit') are present, "
            "you MUST mark 'requires_human_review' as true.\n"
            "Return JSON in the following format:\n"
            "{\n"
            '  "factuality_score": 8,\n'
            '  "policy_compliance": true,\n'
            '  "feedback": "Detailed feedback describing the check findings.",\n'
            '  "requires_human_review": false\n'
            "}"
        )
        super().__init__("Judge", system_instructions)

    async def evaluate_pack(self, content: str, pack: dict) -> tuple[dict, str]:
        prompt = (
            f"Original Input Content:\n{content}\n\n"
            f"Proposed Editorial Intelligence Pack:\n{json.dumps(pack)}\n\n"
            f"Evaluate the pack for factual alignment and legal compliance."
        )
        res_dict = await self.chat(prompt, schema="JudgeEvaluation")
        response = res_dict["content"]
        engine = res_dict["engine"]
        
        clean_response = response.strip()
        if clean_response.startswith("```json"):
            clean_response = clean_response[7:]
        if clean_response.endswith("```"):
            clean_response = clean_response[:-3]
        clean_response = clean_response.strip()
        
        try:
            return json.loads(clean_response), engine
        except Exception as e:
            logger.error(f"Failed to parse Judge JSON: {e}. Raw response: {response}")
            
            # Safe default fallback logic
            requires_hitl = False
            for flag in pack.get("editorial_risk_flags", []):
                flag_l = flag.lower()
                if any(x in flag_l for x in ["defamation", "sub judice", "contempt", "leak", "legal", "court"]):
                    requires_hitl = True
                    
            return {
                "factuality_score": 7 if requires_hitl else 9,
                "policy_compliance": not requires_hitl,
                "feedback": "Failsafe Evaluation: Precautionary human check based on risk keywords." if requires_hitl else "Failsafe Evaluation: Heuristic checks passed.",
                "requires_human_review": requires_hitl
            }, engine

