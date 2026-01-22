import json
import os
from pathlib import Path
from typing import Dict, Any

def load_rules(version: str = "1.0.0") -> Dict[str, Any]:
    """
    Load rules from JSON file.
    
    Args:
        version: Semantic version of rules to load (e.g., "1.0.0")
    
    Returns:
        Dictionary containing rules data
    """
    rules_dir = Path(__file__).parent
    rules_file = rules_dir / f"rules_v{version}.json"
    
    if not rules_file.exists():
        raise FileNotFoundError(f"Rules file not found: {rules_file}")
    
    with open(rules_file, "r", encoding="utf-8") as f:
        rules_data = json.load(f)
    
    return rules_data

def get_latest_rules_version() -> str:
    """Get the latest rules version available."""
    rules_dir = Path(__file__).parent
    rule_files = list(rules_dir.glob("rules_v*.json"))
    
    if not rule_files:
        raise FileNotFoundError("No rules files found")
    
    # Extract versions and return latest
    versions = []
    for f in rule_files:
        version_str = f.stem.replace("rules_v", "")
        versions.append(version_str)
    
    # Simple version comparison (for semantic versioning, use proper version comparison)
    versions.sort(reverse=True)
    return versions[0]
