#!/usr/bin/env python3
"""
Generate OpenAPI specification and save to /docs folder.
"""

import json
import sys
from pathlib import Path

def generate_openapi():
    """Generate and save OpenAPI specification to /docs"""
    try:
        # Get project root (one level up from this script)
        script_dir = Path(__file__).parent
        if script_dir.name == "docs":
            project_root = script_dir.parent  # Script is in /docs
        else:
            project_root = script_dir  # Script is in project root
        
        sys.path.insert(0, str(project_root))
        
        # Import app
        try:
            from app.main import app
        except ImportError as e:
            print(f"❌ Cannot import FastAPI app: {e}")
            print("   Make sure:")
            print("   1. You're in the backend directory")
            print("   2. Virtual environment is activated: venv\\Scripts\\activate")
            print("   3. Dependencies are installed: pip install -r requirements.txt")
            return False
        
        # Generate OpenAPI specification
        openapi_spec = app.openapi()
        
        # Ensure /docs directory exists
        docs_dir = project_root / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        # Save to /docs folder
        output_file = docs_dir / "openapi.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(openapi_spec, f, indent=2, ensure_ascii=False)
        
        # Also generate a summary Markdown file
        generate_openapi_markdown(docs_dir, openapi_spec)
        
        # Count endpoints
        endpoints = len(openapi_spec.get('paths', {}))
        
        print(f"✅ OpenAPI specification saved to: {output_file}")
        print(f"📊 Total endpoints: {endpoints}")
        print(f"🌐 Interactive docs: http://localhost:8000/docs")
        print(f"📄 JSON docs: http://localhost:8000/openapi.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating OpenAPI spec: {e}")
        return False

def generate_openapi_markdown(docs_dir: Path, openapi_spec: dict):
    """Generate a simple Markdown summary of the API"""
    md_file = docs_dir / "API_ENDPOINTS.md"
    
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write("# TransfusionIQ API Endpoints\n\n")
        f.write(f"**Total Endpoints:** {len(openapi_spec.get('paths', {}))}\n\n")
        
        # Group endpoints by tag/category
        endpoints_by_tag = {}
        
        for path, methods in openapi_spec.get('paths', {}).items():
            for method, details in methods.items():
                tags = details.get('tags', ['Uncategorized'])
                for tag in tags:
                    if tag not in endpoints_by_tag:
                        endpoints_by_tag[tag] = []
                    endpoints_by_tag[tag].append({
                        'path': path,
                        'method': method.upper(),
                        'summary': details.get('summary', 'No description'),
                        'description': details.get('description', '')
                    })
        
        # Write each section
        for tag in sorted(endpoints_by_tag.keys()):
            f.write(f"## {tag}\n\n")
            f.write("| Method | Path | Description |\n")
            f.write("|--------|------|-------------|\n")
            
            for endpoint in sorted(endpoints_by_tag[tag], key=lambda x: (x['method'], x['path'])):
                desc = endpoint['summary'] or endpoint['description']
                if len(desc) > 100:
                    desc = desc[:100] + "..."
                f.write(f"| `{endpoint['method']}` | `{endpoint['path']}` | {desc} |\n")
            
            f.write("\n")
    
    print(f"📝 Generated API_ENDPOINTS.md")

if __name__ == "__main__":
    success = generate_openapi()
    sys.exit(0 if success else 1)