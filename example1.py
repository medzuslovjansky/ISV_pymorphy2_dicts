import pymorphy2
import argparse
from constants import VERB_PREFIXES, SIMPLE_DIACR_SUBS, ETM_DIACR_SUBS, DEFAULT_UNITS
import os

CS_FLAVOR = {
    "VERB":
    {
        "infn": (-2, 't'),
        # "1per+sing": (-1, 'u'),
        "2per+sing": {'aješ': 'áš', 'iš': 'íš'},
        "3per+sing": {'aje': 'á', 'i': 'í'},
        "1per+plur": {'ajemo': 'áme', 'imo': 'íme'},
        "2per+plur": {'ajete': 'áte', 'ite': 'íte'},
        "3per+plur": {'jųt': 'jí', 'ųt': 'ou', 'ęt': "í"},
    },
    "NOUN":
    {
        "gent+sing+masc": (-1, "e"),
        "accs+sing+masc": (-1, "e"),
        "gent+plur+masc": (-2, "ů"),
        "datv+plur+masc": (-2, "ům"),
        "accs+plur+masc": (-2, "e"),
        "loct+plur+masc": (-2, "ech"),
        "ablt+sing+femn": (-3, "ou"),
        "datv+plur+femn": (-2, "ám"),
        "ablt+sing+neut": (-2, "em"),
        "datv+plur+neut": (-2, "ům"),
        "loct+plur+neut": (-2, "ech")
    },
    "ADVB": {"ADVB": (-1, 'ě')},
    "ADJF":
    {
        "nomn+plur+femn": (-1, "é"),
        "accs+plur+femn": (-1, "é"),
        "nomn+sing+neut": (-1, "é"),
        "accs+sing+neut": (-1, "é"),
        "nomn+plur+neut": (-1, "á"),
        "accs+plur+neut": (-1, "á"),

        "accs+sing+femn": (-1, "ou"),
        "ablt+sing+femn": (-1, "ou"),
        "loct+sing+masc": (-2, "ém"),
        "loct+sing+neut": (-2, "ém"),
        "loct+sing+femn": (-2, "é"),
        "datv+sing+femn": (-2, "é"),
        "gent+sing+femn": (-2, "é"),

        "accs+plur+masc": (-2, "é"),
        "loct+plur": (-2, "ých"),
        "datv+plur": (-2, "ých"),
        "ablt+plur": (-3, "ými"),
    }
}


PL_FLAVOR = {
    "VERB": 
    {
        "infn": (-2, 'Ч'),
        "1per+sing": (-1, 'ę'),
        "3per+plur": (-2, 'ą'),
        "3per+plur": (-2, 'ą'),
    },
    "NOUN":
    {
        "loct+sing+masc": (-1, "ě"),
        "accs+sing+femn": (-1, "ę"),
    },
    "ADVB": {"ADVB": (-1, 'e')},
    "ADJF":
    {
        "nomn+plur+femn": (-1, "ie"),
        "accs+plur+femn": (-1, "ie"),
        "nomn+plur+neut": (-1, "ie"),
        "accs+plur+neut": (-1, "ie"),

        "accs+sing+femn": (-1, "ą"),
        "ablt+sing+femn": (-1, "ą"),

        "loct+sing+femn": (-2, "ej"),
        "datv+sing+femn": (-2, "ej"),
        "gent+sing+femn": (-2, "ej"),

        "accs+plur+masc": (-2, "ych"),
        "loct+plur": (-2, "ych"),
        "datv+plur": (-2, "ych"),
    }
}


SR_FLAVOR = {
    "VERB": 
    {
    },
    "NOUN":
    {
        "nomn+plur+masc": (-1, "ovi"),
        "gent+plur+masc": (None, "a"),
        # TODO: https://fastlanguagemastery.com/learn-foreign-languages/serbian-language/serbian-cases-of-nouns/
    },
    "ADJF":
    {

        "nomn+sing+masc": {"ny": "an"},
        "gent+sing+masc": (-1, ""),
        "accs+sing+masc+anim": (-1, ""),
        "datv+sing+masc": (-1, ""),
        "loct+sing+masc": (-1, ""),

        "gent+sing+femn": (-2, "e"),
        "ablt+sing+femn": (-2, "om"),

        "loct+plur": (-2, "im"),
        "ablt+plur": (-3, "im"),
    }
}



RU_FLAVOR = {
    "VERB": 
    {
        "infn": (-1, 'ь'),
        "3per+sing": (None, 't'),
    },
    "NOUN":
    {
        "loct+sing+masc": (-1, "ě"),
    },
    "ADJF":
    {
        "nomn+sing+femn": (None, "ja"),
        "nomn+sing+neut": (None, "ě"),
        "nomn+sing+masc": (None, "j"),

        "accs+sing+femn": (None, "ju"),
        "accs+sing+neut": (None, "ě"),
        "accs+sing+masc+anim": (None, ""),
        "accs+sing+masc+inan": (None, "j"),

        # "accs+plur": (None, "iě"),
        "nomn+plur": (-1, "ые"),
        "accs+plur+neut": (-1, "ые"),
        # "accs+plur+femn+anim": (-1, "ых"),
        # "accs+plur+femn+inan": (-1, "ые"),
        # "accs+plur+masc+anim": (-1, "ых"),
        # "accs+plur+masc+inan": (-1, "ые"),
    }
}

