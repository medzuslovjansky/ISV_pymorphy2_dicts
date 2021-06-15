import argparse
from flask import Flask, render_template, request, jsonify
from example2 import perform_spellcheck, pymorphy2
from constants import DEFAULT_UNITS, SIMPLE_DIACR_SUBS, ETM_DIACR_SUBS, CYR_LETTER_SUBS

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

path = "C:\\dev\\pymorphy2-dicts\\"

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

cyr_morph = pymorphy2.MorphAnalyzer(
    path+"out_isv_cyr",
    units=DEFAULT_UNITS,
    char_substitutes=CYR_LETTER_SUBS
)

abecedas = {"lat": std_morph, "etm": etm_morph, "cyr": cyr_morph}
    
@app.route('/')
def index():
    return render_template('main.html')

@app.route('/koriguj', methods=['POST'])
def korigovanje():
    text = request.json['text'];
    selected_morph = abecedas[request.json["abeceda"]]
    text, spans, proposed_corrections = perform_spellcheck(text, selected_morph)

    resp = {
        'text': text,
        'spans': spans,
        'corrections': proposed_corrections
    }
    return jsonify(resp)
 
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
           '--port', type=int, default=666,
           help='The port to listen on (defaults to 666).')
    args = parser.parse_args()
    app.run(host='localhost', port=args.port, debug=True)

