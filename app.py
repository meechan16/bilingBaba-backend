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
    # prev_data = read_from_firestore(uid)
    prev_data = sample_data

    if prev_data["sales"]:
        prev_data["sales"].append(data)
        print(data)
    else:
        prev_data["sales"] = [data,]
    if prev_data['total_sales']:
        prev_data["total_sales"] += int(data['total'])
    else:
        prev_data["total_sales"] = int(data['total'])

    write_to_firestore(uid, prev_data)


def add_pruchase(uid, data):
    prev_data = read_from_firestore(uid)
    # prev_data = sample_data
    if prev_data["purchase"]:
        prev_data["purchase"].append(data)
        print(data)
    else:
        prev_data["purchase"] = [data,]
    if prev_data['total_purchase']:
        prev_data["total_purchase"] += int(data['total'])
    else:
        prev_data["total_purchase"] = int(data['total'])

    write_to_firestore(uid, prev_data)


def add_Item(uid, data):
    prev_data = read_from_firestore(uid)
    # prev_data = sample_data
    if prev_data["items"]:
        prev_data["items"].append(data)
        print(data)
    else:
        prev_data["items"] = [data,]

    write_to_firestore(uid, prev_data)


def add_parties(uid, data):
    prev_data = read_from_firestore(uid)
    # prev_data = sample_data
    if prev_data["parties"]:
        prev_data["parties"].append(data)
        print(data)
    else:
        prev_data["parties"] = [data,]
    write_to_firestore(uid, prev_data)


# ROOT URLS
@app.route("/", methods=['GET'])
def index():
    return jsonify({"status": "200 - working", "descripttion": "welcome to coachpointai API"})


@app.route('/addsales', methods=['POST'])
def add_items():
    auth_header = request.headers.get('Authorization')
    print("Authorization Header:", auth_header)
    # if not check_user_exists(auth_header):
    #     return jsonify({"status": "fail", "Description": "user doesnt exist"}), 200

    file_path = request.get_json()
    print(file_path)
    add_Sale(auth_header, file_path)
    return jsonify({"status": "success"}), 200


@app.route('/update_todo', methods=['POST'])
def todo():
    auth_header = request.headers.get('Authorization')
    print("Authorization Header:", auth_header)
    # if not check_user_exists(auth_header):
    #     return jsonify({"status": "fail", "Description": "user doesnt exist"}), 200
    reqdata = request.get_json()
    print(reqdata)
    write_to_firestore(auth_header, reqdata)
    return jsonify({"status": "success"}), 200


@app.route('/addsalesAndGetPdf', methods=['POST'])
def add_items_and_get_pdf():
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


# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
# app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
# app.config['MAIL_USE_TLS'] = True   # Set it to False if you're using SSL
# app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_USERNAME")

# mail = Mail(app)

# from app.routes.user_routes import USER_BLUEPRINT
# from app.routes.data_routes import DATA_BP

# app.register_blueprint(USER_BLUEPRINT)
# app.register_blueprint(DATA_BP)


# @app.route('/contact_us', methods=['POST'])
# def Support_mail():
#     data = request.get_json()

#     subject = str(data.get('email'))
#     body = data.get('body')
#     email = 'karan@coachpoints.ai'

#     from app.utils.Others import send_email
#     # user_mail_body = "Thank you for reaching out to us. \nWe genuinely appreciate your inquiry, and our dedicated team is committed to providing you with the best possible assistance. \nYour query is important to us, and we will respond as soon as possible.\n In the meantime, if you have any further questions or require immediate assistance,\n please don't hesitate to get in touch. \nWe look forward to helping you with your needs.\n\nCoachpoints.ai"
#     user_mail_body = '''
# Thank you for reaching out to us.
# We appreciate your inquiry, and our dedicated team will get back to you asap.

# In the meantime, if you have any further questions or require immediate assistance, please reply to this email with your email id and query.

# Thanks,
# Team CoachPoints AI
#     '''
#     User_email = send_email(email=subject, subject="Querry Submission - Team Coachpoint",body= user_mail_body)
#     system_email = send_email(email, "Querry from "+subject, body)
#     if User_email and system_email:
#         return jsonify({"message": "Email sent successfully!"}), 200
#     else:
#         return jsonify({"error": "Failed to send email."}), 500


# from app.utils.mongoDb import ADMIN
# @app.route('/admin', methods=['GET'])
# def admin():
#     Id = request.args.get('id')
#     if Id == "cheesecake":
#         data = ADMIN.get_data()
#         print(type(data))
#         if '_id' in data:
#             del data['_id']
#         return format_dictionary({"Status":True,"data":data}), 200
#     else:
#         return jsonify({"status":"False","Desc":"prohabbited"}),200

if __name__ == '__main__':
    app.run(port=9000, debug=True)
