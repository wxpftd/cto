from app.workers.celery_app import celery_app
from app.database import SessionLocal
from app.models import Feedback, Project, Task, Adjustment, FeedbackStatus
from app.services.llm_service import llm_service
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.workers.tasks.process_feedback")
def process_feedback(self, feedback_id: int):
    db = SessionLocal()
    try:
        feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            logger.error(f"Feedback {feedback_id} not found")
            return {"error": "Feedback not found"}
        
        feedback.status = FeedbackStatus.PROCESSING
        db.commit()
        
        project = db.query(Project).filter(Project.id == feedback.project_id).first()
        if not project:
            feedback.status = FeedbackStatus.FAILED
            db.commit()
            logger.error(f"Project {feedback.project_id} not found")
            return {"error": "Project not found"}
        
        tasks = db.query(Task).filter(Task.project_id == project.id).all()
        
        project_context = {
            "name": project.name,
            "description": project.description or "",
            "status": project.status.value
        }
        
        tasks_context = [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description or "",
                "status": task.status.value,
                "priority": task.priority,
                "estimated_hours": task.estimated_hours
            }
            for task in tasks
        ]
        
        logger.info(f"Analyzing feedback {feedback_id} with LLM")
        result = llm_service.analyze_feedback_and_replan(
            feedback_text=feedback.feedback_text,
            project_context=project_context,
            tasks_context=tasks_context
        )
        
        adjustments = result.get("adjustments", [])
        for adj in adjustments:
            adjustment = Adjustment(
                feedback_id=feedback.id,
                adjustment_type=adj.get("adjustment_type", "general"),
                description=adj.get("description", ""),
                original_value=adj.get("original_value"),
                new_value=adj.get("new_value"),
                reasoning=adj.get("reasoning")
            )
            db.add(adjustment)
        
        feedback.status = FeedbackStatus.COMPLETED
        feedback.processed_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Successfully processed feedback {feedback_id}")
        return {
            "feedback_id": feedback_id,
            "status": "completed",
            "adjustments_count": len(adjustments),
            "summary": result.get("summary", "")
        }
        
    except Exception as e:
        logger.error(f"Error processing feedback {feedback_id}: {str(e)}")
        if feedback:
            feedback.status = FeedbackStatus.FAILED
            db.commit()
        return {"error": str(e)}
    finally:
        db.close()
