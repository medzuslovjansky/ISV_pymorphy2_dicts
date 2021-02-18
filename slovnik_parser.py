
from collections import Counter, defaultdict


translations = defaultdict(dict)
morphology_src = {}

unknown_ids = []

metadata_arr = []

with open("data.txt", "r", encoding="utf8") as f:
    content = f.read()
    metadata_lines, translation_lines, completion_stats = content.split("<>")
    for line in metadata_lines.splitlines():
        arr = line.strip().split('\t')
        if len(arr) == 16:
            metadata_arr.append(tuple(arr))
        if len(arr) == 1:
            unknown_ids.append(arr[0])
    for line in translation_lines.splitlines():
        arr = line.strip().split('\t')
        if arr[0].startswith("id"):
            continue
        if len(arr) == 1:
            unknown_ids.append(arr[0])
        if len(arr) == 2:
            lang_id, value = arr
            word_id, _, lang = lang_id.partition("-")
            translations[word_id][lang] = value.split("|")


print()
print(unknown_ids)

'''
for entry in unknown_ids:
    print(entry)
    word_id, lang = entry.split("-")
    print(translations[word_id])
'''

import pandas as pd

df = pd.DataFrame(
    metadata_arr, 
    columns=[
        "word_id", "ISV", "addition", "PartOfSpeech", 
        "EN", "RU", "BE", "UK", "PL", "CS", "SK", "SL", "HR", "SR", "MK", "BG"
    ]
).set_index("word_id")
print(df.PartOfSpeech.unique())

df.to_csv("word_meta.csv", encoding="utf8")
# pd.DataFrame(metadata_arr).to_excel("word_meta_win.xlsx", encoding="utf8")

sizes = Counter()
for word_id, entry in translations.items():
    sizes[len(entry['isv'])] += 1

print(sorted(sizes.items(), key=lambda x: x[0]))

for word_id, entry in translations.items():
    if len(entry['isv']) != len(entry['isv-src']):
        print(entry['isv'])
        print(entry['isv-src'])
        print(entry['ru'], entry['en'])
        print(len(entry['isv']))
        print(word_id)
        break

for word_id, entry in translations.items():
    if sizes[len(entry['isv'])] == 1:
        pass
        '''
        print(entry['isv'][0], len(entry['isv']))
        print(entry['isv-src'][0], len(entry['isv-src']))
        print(entry['ru'], entry['en'])
        print(word_id)
        print("------")
        '''
    if len(entry['isv']) >= 67:
        print(word_id, entry['isv'][0], entry['ru'], entry['en'])
        print(entry['isv-src'][0], len(entry['isv-src']))
