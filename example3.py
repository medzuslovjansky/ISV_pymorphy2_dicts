import pymorphy2
import argparse
from collections import Counter

VERB_PREFIXES = [
    'do', 'iz', 'izpo', 'nad', 'na', 'ne', 'ob', 'odpo', 'od', 'o', 'prědpo',
    'pod', 'po', 'prě', 'pre', 'pri', 'pro', 'råzpro', 'razpro', 'råz', 'raz',
    'sȯ', 's', 'u', 'vȯ', 'vo', 'v', 'vȯz', 'voz', 'vy', 'za',
]

DEFAULT_UNITS = [
    [
        pymorphy2.units.DictionaryAnalyzer()
    ],
    pymorphy2.units.KnownPrefixAnalyzer(known_prefixes=VERB_PREFIXES),
    [
        pymorphy2.units.UnknownPrefixAnalyzer(),
        pymorphy2.units.KnownSuffixAnalyzer()
    ]
]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description='Kludge Statistics Example')
    parser.add_argument('path')
    args = parser.parse_args()
    path = args.path

    etm_morph = pymorphy2.MorphAnalyzer(
        path+"out_isv_etm",
        units=DEFAULT_UNITS,
        char_substitutes={}
    )

    text = "Naša misija jest govoriti najvyše råzumlivo, zato dělamo eksperimenty, čęsto pytajemo ljudi i diskutujemo o tom kako ulěpšati naše govorenje. Zato takože čęsto napominamo ljudi, kaki dělajųt pogrěšky, aby govorili drugo. To sųt vsegda sověty a tvoje govorenje to nakraj jest tvoj izbor. My prosto staramo sę byti možlivo najvyše råzumlivi"

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

