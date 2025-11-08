#!/usr/bin/env python3
"""
Final dataset status including negatives
"""

from pathlib import Path

sources = {
    'APIs.guru': 'apis_guru/apis_guru_examples.jsonl',
    'SchemaStore': 'schemastore/schemastore_examples.jsonl',
    'CloudEvents': 'cloudevents/cloudevents_examples.jsonl',
    'Paraloq': 'paraloq/paraloq_examples.jsonl',
    'MasterControl': 'mastercontrol/mastercontrol_examples.jsonl',
    'Negatives': 'negatives/negative_examples.jsonl'
}

raw_dir = Path('../datasets/raw')
total = 0
positives = 0

print('\n' + '='*80)
print('FINAL DATASET STATUS - JSON EXPERT')
print('='*80 + '\n')

for name, path in sources.items():
    file_path = raw_dir / path
    if file_path.exists():
        count = sum(1 for _ in open(file_path, 'r', encoding='utf-8'))
        size_mb = file_path.stat().st_size / (1024 * 1024)
        status = '[NEG]' if name == 'Negatives' else '[POS]'
        print(f'{status} {name:20s}: {count:>8,} examples ({size_mb:>7.1f} MB)')
        total += count
        if name != 'Negatives':
            positives += count
    else:
        print(f'[???] {name:20s}: NOT COLLECTED YET')

print('\n' + '-'*80)
print(f'Positive examples:        {positives:>8,}')
print(f'Negative examples:        {total - positives:>8,}')
print(f'TOTAL DATASET SIZE:       {total:>8,} examples')
print('='*80)

# Distribution
if total > 0:
    print(f'\nDataset Distribution:')
    print(f'  Positives: {positives/total*100:.1f}% (generation + extraction)')
    print(f'  Negatives: {(total-positives)/total*100:.1f}% (autocorrection)')

print('\n' + '='*80)
print('READY FOR PREPROCESSING & TRAINING')
print('='*80)
print('\nNext steps:')
print('  1. python preprocess.py')
print('  2. ../../cli/target/release/expert-cli train')
print('\nEstimated training time: ~4-6 hours (RTX 4090 + Unsloth)')
print('Expected checkpoints: 250, 500, 750, 1000, 1250, 1500+')
print('='*80)

