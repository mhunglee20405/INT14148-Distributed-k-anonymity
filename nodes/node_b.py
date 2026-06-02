from flask import Flask, jsonify
import pandas as pd
from pathlib import Path

app = Flask(__name__)

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "site_b.csv"


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "node": "Node B",
        "status": "OK"
    })


@app.route("/records", methods=["GET"])
def get_records():
    df = pd.read_csv(DATA_PATH)
    records = df.to_dict(orient="records")

    return jsonify({
        "node": "Node B",
        "record_count": len(records),
        "records": records
    })


if __name__ == "__main__":
    print("Node B is running at http://127.0.0.1:5002")
    app.run(host="127.0.0.1", port=5002, debug=True)