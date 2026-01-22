from typing import Dict, Any
from app.cardioiq.schemas import CardioIQInput, CardioIQOutput
from app.cardioiq.engine import CardioIQEngine

# Singleton instance
_engine = None

def get_engine() -> CardioIQEngine:
    global _engine
    if _engine is None:
        _engine = CardioIQEngine()
    return _engine

class CardioIQService:
    @staticmethod
    def evaluate_patient(data: CardioIQInput) -> CardioIQOutput:
        """
        Main entry point for CDS evaluation.
        """
        engine = get_engine()
        result = engine.evaluate(data)
        
        # TODO: Add Audit Logging here (save to DB)
        
        return result
