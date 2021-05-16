import pymorphy2
import argparse
from constants import VERB_PREFIXES, SIMPLE_DIACR_SUBS, ETM_DIACR_SUBS, DEFAULT_UNITS, BASE_ISV_TOKEN_REGEX
import ipymarkup   # pip install ipymarkup


def dodavaj_bukvy(word, etm_morph):
    corrected = [f.word for f in etm_morph.parse(word)]
    if len(set(corrected)) == 1:
        return corrected[0]
    if len(set(corrected)) == 0:
        return word + "/?"
    return "/".join(set(corrected))


def spellcheck_text(paragraph, strict_std_morph, std_morph):
    delimiters = BASE_ISV_TOKEN_REGEX.finditer(paragraph)
    proposed_corrections = []
    for delim in delimiters:
        token = delim.group().lower()
        is_word = any(c.isalpha() for c in delim.group())
        is_known = None
        corrected = None
        confident_correction = None

        if is_word:
            is_known = strict_std_morph.word_is_known(token)
            candidates = [f.word for f in std_morph.parse(token)]
            print(token, candidates)
            if len(set(candidates)) >= 1:
                corrected = "/".join(set(candidates))

        markup = "" if is_known or not is_word else "^" * len(token)
        if corrected and corrected != token:
            proposed_corrections.append(corrected)
            confident_correction = corrected
            markup = str(len(proposed_corrections))
        span_data = (delim.start(), delim.end(), markup)
        yield span_data, confident_correction



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


    strict_std_morph = pymorphy2.MorphAnalyzer(
        path+"out_isv_lat",
        units=DEFAULT_UNITS,
        char_substitutes={}
    )

    text = "Biblioteka pymorphy2 jest napisana za jezyk Python v 2012 letu. Ona jest ne jedino lemmatizer, napravdu ona jest morfologičny analizator i generator (to znači že biblioteka uměje razuměti i budovati fleksiju slov). Ona ima poddržku russkogo jezyka i eksperimentalnu poddržku ukrajinskogo jezyka."
    print()
    data = list(spellcheck_text(text, strict_std_morph, std_morph))
    print(data)
    print()
    spans = [entry[0] for entry in data if entry[0][2]]
    proposed_corrections = [entry[1] for entry in data if entry[1]]
    ipymarkup.show_span_ascii_markup(text, spans, width=79)
    print("\n".join([f"{k+1}: {v}" for k, v in enumerate(proposed_corrections)]))

