import pymorphy2
import argparse
from isv_nlp_utils.constants import DEFAULT_UNITS

from isv_nlp_utils.flavorizacija import (
    CS_FLAVOR, PL_FLAVOR, RU_FLAVOR, SR_FLAVOR,
    rus_letter_change, pol_letter_change, cz_letter_change, srb_letter_change
)
import os


def flavorise(word, golden_pos_tag, isv_morph, flavor, ju):
    if golden_pos_tag == "PNCT":
        return word
    if golden_pos_tag == "ADVB":
        variants = [
            v for v in isv_morph.parse(word)
            if v.tag.POS == "ADJF"
            and v.tag.number == "sing" and v.tag.gender == "neut" and v.tag.case == "nomn"
        ]
        if not variants:
            return word
    else:
        variants = [v for v in isv_morph.parse(word) if golden_pos_tag in v.tag]

    if not variants:
        return word

    if ju:
        if golden_pos_tag == "VERB" and all(v.tag.person == "1per" for v in variants):
            tags = variants[0].tag.grammemes  # no better way to choose
            new_tags = set(tags) - {'alt-m'} | {'alt-u'}
            word = isv_morph.parse(word)[0].inflect(new_tags).word

    if golden_pos_tag == "ADJF":
        variants = [variants[0]]  # no better way to choose

    flavor_rules = flavor.get(golden_pos_tag, {})
    if golden_pos_tag == "ADVB":
        flavor_rules = {"ADJF": flavor_rules.get('ADVB', (None, ''))}

    for condition_plus, transform in flavor_rules.items():
        conditions_arr = condition_plus.split("+")
        is_match = all(
            all(cond in v.tag for cond in conditions_arr)
            for v in variants
        )
        if is_match:
            if isinstance(transform, tuple):
                suffix, addition = transform
                return word[:suffix] + addition
            if isinstance(transform, dict):
                for base, replacement in transform.items():
                    if word[-len(base):] == base:
                        return word[:-len(base)] + replacement

    return word


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Kludge Flavorisation Example'
    )
    parser.add_argument('path')
    args = parser.parse_args()

    isv_morph = pymorphy2.MorphAnalyzer(os.path.join(args.path, "out_isv_etm"), units=DEFAULT_UNITS)

    text = ('myslim že to bųde pomoćno za råzvitų flavorizacijų . '
            'Toj tekst v råzvitoj {LANG} flavorizaciji bųde izględati tako . '
            'Take prěměny mogųt pomagati v učeńju i råzuměńju medžuslovjańskogo języka i drugyh slovjańskyh językov . '
            'Takože to jest važny krok v tvorjeńju mehanizma avtomatičnogo prěklada .'
            ).split(" ")

    tags = ('VERB CONJ NPRO VERB ADVB PREP ADJF NOUN PNCT '
            'NPRO NOUN PREP ADJF ADJF NOUN VERB VERB ADVB PNCT '
            'ADJF NOUN VERB VERB PREP NOUN CONJ NOUN ADJF NOUN CONJ ADJF ADJF NOUN PNCT '
            'ADVB NPRO VERB ADJF NOUN PREP NOUN NOUN ADJF NOUN PNCT '
            ).split()
    assert len(text) == len(tags)
    print("ЖРЛО")
    print("> " + " ".join(text))
    print()
    ALL_LANG_DATA = [
            {'nomn': 'русскы', 'loct': 'russkoj', 'flavor': RU_FLAVOR, 'letter_change': rus_letter_change, 'ju': True},
            {'nomn': 'пољскы', 'loct': 'poljskoj', 'flavor': PL_FLAVOR, 'letter_change': pol_letter_change, 'ju': True},
            {'nomn': 'чешскы', 'loct': 'češskoj', 'flavor': CS_FLAVOR, 'letter_change': cz_letter_change, 'ju': False},
            {'nomn': 'србскы', 'loct': 'srbskoj', 'flavor': SR_FLAVOR, 'letter_change': srb_letter_change, 'ju': False},
    ]
    for lang_data in ALL_LANG_DATA:
        print(f"РЕЗУЛТАТ ({lang_data['nomn']})")
        print(">", end=" ")
        for word, tag in zip(text, tags):
            if word == "{LANG}":
                word = lang_data['loct']
            raw_flavorized = flavorise(word, tag, isv_morph, lang_data['flavor'], lang_data['ju'])
            func = lang_data['letter_change']
            print(func(raw_flavorized), end=" ")
        print()

    variants = [v for v in isv_morph.parse("idti")]
    print("\n".join(str(v) for v in variants))

    if False:
        variants = [v for v in isv_morph.parse("razvitoj") if "ADJF" in v.tag]
        print("\n".join(str(v) for v in variants))

        print()
        variants = [v for v in isv_morph.parse("flavorizacijų") if "NOUN" in v.tag]
        print("\n".join(str(v) for v in variants))

        print()
        variants = [v for v in isv_morph.parse("take")]
        print("\n".join(str(v) for v in variants))
