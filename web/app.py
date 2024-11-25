
from flask import *

app = Flask(__name__)

@app.route('/about')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
    return render_template("index.html")


if __name__ == '__main__':

  
    app.run(debug=True)