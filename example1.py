import pymorphy2
import argparse

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

def flavorise(word, golden_pos_tag, isv_morph, flavor):
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

    if golden_pos_tag == "VERB" and all(v.tag.person == "1per" for v in variants):
        tags = variants[0].tag.grammemes  # no better way to choose
        new_tags = set(tags) - {'alt-m'} | {'alt-u'}
        # TODO XXX NE FUNGUJE
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
            suffix, addition = transform
            return word[:suffix] + addition

    return word

# no j/й/ь support
lat_alphabet = "abcčdeěfghijklmnoprsštuvyzžęųćå"
cyr_alphabet = "абцчдеєфгхијклмнопрсштувызжяуча"
lat2cyr_trans = str.maketrans(lat_alphabet, cyr_alphabet)
pol_alphabet = "abcčdeěfghijklmnoprsštuwyzżęąco"
lat2pol_trans = str.maketrans(lat_alphabet, pol_alphabet)

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

def rus_letter_change(word):
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

    isv_morph = pymorphy2.MorphAnalyzer(args.path, units=DEFAULT_UNITS)

    if False:
        text = 'Такоже то може быти помочно за развиту флаворизацију Теоретично тој текст в развитој русској флаворизацији буде изгледати тако'.split(" ")
        tags = 'ADVB NPRO VERB VERB ADJF PREP ADJF NOUN ADVB NPRO NOUN PREP ADJF ADJF NOUN VERB VERB ADVB'.split(" ")
        assert len(text) == len(tags)
        for word, tag in zip(text, tags):
            raw_flavorized = flavorise(word, tag, isv_morph, RU_FLAVOR)
            print(rus_letter_change(raw_flavorized), end=" ")
        # will print:
        # Такоже то может быть помочное за развитую флаворизацию Теоретично той текст в развитой русской флаворизации будет изгледать тако 

    text = 'myslim že to bųde pomoćno za råzvitų flavorizacijų . Toj tekst v råzvitoj {LANG} flavorizaciji bųde izględati tako . Take prěměny mogųt pomagati v učenju i råzuměnju medžuslovjanskogo języka i drugyh slovjanskyh językov . Takože to jest važny krok v tvorjenju mehanizma avtomatičnogo prěklada .'.split(" ")

    tags = ('VERB CONJ NPRO VERB ADVB PREP ADJF NOUN PNCT ' 
            'NPRO NOUN PREP ADJF ADJF NOUN VERB VERB ADVB PNCT '
            'ADJF NOUN VERB VERB PREP NOUN CONJ NOUN ADJF NOUN CONJ ADJF ADJF NOUN PNCT '
            'ADVB NPRO VERB ADJF NOUN PREP NOUN NOUN ADJF NOUN PNCT '
            ).split()
    assert len(text) == len(tags)
    print("ЖРЛО")
    print("> " + " ".join(text))
    print()
    print("РЕЗУЛТАТ (русскы)")
    print(">", end=" ")
    for word, tag in zip(text, tags):
        if word == "{LANG}": word = "russkoj"
        raw_flavorized = flavorise(word, tag, isv_morph, RU_FLAVOR)
        print(rus_letter_change(raw_flavorized), end=" ")
    print()
    print("РЕЗУЛТАТ (польскы)")
    print(">", end=" ")
    for word, tag in zip(text, tags):
        if word == "{LANG}": word = "poljskoj"
        raw_flavorized = flavorise(word, tag, isv_morph, PL_FLAVOR)
        print(pol_letter_change(raw_flavorized), end=" ")
    print()

    if False:
        variants = [v for v in isv_morph.parse("razvitoj") if "ADJF" in v.tag]
        print("\n".join(str(v) for v in variants))

        print()
        variants = [v for v in isv_morph.parse("flavorizacijų") if "NOUN" in v.tag]
        print("\n".join(str(v) for v in variants))

        print()
        variants = [v for v in isv_morph.parse("take")]
        print("\n".join(str(v) for v in variants))
