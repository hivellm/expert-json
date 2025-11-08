#!/usr/bin/env python3
"""
Quick check of collection status
"""

from pathlib import Path

sources = {
    'APIs.guru': 'apis_guru/apis_guru_examples.jsonl',
    'SchemaStore': 'schemastore/schemastore_examples.jsonl',
    'CloudEvents': 'cloudevents/cloudevents_examples.jsonl',
    'Paraloq': 'paraloq/paraloq_examples.jsonl',
    'MasterControl': 'mastercontrol/mastercontrol_examples.jsonl'
}

raw_dir = Path('../datasets/raw')
total = 0

print('\n' + '='*70)
print('COLLECTION STATUS - JSON EXPERT')
print('='*70 + '\n')

for name, path in sources.items():
    file_path = raw_dir / path
    if file_path.exists():
        count = sum(1 for _ in open(file_path, 'r', encoding='utf-8'))
        size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f'{name:20s}: {count:>7,} examples ({size_mb:>6.1f} MB)')
        total += count
    else:
        print(f'{name:20s}: NOT COLLECTED YET')

print('\n' + '-'*70)
print(f'TOTAL (before negatives): {total:>7,} examples')
print('='*70)

print('\nNext steps:')
if total >= 50000:
    print('  [OK] Good progress! Continue with negative generation')
    print('  Run: python scripts/generate_negatives.py')
elif total >= 15000:
    print('  [PARTIAL] Keep collecting APIs.guru and SchemaStore')
else:
    print('  [START] Run: python scripts/run_collection.py')

