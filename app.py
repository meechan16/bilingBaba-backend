from flask import Flask, jsonify, Response, request, send_file
import firebase_admin
from firebase_admin import credentials, auth, firestore
from firebase_admin.exceptions import FirebaseError
from flask_cors import CORS
# from flask_mail import Mail
from dotenv import load_dotenv, dotenv_values
import os

app = Flask(__name__)
CORS(app)

load_dotenv()


try:
    cred = credentials.Certificate("auth_key.json")
except Exception as e:
    print(e)
    print("failed to get firebasse auth json from root dir")
    cred = credentials.Certificate('backend/auth_key.json')

firebase_admin.initialize_app(cred)
db = firestore.client()

# user data schema

sample_data = {
    "name": None,
    "email": None,
    "todo_list": {
        "task 1": "done",
        "task 2": "pending",
        "task 3": "pending",
        "task 4": "done",
        "task 5": "done",
    },
    "sales": [],
    "parties": [],
    "items": [],
    "total_sales": 0,
    "total_purchase": 0,
    "total_profit": 0,
    "to_Collect": 0,
    "to_pay": 0,
    "expense": 0,
    "purchase": 0,
    "cash_in_hand": 0
}


def check_user_exists(uid):
    try:
        user = auth.get_user(uid)
        print(user)
        return True
    except FirebaseError as e:
        if e.code == 'user-not-found':
            print("User does not exist")
            return False
        else:
            # Handle other exceptions
            print("Error occurred:", e)
            return False


def write_to_firestore(custom_id, data, collection="user_data"):
    # Add a document with a custom ID to the "items" collection
    doc_ref = db.collection(collection).document(custom_id)
    doc_ref.set(data)
    print("Document '{}' written to Firestore.".format(custom_id))
    return True


def read_from_firestore(custom_id, collection="user_data"):
    # Retrieve a document from the "items" collection
    doc_ref = db.collection(collection).document(custom_id)
    doc = doc_ref.get()
    if doc.exists:
        print("Document data:", doc.to_dict())
    else:
        print("No such document!")
    return doc.to_dict()


def add_Sale(uid, data):
    prev_data = read_from_firestore(uid)
    # print("before", prev_data, "/n")
    # prev_data = sample_data

    try:
        prev_data["sales"].append(data)
        # print(data)
    except Exception as e:
        print(e)
        prev_data["sales"] = [data,]
    try:
        prev_data["total_sales"] += int(data['total'])
    except Exception as e:
        print(e)
        prev_data["total_sales"] = int(data['total'])

    try:
        print(prev_data["name"])
    except:
        print("data got reset")
        return False
    # print("after", prev_data, "/n")
    return write_to_firestore(uid, prev_data)


def add_pruchase(uid, data):
    prev_data = read_from_firestore(uid)
    # prev_data = sample_data
    try:
        prev_data["purchase"].append(data)
        print(data)
    except Exception as e:
        print(e)
        prev_data["purchase"] = [data,]
    try:
        prev_data["total_purchase"] += int(data['total'])
    except Exception as e:
        print(e)
        prev_data["total_purchase"] = int(data['total'])

    try:
        print(prev_data["name"])
    except:
        print("data got reset")
        return False
    # print("after", prev_data, "/n")
    return write_to_firestore(uid, prev_data)


def add_items(uid, data):
    prev_data = read_from_firestore(uid)
    # prev_data = sample_data
    try:
        prev_data["items"].append(data)
        print(data)
    except Exception as e:
        print(e)
        prev_data["items"] = [data,]

    try:
        print(prev_data["name"])
    except:
        print("data got reset")
        return False
    # print("after", prev_data, "/n")
    return write_to_firestore(uid, prev_data)


def add_parties(uid, data):
    prev_data = read_from_firestore(uid)
    # prev_data = sample_data
    try:
        prev_data["parties"].append(data)
        # print(data)
    except Exception as e:
        print(e)
        prev_data["parties"] = [data,]
    try:
        print(prev_data["name"])
    except:
        print("data got reset")
        return False
    # print("after", prev_data, "/n")
    return write_to_firestore(uid, prev_data)

