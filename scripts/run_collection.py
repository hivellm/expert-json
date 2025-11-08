#!/usr/bin/env python3
"""
Automated Collection Runner

Runs all data collection scripts in sequence:
1. APIs.guru (slowest)
2. SchemaStore (moderate)
3. CloudEvents (fast)
4. Negative generation (fast)

Total time: ~3-7 hours depending on network
"""

import subprocess
import sys
from pathlib import Path
import time

def run_script(script_name: str, description: str):
    """Run a collection script and track time"""
    print("\n" + "="*70)
    print(f"RUNNING: {script_name}")
    print(f"Description: {description}")
    print("="*70 + "\n")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            capture_output=False
        )
        
        elapsed = time.time() - start_time
        print(f"\n✅ {script_name} completed in {elapsed/60:.1f} minutes")
        return True
    
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        print(f"\n❌ {script_name} failed after {elapsed/60:.1f} minutes")
        print(f"Error: {e}")
        return False

def main():
    scripts_dir = Path(__file__).parent
    
    # Check if scripts exist
    required_scripts = [
        ("collect_apis_guru.py", "Fetch OpenAPI specs from APIs.guru (~20-30k examples, 2-4 hours)"),
        ("collect_schemastore.py", "Download JSON Schemas from SchemaStore (~15-20k examples, 1-2 hours)"),
        ("collect_cloudevents.py", "Generate CloudEvents examples (~5k examples, 5 minutes)"),
        ("generate_negatives.py", "Create invalid JSON + corrections (~30-40k examples, 30 minutes)")
    ]
    
    missing = []
    for script_name, _ in required_scripts:
        if not (scripts_dir / script_name).exists():
            missing.append(script_name)
    
    if missing:
        print("❌ Missing scripts:")
        for s in missing:
            print(f"  - {s}")
        return
    
    # Run all scripts
    print("="*70)
    print("EXPERT-JSON DATA COLLECTION PIPELINE")
    print("="*70)
    print("\nEstimated total time: 3-7 hours")
    print("Network-dependent (APIs.guru has ~3000 APIs to download)\n")
    
    input("Press Enter to start collection...")
    
    overall_start = time.time()
    results = []
    
    for script_name, description in required_scripts:
        script_path = scripts_dir / script_name
        success = run_script(str(script_path), description)
        results.append((script_name, success))
        
        if not success:
            print(f"\n⚠️  {script_name} failed. Continue anyway? (y/n)")
            if input().lower() != 'y':
                print("\nCollection aborted.")
                return
    
    overall_elapsed = time.time() - overall_start
    
    # Summary
    print("\n\n" + "="*70)
    print("COLLECTION COMPLETE")
    print("="*70)
    print(f"\nTotal time: {overall_elapsed/3600:.1f} hours ({overall_elapsed/60:.1f} minutes)")
    print(f"\nResults:")
    for script_name, success in results:
        status = "✅ Success" if success else "❌ Failed"
        print(f"  {status:12s} - {script_name}")
    
    print(f"\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print(f"\n1. Run preprocessing:")
    print(f"   python ../preprocess.py")
    print(f"\n2. Validate dataset:")
    print(f"   python validate_dataset.py")
    print(f"\n3. Start training:")
    print(f"   ../../cli/target/release/expert-cli train")

if __name__ == "__main__":
    main()

