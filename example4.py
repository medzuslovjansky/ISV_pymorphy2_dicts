import requests
import shutil
import os
import argparse
from collections import Counter

import pymorphy2
import fitz  # this is pymupdf

from constants import VERB_PREFIXES, SIMPLE_DIACR_SUBS, ETM_DIACR_SUBS, DEFAULT_UNITS, BASE_ISV_TOKEN_REGEX

def download_file(url):
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

    return local_filename

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description='Kludge Search Example')
    parser.add_argument('path')
    args = parser.parse_args()
    path = args.path

    if not os.path.isfile("maly_princ_lat.pdf"):
        url = "http://steen.free.fr/interslavic/maly_princ_lat.pdf"
        filename = download_file(url)
    else:
        filename = "maly_princ_lat.pdf"

    with fitz.open(filename) as doc:
        text = []
        for page in doc:
            text += [page.getText()]


    std_morph = pymorphy2.MorphAnalyzer(
        path+"out_isv_lat",
        units=DEFAULT_UNITS,
        char_substitutes=SIMPLE_DIACR_SUBS
    )
    cnt = Counter()

    for page in text[1:]:
        delimiters = BASE_ISV_TOKEN_REGEX.finditer(page)
        for delim in delimiters:
            if any(c.isalpha() for c in delim.group()):
                token = delim.group()
                if not std_morph.word_is_known(token): 
                    cnt[token] += 1
                    razbor = std_morph.parse(token)
                    # print(token, [(f.tag, f.normal_form, f.methods_stack) for f in razbor])
                '''
                razbor = std_morph.parse(token)
                for f in razbor:
                    v_slovniku = (
                        isinstance(m[0], pymorphy2.units.by_lookup.DictionaryAnalyzer)
                        for m in f.methods_stack
                    )
                    if any(v_slovniku):
                        break
                else:
                    print(token, [(f.tag, f.normal_form, f.methods_stack) for f in razbor])
                '''
    print(cnt)


