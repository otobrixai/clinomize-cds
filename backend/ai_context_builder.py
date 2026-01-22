#!/usr/bin/env python3
"""
TRANFUSIONIQ - AI CONTEXT BUILDER (FIXED)
Creates minimal, dense JSON with maximum AI understanding.
Focuses on WHAT AI NEEDS, not human readability.
"""

import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Any
import hashlib

class AIContextBuilder:
    def __init__(self, project_root: str):
        self.root = Path(project_root)
        self.context = {
            "metadata": {
                "project": "TransfusionIQ",
                "type": "medical_cds",
                "hash": "",
                "token_estimate": 0
            },
            "architecture": {},      # File structure, imports
            "patterns": {},          # Common code patterns
            "flows": {},             # Data/business flows
            "gaps": {}               # What's missing/needs attention
        }
    
    def build_minimal_context(self) -> Dict:
        """Build ultra-compact AI context (< 10K tokens)"""
        print("🧠 Building AI-optimized context...")
        
        # 1. Architecture fingerprint (not full structure)
        self._fingerprint_architecture()
        
        # 2. Key patterns only (what matters)
        self._extract_critical_patterns()
        
        # 3. Data flows (succinct)
        self._map_key_flows()
        
        # 4. Gaps & risks
        self._identify_gaps()
        
        # 5. Token optimization
        self._optimize_for_tokens()
        
        return self.context
    
    def _fingerprint_architecture(self):
        """Create architecture fingerprint, not full structure"""
        arch = {
            "layers": {},
            "critical_files": [],
            "dependency_clusters": set()
        }
        
        # Layer detection
        layer_patterns = {
            "api": r".*api.*\.py$",
            "models": r".*model.*\.py$|.*schema.*\.py$",
            "services": r".*service.*\.py$|.*logic.*\.py$|.*util.*\.py$",
            "rules": r".*rule.*\.py$|.*rule.*\.json$",
            "config": r".*config.*\.py$|.*setting.*\.py$|\.env"
        }
        
        for py_file in self.root.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
                
            rel_path = str(py_file.relative_to(self.root))
            
            # Check which layer
            for layer, pattern in layer_patterns.items():
                if re.search(pattern, rel_path, re.IGNORECASE):
                    arch["layers"][layer] = arch["layers"].get(layer, 0) + 1
            
            # Critical files (main, routers)
            if any(x in rel_path for x in ["main.py", "router", "__init__"]):
                arch["critical_files"].append(rel_path)
        
        # Import clusters (what imports what)
        for py_file in list(self.root.rglob("*.py"))[:20]:  # Sample 20 files
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(5000)
                    imports = re.findall(r'from (\S+) import|import (\S+)', content)
                    for imp in imports:
                        module = imp[0] or imp[1]
                        if module and '.' in module:
                            arch["dependency_clusters"].add(module.split('.')[0])
            except:
                pass
        
        arch["dependency_clusters"] = list(arch["dependency_clusters"])
        self.context["architecture"] = arch
    
    def _extract_critical_patterns(self):
        """Extract only critical patterns for AI understanding"""
        patterns = {
            "auth": {},
            "validation": {},
            "errors": {},
            "queries": {}
        }
        
        # Sample key files for patterns
        sample_files = []
        for pattern in ["auth.py", "models.py"]:
            sample_files.extend(list(self.root.rglob(pattern))[:3])
        # Also add API files
        sample_files.extend(list(self.root.rglob("*api*.py"))[:3])
        
        for file in sample_files[:10]:  # Limit to 10 files
            try:
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(10000)
                    
                    # Authentication patterns
                    if "jwt" in content.lower() or "token" in content.lower():
                        patterns["auth"]["type"] = "jwt"
                        patterns["auth"]["has_oauth"] = "oauth" in content.lower()
                    
                    # Validation patterns
                    if "pydantic" in content.lower() or "validation" in content.lower():
                        patterns["validation"]["framework"] = "pydantic"
                        patterns["validation"]["has_custom"] = "validator" in content.lower()
                    
                    # Error handling patterns
                    error_handlers = re.findall(r'except (\w+)', content)
                    if error_handlers:
                        patterns["errors"]["handlers"] = list(set(error_handlers))[:5]
                    
                    # Query patterns
                    if "session" in content or "query" in content:
                        patterns["queries"]["orm"] = "sqlalchemy"
                        patterns["queries"]["has_raw"] = "text(" in content
            except:
                pass
        
        self.context["patterns"] = patterns
    
    def _map_key_flows(self):
        """Map critical data/business flows succinctly"""
        flows = {
            "patient_evaluation": [],
            "analytics_generation": [],
            "user_management": []
        }
        
        # Look for flow indicators in code
        flow_keywords = {
            "patient_evaluation": ["evaluate", "recommendation", "patient", "transfusion"],
            "analytics_generation": ["analytics", "roi", "summary", "report"],
            "user_management": ["user", "register", "login", "permission"]
        }
        
        for py_file in self.root.rglob("*.py"):
            if "api" not in str(py_file) and "service" not in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(5000)
                    
                    for flow_type, keywords in flow_keywords.items():
                        if any(kw in content.lower() for kw in keywords):
                            flows[flow_type].append({
                                "file": str(py_file.relative_to(self.root)),
                                "indicators": [kw for kw in keywords if kw in content.lower()][:3]
                            })
            except:
                pass
        
        # Limit each flow to 3 entries
        for flow in flows:
            flows[flow] = flows[flow][:3]
        
        self.context["flows"] = flows
    
    def _identify_gaps(self):
        """Identify gaps, risks, and areas needing attention"""
        gaps = {
            "security": [],
            "testing": [],
            "documentation": [],
            "performance": []
        }
        
        # Security gaps
        security_files = list(self.root.rglob("*security*.py")) + list(self.root.rglob("*auth*.py"))
        if len(security_files) < 2:
            gaps["security"].append("Limited dedicated security modules")
        
        # Testing gaps
        test_files = list(self.root.rglob("*test*.py"))
        if len(test_files) < 5:
            gaps["testing"].append(f"Only {len(test_files)} test files found")
        
        # Documentation gaps (check README, docstrings)
        readme_files = list(self.root.rglob("README*")) + list(self.root.rglob("*.md"))
        if len(readme_files) < 2:
            gaps["documentation"].append("Limited documentation files")
        
        # Performance indicators
        for py_file in self.root.rglob("*.py"):
            if "api" in str(py_file):
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(10000)
                        if "paginate" not in content and "limit" not in content:
                            gaps["performance"].append("API endpoints may lack pagination")
                            break
                except:
                    pass
        
        # Clean empty gap categories
        gaps = {k: v for k, v in gaps.items() if v}
        self.context["gaps"] = gaps
    
    def _optimize_for_tokens(self):
        """Optimize context for minimal token usage"""
        # Remove empty sections
        for key in list(self.context.keys()):
            if isinstance(self.context[key], dict) and not self.context[key]:
                del self.context[key]
            elif isinstance(self.context[key], list) and not self.context[key]:
                del self.context[key]
        
        # Compress lists to strings where possible
        if "architecture" in self.context:
            arch = self.context["architecture"]
            if "critical_files" in arch:
                arch["critical_files"] = arch["critical_files"][:5]  # Keep only 5
        
        # Add token estimate
        json_str = json.dumps(self.context, separators=(',', ':'))
        self.context["metadata"]["token_estimate"] = len(json_str) // 4
        
        # Add content hash for change detection
        self.context["metadata"]["hash"] = hashlib.md5(json_str.encode()).hexdigest()[:8]
    
    def create_ai_delta_package(self):
        """Create what AI needs beyond what you already have"""
        delta = {
            # 1. Code patterns
            "patterns": self._extract_code_patterns(),
            
            # 2. Business rules mapping
            "rule_mappings": self._map_rules_to_code(),
            
            # 3. Error handling strategies
            "error_strategies": self._analyze_error_handling(),
            
            # 4. Configuration patterns
            "config_patterns": self._extract_config_patterns(),
            
            # 5. Test coverage gaps (already in gaps)
            "test_gaps": self.context.get("gaps", {}).get("testing", []),
            
            # 6. Performance indicators
            "performance_indicators": self._find_performance_patterns(),
            
            # 7. Security patterns
            "security_patterns": self._analyze_security_patterns()
        }
        
        return {k: v for k, v in delta.items() if v}  # Remove empty
    
    def _extract_code_patterns(self):
        """Extract common code patterns"""
        patterns = {}
        
        # Look for decorator patterns
        decorator_counts = {}
        for py_file in list(self.root.rglob("*.py"))[:15]:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(5000)
                    decorators = re.findall(r'@(\w+)', content)
                    for dec in decorators:
                        decorator_counts[dec] = decorator_counts.get(dec, 0) + 1
            except:
                pass
        
        if decorator_counts:
            patterns["common_decorators"] = sorted(
                decorator_counts.items(), key=lambda x: x[1], reverse=True
            )[:5]
        
        return patterns
    
    def _map_rules_to_code(self):
        """Map business rules to code implementation"""
        rule_mappings = {}
        
        # Look for rules directory
        rules_dir = self.root / "app" / "rules"
        if rules_dir.exists():
            rule_files = list(rules_dir.glob("*.json"))
            rule_mappings["rule_files"] = [f.name for f in rule_files[:5]]
            
            # Check if rules are referenced in code
            api_files = list(self.root.rglob("*api*.py"))[:10]
            rule_references = 0
            for api_file in api_files:
                try:
                    with open(api_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(10000)
                        if "rule" in content.lower():
                            rule_references += 1
                except:
                    pass
            
            rule_mappings["api_references"] = rule_references
        
        return rule_mappings
    
    def _analyze_error_handling(self):
        """Analyze error handling strategies"""
        strategies = {}
        
        # Check for custom exception classes
        exceptions = []
        for py_file in list(self.root.rglob("*.py"))[:10]:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(5000)
                    if "class.*Exception" in content or "HTTPException" in content:
                        # Find exception classes
                        exception_matches = re.findall(r'class (\w+Exception)', content)
                        exceptions.extend(exception_matches)
            except:
                pass
        
        if exceptions:
            strategies["custom_exceptions"] = list(set(exceptions))[:5]
        
        # Check for try-except patterns
        try_files = []
        for py_file in list(self.root.rglob("*.py"))[:10]:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(5000)
                    if "try:" in content and "except" in content:
                        try_files.append(str(py_file.relative_to(self.root)))
            except:
                pass
        
        if try_files:
            strategies["error_handling_files"] = try_files[:3]
        
        return strategies
    
    def _extract_config_patterns(self):
        """Extract configuration patterns"""
        config_patterns = {}
        
        # Check for config files
        config_files = []
        for pattern in [".env", ".env.example", "config*.py", "settings*.py", "*.yaml", "*.yml"]:
            config_files.extend([str(f.relative_to(self.root)) for f in self.root.rglob(pattern)][:2])
        
        if config_files:
            config_patterns["config_files"] = config_files
        
        # Check for environment variable usage
        env_vars = set()
        for py_file in list(self.root.rglob("*.py"))[:10]:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(5000)
                    # Look for os.getenv or similar
                    env_matches = re.findall(r'os\.getenv\(["\']([^"\']+)["\']\)', content)
                    env_vars.update(env_matches)
            except:
                pass
        
        if env_vars:
            config_patterns["env_variables"] = list(env_vars)[:10]
        
        return config_patterns
    
    def _find_performance_patterns(self):
        """Find performance-related patterns"""
        performance = {}
        
        # Check for caching
        cache_indicators = []
        for py_file in list(self.root.rglob("*.py"))[:10]:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(5000)
                    if any(x in content.lower() for x in ["cache", "redis", "memcached", "lru"]):
                        cache_indicators.append(str(py_file.relative_to(self.root)))
            except:
                pass
        
        if cache_indicators:
            performance["caching_indicators"] = cache_indicators[:3]
        
        # Check for database optimization
        db_optimizations = []
        for py_file in list(self.root.rglob("*.py"))[:10]:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(5000)
                    if any(x in content for x in [".limit(", ".offset(", "index", "explain"]):
                        db_optimizations.append(str(py_file.relative_to(self.root)))
            except:
                pass
        
        if db_optimizations:
            performance["db_optimizations"] = db_optimizations[:3]
        
        return performance
    
    def _analyze_security_patterns(self):
        """Analyze security patterns"""
        security = {}
        
        # Check for password hashing
        hashing_libs = set()
        for py_file in list(self.root.rglob("*.py"))[:10]:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(5000)
                    if any(x in content.lower() for x in ["bcrypt", "argon2", "scrypt", "pbkdf2"]):
                        hashing_libs.add(str(py_file.relative_to(self.root)))
            except:
                pass
        
        if hashing_libs:
            security["password_hashing"] = list(hashing_libs)[:3]
        
        # Check for input validation
        validation_files = []
        for py_file in list(self.root.rglob("*api*.py"))[:10]:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(5000)
                    if "regex" in content or "sanitize" in content or "xss" in content.lower():
                        validation_files.append(str(py_file.relative_to(self.root)))
            except:
                pass
        
        if validation_files:
            security["input_validation"] = validation_files[:3]
        
        return security
    
    def save_context(self, output_path: str = None):
        """Save optimized AI context"""
        if not output_path:
            # Create docs directory if it doesn't exist
            docs_dir = self.root / "docs"
            docs_dir.mkdir(exist_ok=True)
            output_path = docs_dir / "ai_context.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.context, f, separators=(',', ':'), indent=None)
        
        tokens = self.context["metadata"]["token_estimate"]
        print(f"✅ AI Context saved: {output_path}")
        print(f"📏 Size: ~{tokens:,} tokens (fits easily)")
        
        return output_path
    
    def save_delta_package(self, output_path: str = None):
        """Save delta package (what's missing from existing docs)"""
        if not output_path:
            # Create docs directory if it doesn't exist
            docs_dir = self.root / "docs"
            docs_dir.mkdir(exist_ok=True)
            output_path = docs_dir / "ai_delta.json"
        
        delta = self.create_ai_delta_package()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(delta, f, separators=(',', ':'), indent=None)
        
        tokens = len(json.dumps(delta, separators=(',', ':'))) // 4
        print(f"✅ AI Delta Package saved: {output_path}")
        print(f"📏 Size: ~{tokens:,} tokens")
        
        return output_path

# USAGE
if __name__ == "__main__":
    builder = AIContextBuilder(r"C:\Users\mdmho\transfusion-cds\backend")
    
    # Build minimal context
    context = builder.build_minimal_context()
    builder.save_context()
    
    # Also create delta package
    builder.save_delta_package()
    
    print("\n🎯 UPLOAD BOTH TO AI:")
    print("1. ai_context.json - Architecture fingerprint")
    print("2. ai_delta.json - Missing pieces from your docs")
    print("\n📚 ALREADY HAVE:")
    print("• API Documentation (hand-written)")
    print("• Database Schema (auto-generated)")