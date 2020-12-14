import unicodedata
from string import whitespace
from collections import Counter, defaultdict

import js2py
import re

with open("C:/dev/discord/transliterate.js", "r", encoding="utf8") as f:
    js_string = f.read()


# print(js2py.eval_js(js_string))

# last one: lat x to cyr х 

diacr_letters = "žčšěйćżęų" 
plain_letters = "жчшєjчжеу"


lat_alphabet = "abcčdeěfghijjklmnoprsštuvyzž"
cyr_alphabet = "абцчдеєфгхийьклмнопрсштувызж"


save_diacrits = str.maketrans(diacr_letters, plain_letters)
cyr2lat = str.maketrans(cyr_alphabet, lat_alphabet)

# ољењ трамвай -> 
# чей шар -> 
def make_string_standard(thestring):

    # "e^" -> "ê"
    # 'z\u030C\u030C\u030C' -> 'ž\u030C\u030C'
    thestring = unicodedata.normalize(
        'NFKC', 
        thestring
    ).lower().replace("\n", " ")

    # remove all diacritics beside haceks/carons
    thestring = unicodedata.normalize(
        'NFKD',
        thestring.translate(save_diacrits)
    )
    filtered = "".join(c for c in thestring if c in whitespace or c.isalpha())
    # cyrillic to latin
    filtered = filtered.replace(
        "đ", "dž").replace(
        # Serbian and Macedonian
        "љ", "ль").replace("њ", "нь").replace(
        # Russian
        "я", "йа").replace("ю", "йу").replace("ё", "йо")
        
    filtered = filtered.translate(cyr2lat)
    
    # repeated spaces and 'j's
    return re.sub(r'j+', r'j', filtered)


# import re
# re.sub(r'(.)\1+', r'\1\1', "haaaaapppppyyy")     

translations = {}
word_forms = defaultdict(list)
# something with spaces is bad...
complex_words = set()

pronouns = {'jih', 'njim', 'jem', 'one', 'mu', 'jim', 'njegogo', 'ono', 'jemu', 'je', 'njimi', 'jego', 'njejų', 'nje', 'njej', 'jų', 'jimi', 'jej', 'njų', 'njem', 'go', 'njih', 'on', 'ona', 'oni', 'njemumu', 'njego', 'jejų', 'jesti', 'onoj'}

with open("C:/dev/discord/data.txt", "r", encoding="utf8") as f:
    for line in f:
        # print(line.split("\t"))
        parts = line.split("\t")
        if len(parts) == 16:
            if " " in parts[1]:
                complex_words.add(parts[0])
        if len(parts) != 16:
            lang_id = parts[0].split("-")
            if lang_id[0] in complex_words:
                continue
            if lang_id[-2:] == ["isv", "src"]:
                forms = " ".join(parts[1].strip().split("|"))
                forms = make_string_standard(forms).split()
                base_form = forms[0]
                if base_form not in pronouns:
                    for form in forms:
                        word_forms[form].append(base_form)



print(make_string_standard("ољењ трамвай чей шар свояченица любит свою яйцекладку. Poględnųti jak to prěkladaje kirilicų v latinicų "))
lem_counter = Counter()
unk_counter = Counter()
i = 0
with open("C:\dev\discord\Medžuslovjanska besěda - Medžuslovjansky - medžuslovjansky [663622843120222229].json", "r") as f:
    for line in f:
        if ":" in line:
            key, _, content = line.strip().partition(":")
            content = content.strip()[1:-2]
            if key == '"content"':
                # print(codecs.decode(content.encode("utf8"))
                # print(content.encode("utf8").decode("unicode-escape"))
                
                # invoke = f'\n\n transliterate("{filtered}", 1, "3", 0, 1)'
                # ad_hoc_string = js_string + invoke
                # result = js2py.eval_js(ad_hoc_string)
                decoded = content.encode("utf8").decode("unicode-escape")
                result = make_string_standard(decoded)
                for word in result.split():
                    if word in word_forms:
                        selected_form = word_forms[word][0]
                        lem_counter.update([selected_form])
                    else: 
                        unk_counter.update([word])

print(len(lem_counter))
print(len(unk_counter))


for word, cnt in unk_counter.most_common(10):
    print(word, cnt, word_forms.get(word))

import pandas as pd
from matplotlib import pyplot as plt

for i, cnt in enumerate([unk_counter, lem_counter]):
    data = cnt.most_common(100)

    df = pd.DataFrame(data)

    df[0] = (1 + pd.Series(range(len(data)))).astype(str) + ". " + df[0]
    df = df.rename(columns={0: 'sloveso', 1: 'čestota'})


    #df['lang'] = df.sloveso.apply(lambda s: 'rus' in s or 'češs' in s or 'pols' in s or 'poljs' in s)

    #print(df[df.lang].head(20))
    #print(df[df.lang])

    df = df.set_index('sloveso')



    fig, ax = plt.subplots(facecolor='white', figsize=(20, 70),)

    df.plot(kind='barh', ax=ax, color='lightslategray', fontsize=20)
    ax.set_clip_on(False)

    plt.savefig(f'tmp_{i}.png')
