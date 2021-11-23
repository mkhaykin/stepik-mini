from typing import Optional

import config

import uuid

from flask import Flask
from flask import render_template
from flask import make_response
from flask import request

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY

sessions = dict()


@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')


@app.route('/', methods=['GET', 'POST'])
@app.route('/index.html', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.PORT, debug=True)
    # app.run(host='0.0.0.0', port=port, debug=False)