def flavorise(word, golden_pos_tag, isv_morph, flavor, ju):
    if golden_pos_tag == "PNCT":
        return word
    if golden_pos_tag == "ADVB":
        variants = [v for v in isv_morph.parse(word)
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

# no j/й/ь support
lat_alphabet = "abcčdeěfghijklmnoprsštuvyzžęųćåńľŕ"
cyr_alphabet = "абцчдеєфгхијклмнопрсштувызжяучанлр"
lat2cyr_trans = str.maketrans(lat_alphabet, cyr_alphabet)
pol_alphabet = "abcčdeěfghijklmnoprsštuwyzżęąconlr"
lat2pol_trans = str.maketrans(lat_alphabet, pol_alphabet)

def srb_letter_change(word):
    word = word.replace('ć', "ћ").replace('dž', "ђ").replace("ę", "е")
    word = word.translate(lat2cyr_trans)

    return word.replace('ы', "и").replace('нј', "њ").replace('лј', "љ")

def pol_letter_change(word):
    word = word.translate(lat2pol_trans)
    return (word.replace('č', "cz").replace('š', "sz")
            .replace('rj', "rz").replace('rě', "rze").replace('ri', "rzy")
            .replace('ě', "ie")
            .replace('Ч', "ć")
            .replace('lj', "л").replace('l', "ł").replace("л", "l").replace('łę', "lę")
            .replace('nj', "ni").replace('wj', "wi")
            .replace('ci', "cy")
            .replace('ji', "i")
            .replace('dż', "dz")
    )

def cz_letter_change(word):
    return (word.replace('ę', "ě")
            .replace('ų', "u")
            .replace('šč', "št")
            .replace('rje', "ří")
            .replace('rj', "ř")
            .replace('rě', "ře")
            .replace('ri', "ři")
            .replace('đ', "z")
            .replace('å', "a")
            .replace('h', "ch")
            .replace('g', "h")
            .replace('ć', "c")
            .replace('kě', "ce")
            .replace('gě', "ze")
            .replace('lě', "le")
            .replace('sě', "se")
            .replace('hě', "še")
            .replace('cě', "ce")
            .replace('zě', "ze")
            .replace('nju', "ni")
            .replace('nj', "ň")
            .replace('tje', "tí")
            .replace('dje', "dí")
            .replace('lju', "li")
            .replace('ču', "či")
            .replace('cu', "ci")
            .replace('žu', "ži")
            .replace('šu', "ši")
            .replace('řu', "ři")
            .replace('zu', "zi")
            .replace('ijejų', "í")
            .replace('ija', "e")
            .replace('ijų', "i")
            .replace('ij', "í")
    )

def rus_letter_change(word):
    word = word.replace("ń", "нь").replace("ľ", "ль")
    word = word.translate(lat2cyr_trans)
    return (word.replace('ју', "ю").replace('ја', "я").replace('јо', "ё")
            .replace('ији', "ии")
            .replace('рј', "рь").replace('лј', "ль").replace('нј', "нь")
            .replace('ј', "й")
            .replace('йя', "я").replace('йе', "е")
            .replace('ья', "я").replace('ье', "е")
            .replace('дж', "жд")
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description='Kludge Flavorisation Example')
    parser.add_argument('path')
    args = parser.parse_args()

    isv_morph = pymorphy2.MorphAnalyzer(os.path.join(args.path, "out_isv_etm"), units=DEFAULT_UNITS)

    text = 'myslim že to bųde pomoćno za råzvitų flavorizacijų . Toj tekst v råzvitoj {LANG} flavorizaciji bųde izględati tako . Take prěměny mogųt pomagati v učeńju i råzuměńju medžuslovjańskogo języka i drugyh slovjańskyh językov . Takože to jest važny krok v tvorjeńju mehanizma avtomatičnogo prěklada .'.split(" ")

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
            {'nomn': 'польскы', 'loct': 'poljskoj', 'flavor': PL_FLAVOR, 'letter_change': pol_letter_change, 'ju': True},
            {'nomn': 'чешскы', 'loct': 'češskoj', 'flavor': CS_FLAVOR, 'letter_change': cz_letter_change, 'ju': False},
            {'nomn': 'србскы', 'loct': 'srbskoj', 'flavor': SR_FLAVOR, 'letter_change': srb_letter_change, 'ju': False},
    ]
    for lang_data in ALL_LANG_DATA:
        print(f"РЕЗУЛТАТ ({lang_data['nomn']})")
        print(">", end=" ")
        for word, tag in zip(text, tags):
            if word == "{LANG}": word = lang_data['loct']
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
