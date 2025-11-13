"""
Planner Agent
Builds revision schedules and study plans using Groq API
"""
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.groq_client import GroqClient
from utils.memory import KnowledgeMemory
from typing import Dict, List, Optional


class PlannerAgent:
    def __init__(self, groq_client: GroqClient, memory: KnowledgeMemory):
        """Initialize Planner Agent"""
        self.groq = groq_client
        self.memory = memory
    
    def create_revision_plan(self, document_id: int, days_until_exam: int = 7,
                           hours_per_day: float = 2.0, focus_topics: Optional[List[str]] = None) -> Dict:
        """
        Create a revision plan for a document
        
        Args:
            document_id: ID of the document
            days_until_exam: Number of days until exam
            hours_per_day: Hours available per day
            focus_topics: Optional list of topics to focus on
            
        Returns:
            Revision plan dictionary
        """
        # Get document and related data
        document = self.memory.get_document(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        # Get topics from document metadata or flashcards
        flashcards = self.memory.get_flashcards(document_id)
        topics = self._extract_topics(document, flashcards, focus_topics)
        
        # Get performance stats
        performance = self.memory.get_performance_stats(document_id)
        
        # Generate plan using Groq
        plan = self._generate_plan_with_groq(
            document, topics, days_until_exam, hours_per_day, performance
        )
        
        # Store plan in memory
        plan_id = self.memory.add_revision_plan(document_id, plan)
        plan["plan_id"] = plan_id
        
        return plan
    
    def _extract_topics(self, document: Dict, flashcards: List[Dict], 
                       focus_topics: Optional[List[str]]) -> List[str]:
        """Extract topics from document"""
        if focus_topics:
            return focus_topics
        
        # Get topics from metadata
        metadata = document.get("metadata", {})
        if isinstance(metadata, dict):
            topics = metadata.get("topics", [])
            if topics:
                return topics
        
        # Get topics from flashcards
        flashcard_topics = [fc["topic"] for fc in flashcards if fc.get("topic")]
        unique_topics = list(set(flashcard_topics))
        
        return unique_topics[:5] if unique_topics else ["General Content"]
    
    def _generate_plan_with_groq(self, document: Dict, topics: List[str],
                                days: int, hours_per_day: float, performance: Dict) -> Dict:
        """Generate revision plan using Groq"""
        system_prompt = """You are an expert study planner. Create effective revision schedules that:
- Distribute content evenly across available days
- Include review sessions for previously studied material
- Adapt to user's performance (focus more on weak areas)
- Include practice sessions (quizzes, flashcards)
- Build in rest days before the exam
- Are realistic and achievable"""
        
        content_summary = document["content"][:3000]
        topics_str = ", ".join(topics)
        accuracy = performance.get("accuracy", 0)
        
        prompt = f"""Create a {days}-day revision plan for an exam with the following details:

Content Summary:
{content_summary}

Topics to Cover: {topics_str}
Days until exam: {days}
Hours available per day: {hours_per_day}
Current quiz accuracy: {accuracy}%

Create a detailed day-by-day plan. Each day should include:
- Topics/chapters to study
- Time allocation
- Activities (reading, flashcards, quizzes)
- Review of previous days' material

Return the plan in this JSON format:
{{
    "plan_name": "Revision Plan Name",
    "total_days": {days},
    "hours_per_day": {hours_per_day},
    "schedule": [
        {{
            "day": 1,
            "date": "YYYY-MM-DD",
            "topics": ["Topic 1", "Topic 2"],
            "activities": [
                {{
                    "type": "reading",
                    "description": "Read Chapter 1",
                    "duration_minutes": 60
                }},
                {{
                    "type": "flashcards",
                    "description": "Review flashcards on Topic 1",
                    "duration_minutes": 30
                }}
            ],
            "notes": "Day 1 notes"
        }}
    ],
    "tips": ["Tip 1", "Tip 2", "Tip 3"]
}}"""
        
        try:
            response = self.groq.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.6
            )
            
            # Add dates to schedule
            plan = response
            start_date = datetime.now()
            for day_plan in plan.get("schedule", []):
                day_num = day_plan.get("day", 1)
                plan_date = start_date + timedelta(days=day_num - 1)
                day_plan["date"] = plan_date.strftime("%Y-%m-%d")
            
            return plan
        except Exception as e:
            # Fallback: create simple plan
            return self._create_simple_plan(topics, days, hours_per_day)
    
    def _create_simple_plan(self, topics: List[str], days: int, 
                           hours_per_day: float) -> Dict:
        """Create a simple revision plan as fallback"""
        schedule = []
        topics_per_day = max(1, len(topics) // days)
        start_date = datetime.now()
        
        for day in range(1, days + 1):
            day_topics = topics[(day-1)*topics_per_day:day*topics_per_day + topics_per_day]
            if not day_topics and topics:
                day_topics = [topics[-1]]
            
            plan_date = start_date + timedelta(days=day - 1)
            
            schedule.append({
                "day": day,
                "date": plan_date.strftime("%Y-%m-%d"),
                "topics": day_topics,
                "activities": [
                    {
                        "type": "reading",
                        "description": f"Study {', '.join(day_topics)}",
                        "duration_minutes": int(hours_per_day * 30)
                    },
                    {
                        "type": "practice",
                        "description": "Practice with flashcards and quizzes",
                        "duration_minutes": int(hours_per_day * 30)
                    }
                ],
                "notes": f"Day {day}: Focus on {', '.join(day_topics)}"
            })
        
        return {
            "plan_name": f"{days}-Day Revision Plan",
            "total_days": days,
            "hours_per_day": hours_per_day,
            "schedule": schedule,
            "tips": [
                "Review previous days' material regularly",
                "Take breaks between study sessions",
                "Test yourself with quizzes and flashcards",
                "Get adequate sleep before the exam"
            ]
        }
    
    def get_revision_plans(self, document_id: Optional[int] = None) -> List[Dict]:
        """Retrieve revision plans from memory"""
        return self.memory.get_revision_plans(document_id)

