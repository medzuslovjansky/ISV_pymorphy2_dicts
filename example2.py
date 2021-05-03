import pymorphy2
import argparse

VERB_PREFIXES = [
    'do', 'iz', 'izpo', 'nad', 'na', 'ne', 'ob', 'odpo', 'od', 'o', 'prědpo',
    'pod', 'po', 'prě', 'pre', 'pri', 'pro', 'råzpro', 'razpro', 'råz', 'raz',
    'sȯ', 's', 'u', 'vȯ', 'vo', 'v', 'vȯz', 'voz', 'vy', 'za',
]

SIMPLE_DIACR_SUBS = {
    'e': 'ě', 'c': 'č', 'z': 'ž', 's': 'š',
}
# NOTE: pymorphy2 cannot work with several changes, i.e. {'e': 'ě', 'e': 'ę'}
ETM_DIACR_SUBS = {
    'a': 'å', 'u': 'ų', 'č': 'ć', 'e': 'ę',
    # 'dž': 'đ' # ne funguje
}

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

def dodavaj_bukvy(word, etm_morph):
    # if "gl" in word:
    #     print(word)
    #     print(etm_morph.parse(word))
    corrected = [f.word for f in etm_morph.parse(word)]
    if len(set(corrected)) == 1:
        return corrected[0]
    if len(set(corrected)) == 0:
        return word + "/?"
    return "/".join(set(corrected))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description='Kludge Spellcheck Example')
    parser.add_argument('path')
    args = parser.parse_args()
    path = args.path

    std_morph = pymorphy2.MorphAnalyzer(
        path+"out_isv_lat",
        units=DEFAULT_UNITS,
        char_substitutes=SIMPLE_DIACR_SUBS
    )

    etm_morph = pymorphy2.MorphAnalyzer(
        path+"out_isv_etm",
        units=DEFAULT_UNITS,
        char_substitutes=ETM_DIACR_SUBS
    )

    text = "ja funguju i razuměju avtododavanje etymologičnyh bukv"

    text_smpl = "hcu preporuciti gledi pese troicky most v gradu celjabinsku zeđam foto za zenu"
    text_stnd = "hču prěporučiti gledi pěše troicky most v gradu čeljabinsku žeđam foto za ženu"
    text_full = "hćų prěporųčiti ględi pěše troicky most v grådu čeljabinsku žeđam foto za ženu"

    # grad: gråd = town // grad = hail

    print()
    for word in text.split(" "):
        print(dodavaj_bukvy(word, etm_morph), end=" ")
    print()
    print()

    fixed_text = " ".join(dodavaj_bukvy(word, std_morph) for word in text_smpl.split(" "))
    print(fixed_text)
    print()
    print(text_stnd)
    print("------")
    fixed_text = " ".join(dodavaj_bukvy(word, etm_morph) for word in text_stnd.split(" "))
    print(fixed_text)
    print()
    print(text_full)
    print()
