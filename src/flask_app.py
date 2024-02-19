from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

dataset_path = os.getcwd() + '\\dataset\\dataset_prepared.csv'
dataset = pd.read_csv(dataset_path)

keys = ['PUBUKPRN', 'UKPRN', 'KISCOURSEID', 'KISMODE', 'EMPPOP',
        'EMPRESPONSE', 'EMPSAMPLE', 'EMPRESP_RATE', 'WORKSTUDY', 
        'STUDY', 'UNEMP', 'PREVWORKSTUD', 'BOTH', 'NOAVAIL', 'WORK']


@app.route('/get_all_data', methods=['GET'])
def get_data():
    global dataset
    return jsonify(dataset.to_dict(orient='records'))


@app.route('/post_new_data', methods=['POST'])
def post_data():
    global dataset
    try:
        new_data = request.get_json()

        if not all(key in new_data for key in keys):
            return jsonify({'error': 'Missing keys in the new data record'}), 400

        new_data_record = pd.DataFrame([new_data])
        dataset = pd.concat([dataset, new_data_record], ignore_index=True)
        dataset.to_csv(dataset_path, index=False)

        return jsonify({'message': 'New data record added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/update_data/<target_key>-<target_record_key>', methods=['PUT'])
def update_data(target_key, target_record_key):
    global dataset

    target_record_key = int(target_record_key)
    try:
        if dataset[target_key].isin([target_record_key]).any():
            updated_data = request.get_json()
        
            if not all(key in updated_data for key in keys):
                return jsonify({'error': 'Missing keys in the new data record'}), 400

            new_data_record = pd.DataFrame([updated_data])

            dataset.iloc[dataset[target_key] == target_record_key] = new_data_record.values

            dataset.to_csv(dataset_path, index=False)
            return jsonify({'message': 'Data record updated successfully'})
        else:
            return jsonify({'error': f'Data record with target_record_key {target_record_key} not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/delete_data/<target_key>-<target_record_key>', methods=['DELETE'])
def delete_data(target_key, target_record_key):
    global dataset

    target_record_key = int(target_record_key)
    dataset = dataset[dataset[target_key] != target_record_key]
    dataset.to_csv(dataset_path, index=False)

    return jsonify({'message': 'Data records deleted successfully'}), 201

if __name__ == '__main__':
    app.run(debug=True)
