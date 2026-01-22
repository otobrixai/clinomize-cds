"""
Sandboxed AI explanation service.
AI is ONLY used for explanation, documentation, and evidence context.
AI NEVER recommends, changes thresholds, or overrides rules.
"""
from typing import Dict, Any, Optional
from app.core.config import settings

class AIExplanationService:
    """
    Sandboxed AI service for generating explanations.
    Rules are authoritative - AI only explains why rules triggered.
    """
    
    def __init__(self):
        self.enabled = settings.AI_ENABLED and bool(settings.OPENAI_API_KEY)
    
    def explain_rule_trigger(
        self,
        rule_id: str,
        recommendation: Dict[str, Any],
        encounter_data: Dict[str, Any]
    ) -> str:
        """
        Generate explanation for why a rule triggered.
        This is documentation only - never changes the recommendation.
        
        Args:
            rule_id: ID of the rule that triggered
            recommendation: The recommendation from rules engine
            encounter_data: Patient encounter data
        
        Returns:
            Explanation text
        """
        if not self.enabled:
            return self._fallback_explanation(rule_id, recommendation)
        
        # In production, this would call OpenAI API with strict constraints
        # For now, return structured explanation
        return self._generate_explanation(rule_id, recommendation, encounter_data)
    
    def _generate_explanation(
        self,
        rule_id: str,
        recommendation: Dict[str, Any],
        encounter_data: Dict[str, Any]
    ) -> str:
        """Generate explanation text."""
        component = recommendation.get("component", "No transfusion")
        why_points = recommendation.get("why", [])
        
        explanation = f"Rule {rule_id} triggered because:\n\n"
        for point in why_points:
            explanation += f"• {point}\n"
        
        explanation += f"\nComponent: {component}\n"
        explanation += f"Dose: {recommendation.get('dose_text', 'N/A')}\n"
        
        return explanation
    
    def _fallback_explanation(
        self,
        rule_id: str,
        recommendation: Dict[str, Any]
    ) -> str:
        """Fallback explanation when AI is disabled."""
        why_points = recommendation.get("why", [])
        explanation = f"Rule {rule_id} applied:\n\n"
        for point in why_points:
            explanation += f"• {point}\n"
        return explanation
    
    def highlight_borderline_case(
        self,
        recommendation: Dict[str, Any],
        encounter_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Highlight if this is a borderline case that might need extra consideration.
        This is informational only - does not change recommendation.
        """
        # Check for borderline values
        hb = encounter_data.get("hb_gdl")
        platelets = encounter_data.get("platelets_x109l")
        inr = encounter_data.get("inr")
        
        borderline_notes = []
        
        if hb is not None:
            if 7.0 <= hb <= 7.5:
                borderline_notes.append("Hb is near threshold (7.0 g/dL) - consider clinical context")
            if 8.0 <= hb <= 8.5:
                borderline_notes.append("Hb is near ICU/OR threshold (8.0 g/dL)")
        
        if platelets is not None:
            if 10 <= platelets <= 15:
                borderline_notes.append("Platelets near prophylactic threshold (10 ×10⁹/L)")
            if 45 <= platelets <= 55:
                borderline_notes.append("Platelets near bleeding threshold (50 ×10⁹/L)")
        
        if inr is not None:
            if 1.4 <= inr <= 1.6:
                borderline_notes.append("INR near threshold (1.5) - consider clinical context")
        
        if borderline_notes:
            return "\n".join(borderline_notes)
        
        return None
    
    def generate_evidence_summary(
        self,
        guideline_id: str,
        topic: Optional[str] = None
    ) -> str:
        """
        Generate AI summary of evidence/guidelines.
        ADMIN ONLY - Never exposed to clinical users.
        
        This method would call OpenAI API in production to summarize
        clinical guidelines. For now, returns placeholder.
        """
        if not self.enabled:
            return f"AI is not enabled. Cannot generate evidence summary for guideline: {guideline_id}"
        
        # In production, this would make an OpenAI API call with strict prompts:
        # "Summarize the key points from [guideline_id] regarding [topic].
        #  Focus on transfusion thresholds and contraindications.
        #  Do not provide recommendations, only summarize evidence."
        
        # Placeholder for now
        summary = f"Evidence Summary for {guideline_id}:\n\n"
        if topic:
            summary += f"Topic: {topic}\n\n"
        summary += """This is a placeholder. In production, this would contain an AI-generated
summary of clinical guidelines for administrative review.

Note: AI-generated content is for administrative use only and never
influences clinical recommendations, which are determined solely by
the rules engine."""
        
        return summary.strip()