import flask
from flask import request, Response
import subprocess

app = flask.Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "PBDA Flask APIs"

@app.route('/api/v1/train', methods=['POST'])
def train():
    dat_file = "data/"+request.args['data']
    proc = f"python src/training.py --data_path {dat_file} --model_path models/ --f1_criteria 0.6"
    subprocess.Popen(proc, shell=True)
    return Response(status=204)

@app.route('/api/v1/process', methods=['POST'])
def data_process():
    dat_file = "data/"+request.args['data']
    proc = f"python src/data_processor.py --data_path {dat_file}"
    subprocess.Popen(proc, shell=True)
    return Response(status=204)

if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True)