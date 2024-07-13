from flask import Flask, jsonify, Response, request, send_file
import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
from firebase_admin.exceptions import FirebaseError
from flask_cors import CORS
# from flask_mail import Mail
import os
import io
import uuid

app = Flask(__name__)
CORS(app)

try:
    cred = credentials.Certificate("auth_key.json")
except Exception as e:
    print(e)
    print("failed to get firebasse auth json from root dir")
    cred = credentials.Certificate('backend/auth_key.json')

firebase_admin.initialize_app(cred, {
    'storageBucket': 'billing-baba.appspot.com'
})
db = firestore.client()
bucket = storage.bucket()

# user data schema

sample_data = {
    "name": None,
    "email": None,
    "todo_list": {
        "sample task 1": "done",
        "sample task 2": "pending",
    },
    "sales": [],
    "total_sales": 0,
    "sale_pending": 0,
    "sale_paid": 0,
    "parties": [],
    "items": [],
    "total_purchase": 0,
    "total_profit": 0,
    "total_expense": 0,
    "to_Collect": 0,
    "to_pay": 0,
    "expenseItems": [],
    "ExpenseCategory": [],
    "purchase": [],
    "cash_in_hand": 0
}


def check_user_exists(uid):
    try:
        user = auth.get_user(uid)
        # print(user)
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
    # if doc.exists:
    #     print("Document data:", doc.to_dict())
    # else:
    #     print("No such document!")
    return doc.to_dict()


def upload_file(file_content, filename, file_type):
    # Determine content type and file extension
    if file_type == 'image':
        content_type = 'image/png'
        extension = '.png'
    elif file_type == 'pdf':
        content_type = 'application/pdf'
        extension = '.pdf'
    else:
        raise ValueError(
            "Unsupported file type. Only 'image' and 'pdf' are supported.")

    # Generate full filename
    full_filename = f"file_{filename}{extension}"
    print(full_filename)

    # Create a blob and upload the file
    blob = bucket.blob(full_filename)

    # If file_content is a BytesIO object, read it as bytes
    if isinstance(file_content, io.BytesIO):
        file_content = file_content.read()

    blob.upload_from_string(file_content, content_type=content_type)
    blob.make_public()

    # Return the public URL of the uploaded file
    file_url = blob.public_url
    return file_url


def delete_img(url):
    image1_blob = storage.bucket().blob(url)
    image1_blob.delete()
    return True


# def add_Sale(uid, data):
#     prev_data = read_from_firestore(uid)

#     # print("sales pre", prev_data)
#     # count total length of previous array, add 1 and use it for index
#     try:
#         if len(prev_data["sales"] == 0):
#             sales_index = 0
#         else:
#             sales_index = prev_data["sales"]["index"] + 1
#     except:
#         sales_index = 0
#     # sales_index = len(prev_data['sales']) + 1
#     data['index'] = sales_index

#     # print("index: ", sales_index)

#     # add sales list
#     try:
#         prev_data["sales"].append(data)
#     except Exception as e:
#         prev_data["sales"] = [data,]

#     # add pending paid
#     try:
#         prev_data["sale_pending"] += int(data['pending'])
#     except Exception as e:
#         print(e)
#         prev_data["sale_pending"] = int(data['pending'])
#     try:
#         prev_data["sale_paid"] += int(data['paid'])
#     except Exception as e:
#         print(e)
#         prev_data["sale_paid"] = int(data['paid'])

#     # add to collect
#     if data['paymentStatus'] == 'pending':
#         prev_data['to_collect'] += int(data['pending'])

#     # add total sales
#     try:
#         prev_data["total_sales"] += int(data['total'])
#     except Exception as e:
#         print(e)
#         prev_data["total_sales"] = int(data['total'])

#     # print("sales", prev_data)
#     # Test data
#     try:
#         print("data test", prev_data["name"])
#     except:
#         print("data got reset")
#         return False
#     return write_to_firestore(uid, prev_data)


# def add_pruchase(uid, data):
#     prev_data = read_from_firestore(uid)
#     # prev_data = sample_data
#     try:
#         prev_data["purchase"].append(data)
#         # print(data)
#     except Exception as e:
#         print(e)
#         prev_data["purchase"] = [data,]
#     try:
#         prev_data["total_purchase"] += int(data['total'])
#     except Exception as e:
#         print(e)
#         prev_data["total_purchase"] = int(data['total'])