# ROOT URLS


@app.route("/", methods=['GET'])
def index():
    return jsonify({"status": "200 - working", "descripttion": "welcome to coachpointai API"})


@app.route('/reset_acc', methods=['GET'])
def reset_Acc():
    auth_header = request.headers.get('Authorization')
    print("reset requested by: ", auth_header)
    # if not check_user_exists(auth_header):
    #     return jsonify({"status": "fail", "Description": "user doesnt exist"}), 200

    write_to_firestore(auth_header, sample_data)
    return jsonify({"status": "success"}), 200


@app.route('/addsales', methods=['POST'])
def add_sales():
    auth_header = request.headers.get('Authorization')
    # print("Authorization Header:", auth_header)
    # if not check_user_exists(auth_header):
    #     return jsonify({"status": "fail", "Description": "user doesnt exist"}), 200

    file_path = request.get_json()
    # print(file_path)
    res = add_Sale(auth_header, file_path)
    if res:
        return jsonify({"status": res}), 200
    else:
        return jsonify({"status": res}), 501


@app.route('/addpurchase', methods=['POST'])
def add_purchase():
    auth_header = request.headers.get('Authorization')
    # print("Authorization Header:", auth_header)
    # if not check_user_exists(auth_header):
    #     return jsonify({"status": "fail", "Description": "user doesnt exist"}), 200

    file_path = request.get_json()
    print(file_path)
    res = add_pruchase(auth_header, file_path)
    if res:
        return jsonify({"status": res}), 200
    else:
        return jsonify({"status": res}), 501


@app.route('/additems', methods=['POST'])
def add_it():
    auth_header = request.headers.get('Authorization')
    # print("Authorization Header:", auth_header)
    # if not check_user_exists(auth_header):
    #     return jsonify({"status": "fail", "Description": "user doesnt exist"}), 200

    file_path = request.get_json()
    # print(file_path)
    res = add_items(auth_header, file_path)
    if res:
        return jsonify({"status": res}), 200
    else:
        return jsonify({"status": res}), 501


@app.route('/addparties', methods=['POST'])
def add_pa():
    auth_header = request.headers.get('Authorization')
    # print("Authorization Header:", auth_header)
    # if not check_user_exists(auth_header):
    #     return jsonify({"status": "fail", "Description": "user doesnt exist"}), 200

    file_path = request.get_json()
    # print(file_path)
    res = add_parties(auth_header, file_path)
    if res:
        return jsonify({"status": res}), 200
    else:
        return jsonify({"status": res}), 501


@app.route('/update_todo', methods=['POST'])
def todo():
    auth_header = request.headers.get('Authorization')
    # print("Authorization Header:", auth_header)
    # if not check_user_exists(auth_header):
    #     return jsonify({"status": "fail", "Description": "user doesnt exist"}), 200
    reqdata = request.get_json()
    print(reqdata)
    res = write_to_firestore(auth_header, reqdata)
    if res:
        return jsonify({"status": res}), 200
    else:
        return jsonify({"status": res}), 501


@app.route('/addsalesAndGetPdf', methods=['POST'])
def save_sales_nd_pdf():
    auth_header = request.headers.get('Authorization')
    print("Authorization Header:", auth_header)
    # if not check_user_exists(auth_header):
    #     return jsonify({"status": "fail", "Description": "user doesnt exist"}), 200

    data = request.get_json()
    print(data)
    write_to_firestore(
        data=data, custom_id=auth_header)

    from bill_pdf_maker import create_tax_invoice_pdf
    buffer = create_tax_invoice_pdf(data)
    return send_file(buffer, mimetype='application/pdf')


@app.route('/get_user', methods=['GET'])
def get_items():
    auth_header = request.headers.get('Authorization')
    print("Authorization Header:", auth_header)
    # if not check_user_exists(auth_header):
    #     return jsonify({"status": "fail", "Description": "user doesnt exist"}), 200

    res = read_from_firestore(custom_id=auth_header)
    return jsonify({"status": "success", "data": res}), 200


if __name__ == '__main__':
    app.run(port=9000, debug=True)
