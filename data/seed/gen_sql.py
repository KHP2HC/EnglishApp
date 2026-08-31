"""Generate SQL seed file from vocab data for Supabase."""
import json
import os

base = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(base, 'vocab_enriched.json'), 'r', encoding='utf-8') as f:
    vocab = json.load(f)
with open(os.path.join(base, 'vocab_fixed.json'), 'r', encoding='utf-8') as f:
    fixed = json.load(f)

fixed_map = {item['word']: item for item in fixed}
merged = {}
for item in vocab:
    word = item['word']
    if word in fixed_map:
        merged[word] = fixed_map[word]
    else:
        merged[word] = item
for word, item in fixed_map.items():
    if word not in merged:
        merged[word] = item

result = list(merged.values())

def esc(s):
    if s is None:
        return 'NULL'
    s = str(s).replace("'", "''")
    return f"'{s}'"

lines = ['-- Seed Vocabulary Data (5,251 words)']
lines.append('-- Run after 001_initial.sql')
lines.append('')

batch_size = 500
for i in range(0, len(result), batch_size):
    batch = result[i:i+batch_size]
    lines.append('insert into vocab_cards (word, phonetic, meaning_en, meaning_vi, example_sentence, exam_type, cefr_level, category) values')
    rows = []
    for item in batch:
        word = esc(item.get('word', ''))
        phonetic = esc(item.get('phonetic'))
        meaning_en = esc(item.get('meaning_en') or 'Common English vocabulary word.')
        meaning_vi = esc(item.get('meaning_vi') or 'T\u1eeb v\u1ef1ng ti\u1ebfng Anh th\u00f4ng d\u1ee5ng.')
        example = esc(item.get('example_sentence'))
        exam = (item.get('exam_type') or 'IELTS').upper()
        exam_arr = '{' + exam + '}'
        level = (item.get('difficulty_level') or 'B1').upper()
        if level not in ('A1', 'A2', 'B1', 'B2', 'C1', 'C2'):
            level = 'B1'
        category = esc(item.get('category') or 'general')
        rows.append(f"  ({word}, {phonetic}, {meaning_en}, {meaning_vi}, {example}, '{exam_arr}', '{level}', {category})")
    lines.append(',\n'.join(rows) + ';')
    lines.append('')

out_path = os.path.join(base, '..', '..', 'web', 'supabase', 'migrations', '002_seed_vocab.sql')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f'Wrote {len(result)} vocab entries to {out_path}')
