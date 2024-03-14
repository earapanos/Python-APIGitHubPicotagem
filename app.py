from flask import Flask, jsonify
from automation import AutomacaoLocates

app = Flask(__name__)
automation = AutomacaoLocates()

@app.route('/start_automation', methods=['GET'])
def start_automation():
    automation.run()
    return jsonify({"message": "Automation started successfully"})

if __name__ == '__main__':
    app.run(debug=True)
