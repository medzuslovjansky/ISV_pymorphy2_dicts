import requests
import shutil
import os
import argparse
from collections import Counter

import pymorphy2
import fitz  # pip install pymupdf

from constants import VERB_PREFIXES, SIMPLE_DIACR_SUBS, ETM_DIACR_SUBS, DEFAULT_UNITS, BASE_ISV_TOKEN_REGEX

def download_file(url):
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

    return local_filename

def iterate_over_text(paragraph):
    delimiters = BASE_ISV_TOKEN_REGEX.finditer(paragraph)
    for delim in delimiters:
        if any(c.isalpha() for c in delim.group()):
            token = delim.group()
            yield token

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
        # path+"out_isv_etm",
        path+"out_isv_lat",
        units=DEFAULT_UNITS,
        # char_substitutes=ETM_DIACR_SUBS
        char_substitutes=SIMPLE_DIACR_SUBS
    )
    cnt = Counter()

    for page in text[1:]:
        for token in iterate_over_text(page):
            if not std_morph.word_is_known(token): 
                razbor = std_morph.parse(token)
                lemma_form = razbor[0].normal_form if razbor else token
                cnt[lemma_form] += 1

    form_data = {}
    for form, count in cnt.items():
        if count > 2:
            form_data[form] = {
                "broj": count,
                "kontekst": list(),
                "formy": dict(),
            }

    for page in text[1:]:
        for paragraph in page.split("\n"):
            for token in iterate_over_text(paragraph):
                razbor = std_morph.parse(token)
                lemma_form = razbor[0].normal_form if razbor else token
                if lemma_form in form_data:
                    form_data[lemma_form]['kontekst'].append(paragraph)
                    form_data[lemma_form]['formy'][token] = [(v.normal_form, v.tag) for v in razbor]

    import pandas as pd
    df = pd.DataFrame(index=form_data.keys(), columns=['broj', 'kontekst', 'formy'])

    print(std_morph.parse("petsto"))
    print(std_morph.parse("sam"))
    print(std_morph.parse("zapad"))
    print(std_morph.word_is_known('zapad')) 
    print(form_data['zapad'])
    print(std_morph.parse("puti"))
    for lemma, data in form_data.items():
        #print()
        #print(lemma)
        #print(data)
        df.loc[lemma, :] = data
    print(df.head())
    print(df.index)
    # df.sort_values(by='broj', ascending=False).to_csv("princ_OOV2.csv", sep=";")
