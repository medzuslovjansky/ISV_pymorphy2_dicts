import subprocess
from os.path import join, isdir
import shutil
import logging
from collections import Counter

from convert import Dictionary, doubleform_signal


REPEATED_FORMS = Counter()


def log_doubleform(sender, tags_signature):
    REPEATED_FORMS.update({tags_signature: 1})


DIR = "C:\\dev"
DEBUG = True
RUN_EXPORT = False
RUN_CONVERT = False
RUN_BUILD_DICTS = False

if RUN_EXPORT:
    subprocess.check_output(
        ["npm", "run", "generateParadigms"],
        cwd=join(DIR,"interslavic"), shell=True
    )


dictionary_path = join(DIR, "interslavic", "static", "words_forms.txt")
dictionary_out = join(DIR, "pymorphy2-dicts", "out_isv_new.xml")
out_dir = join(DIR, "pymorphy2-dicts", "out_isv")


if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
    doubleform_signal.connect(log_doubleform)

if RUN_CONVERT:
    d = Dictionary(dictionary_path, mapping="mapping_isv.csv")
    d.export_to_xml(join(DIR, "pymorphy2-dicts", "out_isv_new.xml"))

    if DEBUG:
        logging.debug("=" * 50)
        for term, cnt in REPEATED_FORMS.most_common():
            logging.debug(u"%s: %s" % (term, cnt))

if RUN_BUILD_DICTS:
    if isdir(out_dir):
        shutil.rmtree(out_dir)

    subprocess.check_output(
        ["python", "build-dict.py", dictionary_out, out_dir],
        cwd=join(DIR, "pymorphy2-dicts")
    )

import pymorphy2
morph = pymorphy2.MorphAnalyzer(out_dir)
# print(morph.parse("фунгујут"))
print()

from pathlib import Path

DICTS_DIR = join(DIR, "pymorphy2-dicts")

print('suffixes.json')
print(Path(join(out_dir, 'suffixes.json')).stat().st_size)

print('suff.txt')
print(Path(join(DICTS_DIR, 'suff.txt')).stat().st_size)

print('paradigm.txt')
print(Path(join(DICTS_DIR, 'paradigm.txt')).stat().st_size)

phrase = "Тутчас можем писати на прдачном језыковєдском нарєчју"

phrase = "нарєчје јест разумливо приблизно всим машинам без ученја"

phrase = "jа уже виджу нєколико проблемов буду чинити"

phrase = "писанйе jедним столбецем дозволjаjе додати информациjу односно двусмыслности"


phrase = "чи можем ли jа говорити на прдачном језыковєдском нарєчју в тутом каналу буде ли то добро Jесм поправил нєкаке грєшкы од првого раза"
phrase = "понєктори користники сут измыслили нєколико прдачных нарєчиј"

phrase = "мене приjати же тутчас jест канал в ктором jа можем писати на прдачном језыковєдском нарєчју"

phrase = "хм jа трєбују измыслити нєкаку методу работы с заименниками прємного опциj анализа имаjут оне"

phrase = "Мой изкус односно фунгованйа всакоможных заименников чи имайут ли премного формов они и оне"

for i, word in enumerate(phrase.replace("й", "j").replace("j", "ј").split(" ")):

    parsings = morph.parse(word)
    desc = " | ".join(f"**{parsing.normal_form}** - {parsing.tag}" for parsing in parsings)
    if i % 2 == 0:
        desc = "> " + desc
    print(desc)
    # print(len(morph.parse(word)))
    # print(morph.parse(word)[0])
