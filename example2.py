import pymorphy2
import argparse
from constants import VERB_PREFIXES, SIMPLE_DIACR_SUBS, ETM_DIACR_SUBS, DEFAULT_UNITS


def dodavaj_bukvy(word, etm_morph):
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

    text_smpl = "po mojemu mnenju hcu preporuciti gledi pese troicky most v gradu celjabinsku zeđam foto za zenu"
    text_stnd = "po mojemu mněnju hču prěporučiti gledi pěše troicky most v gradu čeljabinsku žeđam foto za ženu"
    text_full = "po mojemu mněńju hćų prěporųčiti ględi pěše troicky most v grådu čeljabinsku žeđam foto za ženu"

    # grad: gråd = town // grad = hail

    print()
    for word in text.split(" "):
        print(dodavaj_bukvy(word, etm_morph), end=" ")
    print()
    print()

    print(text_smpl)
    fixed_text = " ".join(dodavaj_bukvy(word, std_morph) for word in text_smpl.split(" "))
    print("=== ADD SIMPLE DIACRITICS ===")
    print(fixed_text)
    print()
    print(text_stnd)
    print("=== ADD ETYMOLOGICAL DIACRITICS ===")
    fixed_text = " ".join(dodavaj_bukvy(word, etm_morph) for word in text_stnd.split(" "))
    print(fixed_text)
    print()
    print("=== GROUND TRUTH ===")
    print(text_full)
    print()
