from flask import Flask, Blueprint, render_template
from homepage import home
from oahupage import oahu
from kauaipage import kauai
from mauipage import maui
from bigislandpage import bigisland
from aboutpage import about

app = Flask(__name__)

app.register_blueprint(home)
app.register_blueprint(oahu)
app.register_blueprint(kauai)
app.register_blueprint(maui)
app.register_blueprint(bigisland)
app.register_blueprint(about)


if __name__ == '__main__':
    app.run(debug=True)
