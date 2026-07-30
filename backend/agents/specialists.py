import json
import logging
from backend.agents.base_agent import BaseAgent
from backend.memory.chromadb_client import ChromaDBClient

logger = logging.getLogger("Specialists")

class RetrievalAgent(BaseAgent):
    def __init__(self):
        system_instructions = (
            "You are a Media Research Specialist at the Australian Media Channel.\n"
            "Your task is to take a query and match it with relevant historical archives, articles, or editorial guidelines.\n"
            "Present a summary of findings clearly and cite sources."
        )
        super().__init__("RetrievalSpecialist", system_instructions)
        self.chroma_client = ChromaDBClient()

    async def retrieve_context(self, task_description: str, content: str) -> tuple[str, str]:
        # Formulate query text based on task and content
        search_query = f"{task_description} {content[:100]}"
        logger.info(f"Retrieval Specialist querying ChromaDB for: '{search_query[:50]}...'")
        
        # Query ChromaDB
        docs = self.chroma_client.query_documents(search_query, n_results=2)
        
        if not docs:
            return "No historical records or guidelines found in ChromaDB matching this query.", "ChromaDB Vector Store"
            
        context_parts = []
        for doc in docs:
            title = doc["metadata"].get("title", "Untitled Document")
            src = doc["metadata"].get("source", "Unknown Source")
            content_text = doc["document"]
            context_parts.append(f"Document: {title} | Source: {src}\nContent: {content_text}\n---")
            
        return "\n\n".join(context_parts), "ChromaDB Vector Store"



class MetadataAgent(BaseAgent):
    def __init__(self):
        system_instructions = (
            "You are a Metadata and Compliance Extraction Agent for the Australian Media Channel.\n"
            "Your task is to analyze raw content and retrieved context to identify:\n"
            "1. Major key themes\n"
            "2. Entity and classification tags\n"
            "3. Legal and editorial risk flags (e.g. defamation risk, privacy breach, sub judice contempt, copyright infringements).\n"
            "Return JSON only in the following format:\n"
            "{\n"
            '  "key_themes": ["theme1", "theme2"],\n'
            '  "metadata_tags": ["tag1", "tag2"],\n'
            '  "editorial_risk_flags": ["risk1", "risk2"]\n'
            "}"
        )
        super().__init__("MetadataSpecialist", system_instructions)

    async def extract_metadata(self, content: str, context: str) -> tuple[dict, str]:
        prompt = (
            f"Analyze the incoming content and context to extract metadata and risk flags:\n"
            f"Content:\n{content}\n\n"
            f"Retrieved Historical Context / Guidelines:\n{context}\n\n"
            f"Return JSON."
        )
        res_dict = await self.chat(prompt, schema="Metadata")
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
            logger.error(f"Failed to parse Metadata JSON: {e}. Raw response: {response}")
            return {
                "key_themes": ["General News"],
                "metadata_tags": ["Uncategorized"],
                "editorial_risk_flags": ["Unverified Content Risks"]
            }, engine



class WriterAgent(BaseAgent):
    def __init__(self):
        system_instructions = (
            "You are a Senior Editorial Writer and Synthesis Agent at the Australian Media Channel.\n"
            "Your task is to construct the final Editorial Intelligence Pack. Integrate the original text, "
            "the extracted themes, tags, risk flags, and retrieved historical context.\n"
            "Output a structured JSON object exactly matching the schema:\n"
            "{\n"
            '  "executive_summary": "detailed summary of the story, significance, and context",\n'
            '  "key_themes": ["list of main themes"],\n'
            '  "metadata_tags": ["list of tags"],\n'
            '  "editorial_risk_flags": ["list of risks or compliance warnings"],\n'
            '  "suggested_headlines": ["Headline 1", "Headline 2", "Headline 3"]\n'
            "}"
        )
        super().__init__("WriterSpecialist", system_instructions)

    async def generate_pack(self, content: str, context: str, metadata: dict) -> tuple[dict, str]:
        prompt = (
            f"Draft the Editorial Intelligence Pack.\n"
            f"Original Content:\n{content}\n\n"
            f"Retrieved Context:\n{context}\n\n"
            f"Extracted Themes and Risks:\n{json.dumps(metadata)}\n\n"
            f"Please output a valid JSON matching the requested structure."
        )
        res_dict = await self.chat(prompt, schema="EditorialIntelligencePack")
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
            logger.error(f"Failed to parse Writer JSON: {e}. Raw response: {response}")
            return {
                "executive_summary": f"Failsafe Summary: {content[:200]}...",
                "key_themes": metadata.get("key_themes", []),
                "metadata_tags": metadata.get("metadata_tags", []),
                "editorial_risk_flags": metadata.get("editorial_risk_flags", []),
                "suggested_headlines": ["Media Report Update", "Review Needed"]
            }, engine

