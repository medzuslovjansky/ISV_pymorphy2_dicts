import unicodedata
from string import whitespace
from collections import Counter, defaultdict

import js2py
import re


    

# last one: lat x to cyr х 

diacr_letters = "žčšěйćżęų" 
plain_letters = "жчшєjчжеу"


lat_alphabet = "abcčdeěfghijjklmnoprsštuvyzž"
cyr_alphabet = "абцчдеєфгхийьклмнопрсштувызж"


save_diacrits = str.maketrans(diacr_letters, plain_letters)
cyr2lat = str.maketrans(cyr_alphabet, lat_alphabet)

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


def preprocess_preacc():
    flags_dict = {
        "STEM": "S",
        "VERB": "V",
        "VERB2STEM": "Z",
        "EXCEPTION_STEM": "E",
        "VERB_ASPECT": "A",
        "VP": "P",
    }
    lines = []
    with open("hunspell.preaff", "r") as f:
        for line in f:
            data, _, comment = line.partition("#")
            #if "<" in line or "#" in line:
            #    print(data, comment)
            if data.strip():
                processed = data.strip().format(**flags_dict)
                if "<" in line:
                    print(processed)
                    print([data, comment, line])

                lines.append(processed)
    with open("./hunspell_data/ISV.aff", "w") as f_out:
        for data in lines:
            f_out.write(data + "\n")
            
    lines = []
    with open("hunspell.predic", "r") as f:
        for line in f:
            data, _, comment = line.partition("#")
            if data.strip():
                lines.append(data.strip().format(**flags_dict))
    with open("./hunspell_data/ISV.dic", "w") as f_out:
        for data in lines:
            f_out.write(data + "\n")


preprocess_preacc()

from hunspell import Hunspell
h = Hunspell('ISV', hunspell_data_dir='./hunspell_data')


with open("učenje - fraznik [706531244871123045].json", "r") as f:
    for line in f:
        if ":" in line:
            key, _, content = line.strip().partition(":")
            content = content.strip()[1:-2]
            if key == '"content"':

                decoded = content.encode("utf8").decode("unicode-escape")
                result = make_string_standard(decoded)
                for word in result.split():
                    if False and h.stem(word):
                        print(word)
                        print(h.stem(word))
                        print(h.analyze(word))


for word in [
    "znaju", "Blagodarjų", "Blagodari", 'razuměm', 'razuměj', 
    'Govoriš', 'zovem', 'nazovemo', 'prězovut', 'zvati', 'sravnivaju',
    'pozovu', 'nedozovu', 'pozvati', 'prospati', 'spiš', 'prospiš', 'spi', 'spimo', 'spiu'
]:
    # print(word)
    # print(h.analyze(word))
    print(make_string_standard(word))
    print(h.analyze(make_string_standard(word)))
    #print(h.spell(make_string_standard(word)))
    #print(h.suggest(make_string_standard(word)))
    #print(h.suffix_suggest(make_string_standard(word)))
    # print(h.stem(make_string_standard(word)))
