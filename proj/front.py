from flask import Flask, render_template

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def ask():
    return render_template('ask.html')

@app.route('/results',methods=['GET', 'POST'])
def results():
    return render_template('results.html')

if __name__ == '__main__':
    app.run(debug=True,port=8000)
