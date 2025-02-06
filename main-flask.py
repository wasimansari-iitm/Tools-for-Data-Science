from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

# Load data from the CSV file
df = pd.read_csv('q-fastapi.csv')

@app.route('/api', methods=['GET'])
def read_students():
    classes = request.args.getlist('class')

    if classes:
        # Filter the DataFrame based on the classes specified in the query parameter
        filtered_df = df[df['class'].isin(classes)]
    else:
        filtered_df = df

    # Sort the filtered DataFrame by studentId
    filtered_df = filtered_df.sort_values(by='studentId')

    # Convert filtered DataFrame to a list of dictionaries
    students = filtered_df.to_dict(orient='records')

    # Create the response ensuring studentId comes first
    response = {
        "students": []
    }

    for student in students:
        response["students"].append({
            "studentId": student["studentId"],  # studentId first
            "class": student["class"]            # class second
        })

    # Print for debugging purposes
    print("Response before sending:", response)

    return jsonify(response)

@app.errorhandler(404)
def not_found(e):
    return jsonify(error=str(e)), 404

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)
