from openai import OpenAI
from typing import Dict, List, Any
import json
from app.config import settings


class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.temperature = settings.LLM_TEMPERATURE
    
    def analyze_feedback_and_replan(
        self,
        feedback_text: str,
        project_context: Dict[str, Any],
        tasks_context: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        prompt = self._build_replan_prompt(feedback_text, project_context, tasks_context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an intelligent project planning assistant. Analyze user feedback and suggest specific adjustments to project tasks, priorities, and plans. Return your response as a valid JSON object."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            raise Exception(f"LLM service error: {str(e)}")
    
    def _build_replan_prompt(
        self,
        feedback_text: str,
        project_context: Dict[str, Any],
        tasks_context: List[Dict[str, Any]]
    ) -> str:
        tasks_str = "\n".join([
            f"- Task #{t['id']}: {t['title']} (Status: {t['status']}, Priority: {t['priority']})"
            for t in tasks_context
        ])
        
        prompt = f"""
Project Context:
- Name: {project_context['name']}
- Description: {project_context['description']}
- Status: {project_context['status']}

Current Tasks:
{tasks_str if tasks_str else "No tasks yet"}

User Feedback:
{feedback_text}

Based on this feedback, analyze and suggest specific adjustments. Return a JSON object with:
{{
    "summary": "Brief summary of analysis",
    "adjustments": [
        {{
            "adjustment_type": "task_priority|task_description|new_task|task_status|remove_task",
            "description": "What adjustment to make",
            "original_value": "Current value (if applicable)",
            "new_value": "Suggested new value",
            "reasoning": "Why this adjustment makes sense",
            "task_id": "ID of affected task (if applicable)"
        }}
    ]
}}

Provide actionable, specific suggestions that directly address the user's feedback.
"""
        return prompt


llm_service = LLMService()
