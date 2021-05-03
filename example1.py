import pymorphy2
import argparse


NOM_SING_CONVERT = {"femn": "я", "neut": "е", "masc": "й"}
ACC_SING_CONVERT = {"femn": "ю", "neut": "е", "masc": "й"}

def flavorise(word, golden_pos_tag, isv_morph):
    variants = [v for v in isv_morph.parse(word) if golden_pos_tag in v.tag]
    if golden_pos_tag == "VERB":
        # all infinitives?
        if all("infn" in v.tag for v in variants):
            return word[:-1] + "ь"
        # all 3rd person sing?
        if all(("3per" in v.tag and "sing" in v.tag) for v in variants):
            return word + "т"
    if golden_pos_tag == "ADJF":
        some_variant = variants[0]  # no better way to choose
        if some_variant.tag.case == "nomn":
            if "sing" in some_variant.tag:
                return word + NOM_SING_CONVERT[some_variant.tag.gender]
            if "plur" in some_variant.tag:
                return word[:-2] + "ие"
        if some_variant.tag.case == "accs":
            if some_variant.tag.animacy == "anim" and some_variant.tag.gender == "masc":
                return word
            if some_variant.tag.number == "sing":
                return word + ACC_SING_CONVERT[some_variant.tag.gender]
            if some_variant.tag.number == "plur":
                return word[:-2] + "ие"
    return word

def jota_translate(word):
    return word.replace('ју', "ю").replace('ја', "я").replace('јо', "ё").replace('ији', "ии").replace('ј', "й")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description='Kludge Flavorisation Example')
    parser.add_argument('path')
    args = parser.parse_args()

    isv_morph = pymorphy2.MorphAnalyzer(args.path)
        
    text = 'Такоже то може быти помочно за развиту флаворизацију Теоретично тој текст в развитој русској флаворизацији буде изгледати тако'.split()
    tags = 'ADVB NPRO VERB VERB ADJF PREP ADJF NOUN ADVB NPRO NOUN PREP ADJF ADJF NOUN VERB VERB ADVB'.split()
    assert len(text) == len(tags)
    for word, tag in zip(text, tags):
        raw_flavorized = flavorise(word, tag, isv_morph)
        print(jota_translate(raw_flavorized), end=" ")

