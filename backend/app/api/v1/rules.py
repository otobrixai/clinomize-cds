"""
Rules API endpoint - returns current versioned rules.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.rules.loader import load_rules, get_latest_rules_version
from app.rules.engine import RulesEngine
from app.api.v1.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("")
async def get_rules(
    version: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current versioned rules.
    
    Args:
        version: Optional specific version (e.g., "1.0.0"). If not provided, returns latest.
    
    Returns:
        Rules data with version information
    """
    try:
        if version:
            rules_version = version
        else:
            rules_version = get_latest_rules_version()
        
        rules_data = load_rules(rules_version)
        
        # Return rules with metadata (without exposing internal structure)
        return {
            "version": rules_data.get("version"),
            "source": rules_data.get("source"),
            "updated_date": rules_data.get("updated_date"),
            "rule_count": len(rules_data.get("rules", [])),
            "rules": rules_data.get("rules"),  # Full rules if needed
            "note": "Rules are version-controlled. Contact admin for rule updates."
        }
    except FileNotFoundError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Rules version not found: {version}")
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error loading rules: {str(e)}")

@router.get("/versions")
async def list_rule_versions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all available rule versions."""
    from pathlib import Path
    import app.rules.loader as loader_module
    
    rules_dir = Path(loader_module.__file__).parent
    rule_files = list(rules_dir.glob("rules_v*.json"))
    
    versions = []
    for f in rule_files:
        version_str = f.stem.replace("rules_v", "")
        versions.append(version_str)
    
    versions.sort(reverse=True)
    
    return {
        "available_versions": versions,
        "latest": versions[0] if versions else None
    }
