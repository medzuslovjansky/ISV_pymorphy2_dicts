import unicodedata
from string import whitespace
from collections import Counter, defaultdict

import js2py
import re

translations = {}
all_words = set()

complex_words = set()
word_forms = defaultdict(list)
# something with spaces is bad...

predefined_forms = {
}

with open("C:/dev/discord/data.txt", "r", encoding="utf8") as f:
    for line in f:
        # print(line.split("\t"))
        #if "prisutstvovatipri" in line:
        # if "23860" == line[:5]:
        parts = line.split("\t")
        if "$23860" in line[:5]:
            print(line)
            print(parts)
        if len(parts) == 16:
            if " " in parts[1]:
                complex_words.add(parts[0])
        if len(parts) != 16:
            lang_id = parts[0].split("-")
            if lang_id[0] in complex_words:
                continue
            if lang_id[-2:] == ["isv", "src"]:
                forms = parts[1].strip().split("|")
                all_words.add(f for f in forms)
                base_form = forms[0]
                if "$23860-" == line[:6]:
                    print(forms)
                    print(base_form)
                for form in forms:
                    word_forms[form].append(base_form)

print(len(word_forms))
print(len(all_words))

print(word_forms['se'])
pronouns = set()

for form, data in word_forms.items():
    if len(set(data)) > 5:
        if 'go' in data:
            print(form, data)
            pronouns |= set(data) | set([form])

print(pronouns)