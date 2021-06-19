import pymorphy2
import re

VERB_PREFIXES = [
    'do', 'iz', 'izpo', 'nad', 'na', 'ne', 'ob', 'odpo', 'od', 'o', 'prědpo',
    'pod', 'po', 'prě', 'pre', 'pri', 'pro', 'råzpro', 'razpro', 'råz', 'raz',
    'sȯ', 's', 'u', 'vȯ', 'vo', 'v', 'vȯz', 'voz', 'vy', 'za',
]

CYR_LETTER_SUBS = {
    "н": "њ", "л": "љ", "е": "є", "и": "ы"
}

SIMPLE_DIACR_SUBS = {
    'e': 'ě', 'c': 'č', 'z': 'ž', 's': 'š',
}
# NOTE: pymorphy2 cannot work with several changes, i.e. {'e': 'ě', 'e': 'ę'}
ETM_DIACR_SUBS = {
    'a': 'å', 'u': 'ų', 'č': 'ć', 'e': 'ę',
    'n': 'ń', 'r': 'ŕ', 'l': 'ľ',
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

letters = "a-zа-яёěčžšåųćęđŕľńјљєњ"
BASE_ISV_TOKEN_REGEX = re.compile(
    f'''(?:-|[^{letters}\s"'""«»„“-]+|[0-9{letters}_]+(-?[0-9{letters}_]+)*)''',
    re.IGNORECASE | re.UNICODE
)

