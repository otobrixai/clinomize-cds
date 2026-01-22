#!/usr/bin/env python3
"""
TRANFUSIONIQ - SMART CODE INDEXER
Creates a searchable index of your codebase for AI troubleshooting.
Organizes by file type and importance.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
import hashlib

@dataclass
class CodeFile:
    path: str
    content: str
    lines: int
    type: str
    importance: int  # 1=low, 5=critical
    functions: List[str]
    classes: List[str]
    hash: str

class SmartCodeIndexer:
    def __init__(self, project_root: str, max_total_tokens: int = 30000):
        self.root = Path(project_root)
        self.max_tokens = max_total_tokens
        self.index = {
            "metadata": {
                "project": "TransfusionIQ",
                "total_files": 0,
                "total_lines": 0,
                "index_hash": "",
                "token_estimate": 0
            },
            "critical_files": {},      # API, models, services (full content)
            "important_files": {},     # Config, utils (summarized)
            "other_files": {},         # Tests, migrations (metadata only)
            "search_index": {}         # Function/class locations
        }
        
        # Priority order for file types
        self.file_priority = {
            "api": 5,
            "model": 5, 
            "service": 4,
            "schema": 4,
            "router": 5,
            "config": 4,
            "main": 5,
            "rule": 3,
            "util": 3,
            "test": 2,
            "migration": 2,
            "other": 1
        }
    
    def create_index(self) -> Dict:
        """Create smart code index"""
        print("📚 Creating smart code index...")
        
        all_files = self._collect_files()
        print(f"📁 Found {len(all_files)} files")
        
        # Process files by priority
        critical_files = []
        important_files = []
        other_files = []
        
        for file_path in all_files:
            priority = self._get_file_priority(file_path)
            code_file = self._process_file(file_path, priority)
            
            if priority >= 4:
                critical_files.append(code_file)
            elif priority == 3:
                important_files.append(code_file)
            else:
                other_files.append(code_file)
        
        # Build index with token limits
        self._build_index_smart(critical_files, important_files, other_files)
        
        # Create search index
        self._create_search_index()
        
        # Calculate tokens and hash
        self._finalize_index()
        
        return self.index
    
    def _collect_files(self) -> List[Path]:
        """Collect all relevant files"""
        files = []
        exclude_dirs = {'.git', '__pycache__', 'venv', '.venv', 'node_modules', '.idea', '.vscode'}
        exclude_exts = {'.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe'}
        
        for py_file in self.root.rglob("*.py"):
            # Skip excluded directories
            if any(exclude in str(py_file) for exclude in exclude_dirs):
                continue
            
            # Skip excluded file types
            if any(py_file.suffix == ext for ext in exclude_exts):
                continue
            
            files.append(py_file)
        
        # Also include important non-Python files
        for pattern in ['*.json', '*.yaml', '*.yml', '*.md', '*.txt', 'Dockerfile', 'requirements.txt']:
            for file in self.root.rglob(pattern):
                if any(exclude in str(file) for exclude in exclude_dirs):
                    continue
                if file not in files:
                    files.append(file)
        
        return files
    
    def _get_file_priority(self, file_path: Path) -> int:
        """Determine file priority for indexing"""
        rel_path = str(file_path.relative_to(self.root)).lower()
        
        # Check file patterns
        patterns = {
            5: [  # Critical
                r'.*api.*\.py$',
                r'.*model.*\.py$',
                r'.*schema.*\.py$',
                r'.*router.*\.py$',
                r'main\.py$',
                r'app\.py$'
            ],
            4: [  # Important
                r'.*service.*\.py$',
                r'.*config.*\.py$',
                r'.*setting.*\.py$',
                r'.*core.*\.py$',
                r'.*auth.*\.py$',
                r'.*rule.*\.py$',
                r'.*rule.*\.json$'
            ],
            3: [  # Medium
                r'.*util.*\.py$',
                r'.*helper.*\.py$',
                r'.*deps.*\.py$',
                r'\.env$',
                r'requirements\.txt$'
            ],
            2: [  # Low
                r'.*test.*\.py$',
                r'.*migration.*\.py$',
                r'.*alembic.*\.py$'
            ]
        }
        
        for priority, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.match(pattern, rel_path):
                    return priority
        
        return 1  # Default priority
    
    def _process_file(self, file_path: Path, priority: int) -> CodeFile:
        """Process a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            content = "[Binary or unreadable file]"
        
        # Extract structure for Python files
        functions = []
        classes = []
        
        if file_path.suffix == '.py':
            functions = self._extract_functions(content)
            classes = self._extract_classes(content)
        
        # Calculate hash
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        
        return CodeFile(
            path=str(file_path.relative_to(self.root)),
            content=content,
            lines=len(content.splitlines()),
            type=self._get_file_type(file_path),
            importance=priority,
            functions=functions,
            classes=classes,
            hash=content_hash
        )
    
    def _extract_functions(self, content: str) -> List[str]:
        """Extract function names from Python code"""
        functions = []
        try:
            # Look for function definitions
            func_pattern = r'^(?:async\s+)?def\s+(\w+)\s*\('
            for match in re.finditer(func_pattern, content, re.MULTILINE):
                functions.append(match.group(1))
        except:
            pass
        return functions[:20]  # Limit to 20 functions per file
    
    def _extract_classes(self, content: str) -> List[str]:
        """Extract class names from Python code"""
        classes = []
        try:
            # Look for class definitions
            class_pattern = r'^class\s+(\w+)\s*[(:]'
            for match in re.finditer(class_pattern, content, re.MULTILINE):
                classes.append(match.group(1))
        except:
            pass
        return classes[:10]  # Limit to 10 classes per file
    
    def _get_file_type(self, file_path: Path) -> str:
        """Get file type category"""
        suffixes = {
            '.py': 'python',
            '.json': 'json',
            '.yaml': 'yaml', '.yml': 'yaml',
            '.md': 'markdown',
            '.txt': 'text',
            '.sql': 'sql',
            '.html': 'html',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.css': 'css'
        }
        return suffixes.get(file_path.suffix, 'other')
    
    def _build_index_smart(self, critical: List[CodeFile], important: List[CodeFile], other: List[CodeFile]):
        """Build index with smart content selection"""
        
        # 1. Critical files (full content)
        for file in critical[:50]:  # Limit to 50 critical files
            self.index["critical_files"][file.path] = {
                "content": file.content,
                "lines": file.lines,
                "type": file.type,
                "functions": file.functions,
                "classes": file.classes,
                "hash": file.hash
            }
        
        # 2. Important files (summarized)
        for file in important[:30]:  # Limit to 30 important files
            # Summarize long files
            if file.lines > 200:
                summary = self._summarize_file(file.content)
                content = summary
            else:
                content = file.content
            
            self.index["important_files"][file.path] = {
                "content": content,
                "lines": file.lines,
                "type": file.type,
                "functions": file.functions,
                "classes": file.classes,
                "hash": file.hash,
                "full_content_available": file.lines <= 200
            }
        
        # 3. Other files (metadata only)
        for file in other[:100]:  # Limit to 100 other files
            self.index["other_files"][file.path] = {
                "lines": file.lines,
                "type": file.type,
                "functions": file.functions[:5],  # Just first 5
                "classes": file.classes[:3],      # Just first 3
                "hash": file.hash
            }
        
        # Update metadata
        self.index["metadata"]["total_files"] = len(critical) + len(important) + len(other)
        self.index["metadata"]["total_lines"] = sum(f.lines for f in critical + important + other)
    
    def _summarize_file(self, content: str, max_lines: int = 100) -> str:
        """Summarize a file by keeping key parts"""
        lines = content.splitlines()
        
        if len(lines) <= max_lines:
            return content
        
        # Keep first 30 lines (usually imports and class definitions)
        # Keep last 30 lines (often main logic)
        # Look for function/class definitions in the middle
        important_lines = []
        
        # First 30 lines
        important_lines.extend(lines[:30])
        
        # Last 30 lines  
        important_lines.extend(lines[-30:])
        
        # Find key lines in the middle (function/class definitions)
        middle_start = 30
        middle_end = len(lines) - 30
        
        for i in range(middle_start, middle_end):
            line = lines[i]
            # Look for important patterns
            if any(pattern in line for pattern in ['def ', 'class ', '@', 'def ', 'async def ']):
                # Add 2 lines before and 2 lines after for context
                for j in range(max(0, i-2), min(len(lines), i+3)):
                    if lines[j] not in important_lines:
                        important_lines.append(lines[j])
        
        # Deduplicate and add summary note
        important_lines = list(dict.fromkeys(important_lines))
        
        summary = "\n".join(important_lines[:max_lines])
        summary += f"\n\n[FILE TRUNCATED: Original {len(lines)} lines, showing {len(important_lines)} key lines]"
        
        return summary
    
    def _create_search_index(self):
        """Create search index for functions/classes"""
        search_index = {}
        
        # Index from critical files
        for file_path, file_data in self.index["critical_files"].items():
            for func in file_data.get("functions", []):
                search_index.setdefault(func, []).append({
                    "file": file_path,
                    "type": "function",
                    "context": self._get_function_context(file_data["content"], func)
                })
            
            for cls in file_data.get("classes", []):
                search_index.setdefault(cls, []).append({
                    "file": file_path,
                    "type": "class",
                    "context": self._get_class_context(file_data["content"], cls)
                })
        
        # Index from important files
        for file_path, file_data in self.index["important_files"].items():
            for func in file_data.get("functions", []):
                search_index.setdefault(func, []).append({
                    "file": file_path,
                    "type": "function",
                    "context": "[Content summarized - check file for details]"
                })
        
        self.index["search_index"] = search_index
    
    def _get_function_context(self, content: str, func_name: str) -> str:
        """Extract context around a function"""
        pattern = rf'^(?:async\s+)?def\s+{func_name}\s*\(.*?\):'
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        
        if match:
            start = match.start()
            # Get 10 lines after function definition
            lines = content[start:].splitlines()[:15]
            return "\n".join(lines)
        
        return f"Function {func_name} definition"
    
    def _get_class_context(self, content: str, class_name: str) -> str:
        """Extract context around a class"""
        pattern = rf'^class\s+{class_name}\s*[(:].*?:'
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        
        if match:
            start = match.start()
            # Get 20 lines after class definition
            lines = content[start:].splitlines()[:25]
            return "\n".join(lines)
        
        return f"Class {class_name} definition"
    
    def _finalize_index(self):
        """Finalize index with token calculation"""
        json_str = json.dumps(self.index, separators=(',', ':'))
        self.index["metadata"]["token_estimate"] = len(json_str) // 4
        self.index["metadata"]["index_hash"] = hashlib.md5(json_str.encode()).hexdigest()[:12]
    
    def save_index(self, output_path: str = None):
        """Save the code index"""
        if not output_path:
            docs_dir = self.root / "docs"
            docs_dir.mkdir(exist_ok=True)
            output_path = docs_dir / "code_index.json"
        
        # Use compression for large files
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=None, separators=(',', ':'))
        
        tokens = self.index["metadata"]["token_estimate"]
        size_mb = Path(output_path).stat().st_size / 1024 / 1024
        
        print(f"✅ Code index saved: {output_path}")
        print(f"📊 Stats:")
        print(f"   • Files indexed: {self.index['metadata']['total_files']}")
        print(f"   • Total lines: {self.index['metadata']['total_lines']:,}")
        print(f"   • Critical files: {len(self.index['critical_files'])}")
        print(f"   • Important files: {len(self.index['important_files'])}")
        print(f"   • Token estimate: {tokens:,}")
        print(f"   • File size: {size_mb:.1f} MB")
        
        # Create a lightweight version if too large
        if tokens > 30000:
            print(f"\n⚠️  Index is large ({tokens:,} tokens). Creating lightweight version...")
            self._create_lightweight_index(output_path)
        
        return output_path
    
    def _create_lightweight_index(self, original_path: Path):
        """Create a lightweight version of the index"""
        lightweight = {
            "metadata": self.index["metadata"],
            "file_list": {},
            "search_index": self.index["search_index"]
        }
        
        # Just file metadata, not content
        for category in ["critical_files", "important_files", "other_files"]:
            for file_path, data in self.index[category].items():
                lightweight["file_list"][file_path] = {
                    "lines": data.get("lines", 0),
                    "type": data.get("type", "unknown"),
                    "functions": data.get("functions", [])[:3],
                    "classes": data.get("classes", [])[:2],
                    "hash": data.get("hash", "")
                }
        
        # Save lightweight version
        lightweight_path = original_path.parent / "code_index_light.json"
        with open(lightweight_path, 'w', encoding='utf-8') as f:
            json.dump(lightweight, f, indent=None, separators=(',', ':'))
        
        tokens = len(json.dumps(lightweight, separators=(',', ':'))) // 4
        print(f"✅ Lightweight index: {lightweight_path}")
        print(f"   • Token estimate: {tokens:,}")
        print(f"   • Use this for quick searches, full index for details")

# Usage
if __name__ == "__main__":
    print("📚 TRANFUSIONIQ - SMART CODE INDEXER")
    print("=" * 60)
    
    indexer = SmartCodeIndexer(r"C:\Users\mdmho\transfusion-cds\backend")
    index = indexer.create_index()
    
    index_file = indexer.save_index()
    
    print("\n" + "=" * 60)
    print("🎯 HOW TO USE WITH AI:")
    print("=" * 60)
    print("\nFor troubleshooting, provide:")
    print("1. The error/message you're seeing")
    print("2. This code_index.json file")
    print("\nAI can now:")
    print("• Search for functions/classes by name")
    print("• See full code of critical files")
    print("• Find where specific patterns occur")
    print("• Trace error locations")
    print("\nExample prompt:")
    print('"""')
    print("I'm getting 'ImportError: cannot import name X'")
    print("Here's my code index. Find where X is defined and used.")
    print('"""')