from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/check',methods=['GET'])
def check():
    return jsonify({'message' : 'api working ....'})

@app.route('/set' ,methods=['POST'])
def set():
    data = request.get_json()
    data = data['data']
    return jsonify({'data' : 'msg received'})

if __name__ == '__main__':
    app.run(debug=True)