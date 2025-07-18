from flask import Flask, render_template, request
import pandas as pd
from random import choice
import os
import random
import re

app = Flask(__name__)

# excel taulukon lukeminen ja numeron muutos merkkijonoksi
dataframe = pd.read_excel(
    "alkon-hinnasto-tekstitiedostona.xlsx",
    usecols=["Numero", "Nimi", "Hinta", "Tyyppi", "Alkoholi-%", "Pullokoko"],
    header=3,
    dtype={"Numero": str}
)

# tilavuuden muutos
def parse_litrat(s):
    if not isinstance(s, str):
        s = str(s)
    s = s.lower().replace(",", ".").strip()
    match = re.search(r"\d+(\.\d+)?", s)
    if match:
        return float(match.group())
    else:
        return 0.0

# pullokoon muutos käyttäen parse_litrat
dataframe["Pullokoko_l"] = dataframe["Pullokoko"].apply(parse_litrat)

# etusivu
@app.route('/')
def index():
    kategoriat = [
        "punaviinit",
        "roseeviinit",
        "valkoviinit",
        "kuohuviinit ja samppanjat",
        "jälkiruokaviinit, väkevöidyt ja muut viinit",
        "viinijuomat",
        "hanapakkaukset",
        "oluet",
        "siiderit",
        "juomasekoitukset",
        "vodkat ja viinat",
        "ginit ja muut viinat",
        "rommit",
        "konjakit",
        "brandyt, armanjakit ja calvadosit",
        "viskit",
        "liköörit ja katkerot",
        "alkoholittomat"
    ]
    return render_template("index.html", kategoriat=kategoriat)

# arvonta sivu
@app.route('/arvonta')
def arvonta():
    kategoria = request.args.get("kategoria", "").lower()
    nimi = choice(["Henri", "Roope", "Ose"])

    suodatetut = dataframe[
        (dataframe["Tyyppi"].str.lower().str.contains(kategoria)) &
        (dataframe["Hinta"] < 15)
    ]

    if suodatetut.empty:
        return "Ei löytynyt tuotteita valitulla kategorialla."

    # valitaan yksi
    rivi = suodatetut.sample(n=1).iloc[0]

    # tuotteen linkitys
    numero = str(rivi["Numero"])
    linkki = f"https://www.alko.fi/tuotteet/{numero}/"

    # kisu kuva
    polku = os.path.join(app.static_folder, "kissakuvat")
    files = os.listdir(polku)
    random_image = random.choice(files)

    return render_template(
        "arvonta.html",
        nimi=nimi,
        tuote_nimi=rivi["Nimi"],
        hinta=rivi["Hinta"],
        tyyppi=rivi["Tyyppi"],
        alkoholi=rivi["Alkoholi-%"],
        pullokoko=rivi["Pullokoko_l"],
        linkki=linkki,
        random_image=random_image,
    )


if __name__ == '__main__':
    app.run(debug=True, port=8000)
