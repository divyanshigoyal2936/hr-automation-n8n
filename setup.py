#!/usr/bin/env python3
"""
Quick setup script for HR Automation N8N project
"""
import os
import json
import shutil

def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 60)
    print("HR Automation N8N - Setup")
    print("=" * 60)
    
    # Check workflows exist
    workflows_dir = os.path.join(project_root, "workflows")
    workflows = [
        "01-job-description-posting.json",
        "02-application-collection.json", 
        "03-candidate-matching.json",
        "04-hr-validation-scheduling.json"
    ]
    
    print("\n[Workflows found:]")
    for wf in workflows:
        path = os.path.join(workflows_dir, wf)
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"  [OK] {wf} ({size:,} bytes)")
        else:
            print(f"  [MISSING] {wf}")
    
    # Check config
    config_dir = os.path.join(project_root, "config")
    env_example = os.path.join(config_dir, "environment.example")
    if os.path.exists(env_example):
        print(f"\n[Config template:] {env_example}")
        print("   Copy to .env and fill in your credentials")
    
    # Check docs
    docs_dir = os.path.join(project_root, "docs")
    docs = ["airtable-schema.md", "deployment-guide.md"]
    print("\n[Documentation:]")
    for doc in docs:
        path = os.path.join(docs_dir, doc)
        if os.path.exists(path):
            print(f"  [OK] {doc}")
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("1. Copy config/environment.example to config/.env")
    print("2. Fill in all API keys and credentials")
    print("3. Create Airtable base using docs/airtable-schema.md")
    print("4. Import workflows into n8n (Workflows -> Import)")
    print("5. Configure credentials in n8n for each service")
    print("6. Activate workflows")
    print("7. Test with sample data")
    print("\n[See docs/deployment-guide.md for detailed instructions]")
    print("=" * 60)

if __name__ == "__main__":
    main()