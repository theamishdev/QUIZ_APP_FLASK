from flask import Flask
import time
app=Flask(__name__)
@app.route("/io")
def io():
    time.sleep(5)
    return "IO bound task completed"
@app.route("/cpu")
def cpu():
    count=0
    for i in range(10**7):
        count+=1
    return "CPU bound task completed"
if __name__=="__main__":
    app.run(debug=True)
    