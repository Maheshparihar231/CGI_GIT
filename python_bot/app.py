from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/check',methods=['GET'])
def check():
    return jsonify({'message' : 'api working ....'})


# if __name__ == '__main__':
#     app.run(debug=True)



