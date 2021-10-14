import argparse
from isv_nlp_utils.constants import BASE_ISV_TOKEN_REGEX, create_analyzers_for_every_alphabet
import ipymarkup   # pip install ipymarkup


def dodavaj_bukvy(word, etm_morph):
    corrected = [f.word for f in etm_morph.parse(word)]
    if len(set(corrected)) == 1:
        return corrected[0]
    if len(set(corrected)) == 0:
        return word + "/?"
    return "/".join(set(corrected))


def spellcheck_text(paragraph, std_morph):
    delimiters = BASE_ISV_TOKEN_REGEX.finditer(paragraph)
    proposed_corrections = []
    for delim in delimiters:
        token = delim.group().lower()
        is_word = any(c.isalpha() for c in delim.group())
        is_known = None
        corrected = None
        confident_correction = None

        if is_word:
            is_known = True
            candidates = set([f.word for f in std_morph.parse(token)])
            if candidates != {token} or not std_morph.word_is_known(token):
                is_known = False
            if len(set(candidates)) >= 1:
                corrected = "/".join(set(candidates))

        markup = "" if is_known or not is_word else "^" * len(token)
        if corrected and corrected != token:
            proposed_corrections.append(corrected)
            confident_correction = corrected
            markup = str(len(proposed_corrections))
        span_data = (delim.start(), delim.end(), markup)
        yield span_data, confident_correction


def perform_spellcheck(text, std_morph):
    data = list(spellcheck_text(text, std_morph))
    spans = [entry[0] for entry in data if entry[0][2]]
    proposed_corrections = [entry[1] for entry in data if entry[1]]
    return text, spans, proposed_corrections


def print_spellcheck(text, std_morph):
    text, spans, proposed_corrections = perform_spellcheck(text, std_morph)
    print("let text = ", text)
    print("")
    print("let spans = ", [list(entry) for entry in spans])
    print("")
    print("let corrections = ", proposed_corrections)
    print("")

    ipymarkup.show_span_ascii_markup(text, spans, width=79)
    print("\n".join([f"{k+1}: {v}" for k, v in enumerate(proposed_corrections)]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Kludge Spellcheck Example')
    parser.add_argument('path')
    args = parser.parse_args()
    path = args.path

    abecedas = create_analyzers_for_every_alphabet(path)
    std_morph = abecedas['lat']
    etm_morph = abecedas['etm']

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

    text = ("Biblioteka pymorphy2 jest napisana za jezyk Python v 2012 letu. "
            "Ona jest ne jedino lemmatizer, napravdu ona jest morfologičny analizator i generator "
            "(to znači že biblioteka uměje razuměti i budovati fleksiju slov). Ona ima poddržku "
            "russkogo jezyka i eksperimentalnu poddržku ukrajinskogo jezyka.")
    print_spellcheck(text, std_morph)
    text = ("Biblioteka pymorphy2 jest napisana za jezyk Python v 2012 letu. "
            "Ona imaje nekoliko osoblivostej, ktore delajut jej ukoristanje za MS mnogo uměstnym.")

    print_spellcheck(text, std_morph)
