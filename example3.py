import pymorphy2
import argparse
from collections import Counter

from constants import VERB_PREFIXES, SIMPLE_DIACR_SUBS, ETM_DIACR_SUBS, DEFAULT_UNITS

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description='Kludge Statistics Example')
    parser.add_argument('path')
    args = parser.parse_args()
    path = args.path

    etm_morph = pymorphy2.MorphAnalyzer(
        path+"out_isv_etm",
        units=DEFAULT_UNITS,
        char_substitutes=ETM_DIACR_SUBS
    )

    text = "Naša misija jest govoriti najvyše råzumlivo, zato dělamo eksperimenty, čęsto pytajemo ljudi i diskutujemo o tom kako ulěpšati naše govorenje. Zato takože čęsto napominamo ljudi, kaki dělajųt pogrěšky, aby govorili drugo. To sųt vsegda sověty a tvoje govorenje to nakraj jest tvoj izbor. My prosto staramo sę byti možlivo najvyše råzumlivi"

    text = "on je pisal, ona je pisala, oni sut pisali. Ja jesm pisavša. Piši i ty, jerbo pisano slovo jest dobro. Generalno pisanje jest dobro"
    print(etm_morph.parse("pisanje"))

    cnt = Counter()
    for word in text.replace(".", "").replace(",", "").split(" "):
        forms = [v.normal_form for v in etm_morph.parse(word)]
        if len(forms) == 0:
            form = word
        else:
            form = forms[0]  # najvyše věrojetna forma podolg spornym hevristikam
        cnt[form] += 1
    print(cnt)

    cnt = Counter()
    for word in text.replace(".", "").replace(",", "").split(" "):
        forms = [v.normal_form for v in etm_morph.parse(word)]
        for form in forms:
            cnt[form] += 1/len(forms)
    print(cnt)