#     try:
#         print(prev_data["name"])
#     except:
#         print("data got reset")
#         return False
#     # print("after", prev_data, "/n")
#     return write_to_firestore(uid, prev_data)


# def add_items(uid, data):
#     prev_data = read_from_firestore(uid)
#     # prev_data = sample_data
#     try:
#         prev_data["items"].append(data)
#         print(data)
#     except Exception as e:
#         print(e)
#         prev_data["items"] = [data,]

#     try:
#         print(prev_data["name"])
#     except:
#         print("data got reset")
#         return False
#     # print("after", prev_data, "/n")
#     return write_to_firestore(uid, prev_data)


# def add_units(uid, data):
#     prev_data = read_from_firestore(uid)
#     # prev_data = sample_data
#     try:
#         prev_data["units"].append(data)
#         print(data)
#     except Exception as e:
#         print(e)
#         prev_data["units"] = [data,]

#     try:
#         print(prev_data["name"])
#     except:
#         print("data got reset")
#         return False
#     # print("after", prev_data, "/n")
#     return write_to_firestore(uid, prev_data)


# def add_category(uid, data):
#     prev_data = read_from_firestore(uid)
#     # prev_data = sample_data
#     entry = {}
#     entry["name"] = data["Category"]
#     try:
#         prev_data["category"].append(entry)
#         # print(data)
#     except Exception as e:
#         print(e)
#         prev_data["category"] = list(entry)

#     try:
#         print(prev_data["name"])
#     except:
#         print("data got reset")
#         return False
#     # print("after", prev_data, "/n")
#     return write_to_firestore(uid, prev_data)


def add_info(uid, data):
    # prev_data = read_from_firestore(uid)
    prev_data = sample_data
    # write_to_firestore(auth_header, sample_data)
    # prev_data = sample_data
    try:
        print(prev_data["name"])
    except:
        print("data got reset")
        return False
    try:
        prev_data["uid"] = data['uid']
        prev_data["name"] = data['Name']
        prev_data["BusinessName"] = data['BusinessName']
        prev_data["email"] = data['email']
        prev_data["GSTIN"] = data['GSTIN']
        prev_data["mobile"] = data['Mobile']
        # print(data)
    except Exception as e:
        print(e)
        return False
    # print("after", prev_data, "/n")
    return write_to_firestore(uid, prev_data)


# def add_parties(uid, data):
#     prev_data = read_from_firestore(uid)
#     # prev_data = sample_data
#     try:
#         prev_data["parties"].append(data)
#         # print(data)
#     except Exception as e:
#         print(e)
#         prev_data["parties"] = [data,]
#     try:
#         print(prev_data["name"])
#     except:
#         print("data got reset")
#         return False
#     # print("after", prev_data, "/n")
#     return write_to_firestore(uid, prev_data)


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

    write_to_firestore(auth_header, {})
    return jsonify({"status": "success"}), 200


@app.route('/editData', methods=['POST'])
def editData():
    auth_header = request.headers.get('Authorization')
    print("Authorization Header:", auth_header)
    if not check_user_exists(auth_header):
        return jsonify({"status": "fail", "Description": "user doesnt exist"}), 200

    data = request.get_json()
    prev_data = read_from_firestore(auth_header)
    # prev_data = sample_data
    # try:
    #     prev_data["parties"].append(data)
    #     # print(data)
    # except Exception as e:
    #     print(e)
    #     prev_data["parties"] = [data,]
    try:
        a = data["name"]
    except:
        print("data got reset")
        return jsonify({"status": False, "desc": "data got reset"}), 400
    # print(data)
    res = write_to_firestore(auth_header, data)
    # res = add_Sale(auth_header, file_path)
    if res:
        return jsonify({"status": res}), 200
    else:
        return jsonify({"status": res}), 501


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


# @app.route('/additems', methods=['POST'])
# def add_it():
#     auth_header = request.headers.get('Authorization')
#     # print("Authorization Header:", auth_header)
#     # if not check_user_exists(auth_header):
#     #     return jsonify({"status": "fail", "Description": "user doesnt exist"}), 200

#     file_path = request.get_json()
#     # print(file_path)
#     res = add_items(auth_header, file_path)
#     if res:
#         return jsonify({"status": res}), 200
#     else:
#         return jsonify({"status": res}), 501


# @app.route('/addCategory', methods=['POST'])
# def add_cat():
#     auth_header = request.headers.get('Authorization')
#     # print("Authorization Header:", auth_header)
#     # if not check_user_exists(auth_header):
#     #     return jsonify({"status": "fail", "Description": "user doesnt exist"}), 200

