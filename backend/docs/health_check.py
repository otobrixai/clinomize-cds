#!/usr/bin/env python3
"""
TransfusionIQ Health Check
Checks documentation in /docs folder.
"""

import json
from pathlib import Path
import sys

def check_docs_folder():
    """Check if /docs folder exists and has content"""
    docs_dir = Path("docs")
    if not docs_dir.exists():
        print("❌ /docs folder: Does not exist")
        return False
    
    # List documentation files
    doc_files = list(docs_dir.glob("*.md")) + list(docs_dir.glob("*.json"))
    
    if not doc_files:
        print("⚠️  /docs folder: Exists but empty")
        return False
    
    print(f"✅ /docs folder: {len(doc_files)} documentation files")
    
    # Show what's there
    for doc_file in sorted(doc_files)[:5]:  # Show first 5
        size_kb = doc_file.stat().st_size / 1024
        print(f"   • {doc_file.name} ({size_kb:.1f} KB)")
    
    if len(doc_files) > 5:
        print(f"   • ... and {len(doc_files) - 5} more")
    
    return True

def check_database_docs():
    """Check if database documentation exists in /docs"""
    db_json = Path("docs/database_schema.json")
    db_md = Path("docs/DATABASE_SCHEMA.md")
    
    if db_json.exists() and db_md.exists():
        try:
            with open(db_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            tables = len(data.get('tables', {}))
            print(f"✅ Database Docs: {tables} tables documented (JSON + Markdown)")
            return True
        except Exception as e:
            print(f"❌ Database Docs: Error reading ({e})")
            return False
    elif db_json.exists():
        print("✅ Database Docs: JSON exists (run generate_schema_docs.py for Markdown)")
        return True
    else:
        print("⚠️  Database Docs: Not found in /docs")
        return False

def check_api_docs():
    """Check if API documentation exists in /docs"""
    api_json = Path("docs/openapi.json")
    api_md = Path("docs/API_ENDPOINTS.md")
    
    if api_json.exists():
        try:
            with open(api_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            endpoints = len(data.get('paths', {}))
            
            if api_md.exists():
                print(f"✅ API Docs: {endpoints} endpoints documented (JSON + Markdown)")
            else:
                print(f"✅ API Docs: {endpoints} endpoints (JSON only)")
            return True
        except Exception as e:
            print(f"❌ API Docs: Error reading ({e})")
            return False
    else:
        print("⚠️  API Docs: No openapi.json in /docs")
        return False

def check_manual_docs():
    """Check if manual documentation exists in /docs"""
    manual_docs = Path("docs/API_DOCUMENTATION.md")
    
    if manual_docs.exists():
        try:
            size_kb = manual_docs.stat().st_size / 1024
            with open(manual_docs, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if len(content) > 1000:
                print(f"✅ Manual Docs: {size_kb:.1f} KB comprehensive documentation")
                return True
            else:
                print("⚠️  Manual Docs: File exists but seems minimal")
                return False
        except Exception as e:
            print(f"❌ Manual Docs: Error reading ({e})")
            return False
    else:
        print("❌ Manual Docs: No API_DOCUMENTATION.md in /docs")
        return False

def main():
    print("🔍 TransfusionIQ Documentation Health Check")
    print("=" * 60)
    print("📁 Checking /docs folder...\n")
    
    checks = [
        ("Documentation Folder", check_docs_folder),
        ("Database Documentation", check_database_docs),
        ("API Documentation", check_api_docs),
        ("Manual Documentation", check_manual_docs),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"📋 {name}:")
        results.append(check_func())
        print()
    
    print("=" * 60)
    successful = sum(results)
    total = len(results)
    
    if successful == total:
        print(f"🎉 PERFECT! All documentation is in /docs folder")
    else:
        print(f"⚠️  {successful}/{total} documentation checks passed")
        
        if not Path("docs").exists():
            print("\n📌 Quick fix: Create /docs folder and move files:")
            print("   mkdir docs")
            print("   move API_DOCUMENTATION.md docs/")
            print("   move database_schema.json docs/")
    
    print("\n📚 Expected files in /docs folder:")
    expected = [
        "API_DOCUMENTATION.md",
        "database_schema.json", 
        "DATABASE_SCHEMA.md",
        "openapi.json",
        "API_ENDPOINTS.md"
    ]
    
    docs_dir = Path("docs")
    for file in expected:
        exists = "✅" if (docs_dir / file).exists() else "❌"
        print(f"   {exists} {file}")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)