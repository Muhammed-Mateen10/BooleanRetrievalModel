from flask import Flask, render_template, request
from BoolenRetrievalModel import BooleanRetrievalModel
app = Flask(__name__)

BRM = BooleanRetrievalModel()

@app.route("/")
def hello():
  return render_template('home.html')

# @app.route("/search")
# def 

@app.route("/help")
def help():
  return render_template("help.html")

@app.route("/search" , methods= ["GET" , "POST"])
def gfg():
  if request.method == 'POST':
    input = request.form.get("Query")
    matchedDocs = BRM.Query(input)
    return render_template("search.html" , input = input , result = matchedDocs)




if __name__ == "__main__":
  app.run()