#     file_path = request.get_json()
#     # print(file_path)
#     res = add_category(auth_header, file_path)
#     if res:
#         return jsonify({"status": res}), 200
#     else:
#         return jsonify({"status": res}), 501


# @app.route('/addUnits', methods=['POST'])
# def add_un():
#     auth_header = request.headers.get('Authorization')
#     # print("Authorization Header:", auth_header)
#     # if not check_user_exists(auth_header):
#     #     return jsonify({"status": "fail", "Description": "user doesnt exist"}), 200

#     file_path = request.get_json()
#     # print(file_path)
#     res = add_units(auth_header, file_path)
#     if res:
#         return jsonify({"status": res}), 200
#     else:
#         return jsonify({"status": res}), 501


@app.route('/addinfo', methods=['POST'])
def add_inf():
    auth_header = request.headers.get('Authorization')
    # print("Authorization Header:", auth_header)
    # if not check_user_exists(auth_header):
    #     return jsonify({"status": "fail", "Description": "user doesnt exist"}), 200

    file_path = request.get_json()
    # print(file_path)
    res = add_info(auth_header, file_path)
    if res:
        return jsonify({"status": res}), 200
    else:
        return jsonify({"status": res}), 501


# @app.route('/addparties', methods=['POST'])
# def add_pa():
#     auth_header = request.headers.get('Authorization')
#     # print("Authorization Header:", auth_header)
#     # if not check_user_exists(auth_header):
#     #     return jsonify({"status": "fail", "Description": "user doesnt exist"}), 200

#     file_path = request.get_json()
#     # print(file_path)
#     res = add_parties(auth_header, file_path)
#     if res:
#         return jsonify({"status": res}), 200
#     else:
#         return jsonify({"status": res}), 501


@app.route('/update_todo', methods=['POST'])
def todo():
    header = request.headers.get('Authorization')
    # print("Authorization Header:", auth_header)
    # if not check_user_exists(auth_header):
    #     return jsonify({"status": "fail", "Description": "user doesnt exist"}), 200
    data = request.get_json()

    prev_data = read_from_firestore(header)
    # prev_data = sample_data
    # print('reqdata = ', data)
    prev_data["todo_list"] = data["todo_lists"]
    # try:

    #     # print(data)
    # except Exception as e:
    #     print(e)
    #     # prev_data["todo_list"] = [data["todo_lists"]
    # print('data = ', prev_data)
    try:
        print("Todo test PASS for - ", prev_data["name"])
    except:
        print("data got reset")
        return jsonify({"status": "failed due to insufficient data"}), 200

    res = write_to_firestore(header, prev_data)
    if res:
        return jsonify({"status": res}), 200
    else:
        return jsonify({"status": res}), 501


@app.route('/get-sales-invoice-pdf', methods=['POST'])
def save_sales_nd_pdf():
    auth_header = request.headers.get('Authorization')
    # print("Authorization Header:", auth_header)
    if not check_user_exists(auth_header):
        return jsonify({"status": "fail", "Description": "user doesnt exist"}), 200

    data = request.get_json()
    # print(data)
    # add_Sale(data=data, uid=auth_header)

    from bill_pdf_maker import create_tax_invoice_pdf
    buffer = create_tax_invoice_pdf(data)
    link = upload_file(buffer, "invoicePdf", file_type="pdf")
    return jsonify({"link": link})


@app.route('/generate-barcode', methods=['POST'])
def barcodeGen():
    auth_header = request.headers.get('Authorization')
    # print("Authorization Header:", auth_header)
    if not check_user_exists(auth_header):
        return jsonify({"status": "fail", "Description": "user doesnt exist"}), 200

    data = request.get_json()

    from barcode1 import generate_barcode_blob

    barcode = generate_barcode_blob(data['itemNumber'])

    url = upload_file(barcode, filename=str(data['itemNumber']))

    return jsonify({"url": url, "status": "success"}), 200


@app.route('/get_user', methods=['GET'])
def get_items():
    auth_header = request.headers.get('Authorization')
    # print("Authorization Header:", auth_header)
    # if not check_user_exists(auth_header):
    #     return jsonify({"status": "fail", "Description": "user doesnt exist"}), 200

    res = read_from_firestore(custom_id=auth_header)
    # print(res)
    return jsonify({"status": "success", "data": res}), 200


if __name__ == '__main__':
    app.run(port=9000, debug=True)
