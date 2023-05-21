import pymongo as pymongo
from flask import Flask, request, jsonify
from datetime import datetime
import re

# flask init
app = Flask(__name__)


# mongo init
def mongo_init():
    db_client = pymongo.MongoClient("mongodb://mongo:mongo@mongo:27017/?authMechanism=DEFAULT")
    current_db = db_client["distribution"]
    current_db.clients.create_index([('phone_number', 1)], unique=True)
    return current_db


def validate_phone_number(number):
    pattern = r'^7\d{10}$'
    match = re.match(pattern, number)
    if match:
        return True
    else:
        return False


# response page
@app.route('/add_client', methods=["POST"])
def add_client():
    params = request.get_json(force=True)

    new_client = {
        "phone_number": params.get("number"),
        "operator_code": params.get("operator"),
        "tag": params.get("tag"),
        "time_zone": params.get("time"),
    }
    # init mongo
    current_db = mongo_init()
    clients_collection = current_db["clients"]

    if not validate_phone_number(str(new_client["phone_number"])):
        return jsonify({"error": "Wrong number"}), 400

    elif clients_collection.find_one({"phone_number": int(new_client["phone_number"])}):
        return jsonify({"error": f"Client with number -  {new_client['phone_number']} already exist"}), 400

    for k, v in new_client.items():
        if v is None:
            return jsonify({"error": "Input all data that needs"}), 400

    clients_collection.insert_one(new_client)
    return jsonify({"message": f"Client with number - {new_client['phone_number']} successfully added."}), 200


@app.route('/update_client', methods=["PUT"])
def update_client():
    params = request.get_json(force=True)
    changed_client = {
        "phone_number": params.get("number"),
        "operator_code": params.get("operator"),
        "tag": params.get("tag"),
        "time_zone": params.get("time"),
    }

    current_db = mongo_init()
    clients_collection = current_db["clients"]

    if not clients_collection.find_one({"phone_number": int(changed_client["phone_number"])}):
        return jsonify({"error": f"There is no client with this number - {changed_client['phone_number']}"}), 400

    for k, v in changed_client.items():
        if v is None:
            return jsonify({"error": "Input all data that needs"}), 400

    filter = {"phone_number": changed_client["phone_number"]}
    update = {"$set": changed_client}
    clients_collection.update_one(filter, update)

    return jsonify({"message": f"Client with number - {changed_client['phone_number']} successfully updated"}), 200


@app.route('/delete_client/<string:phone_number>', methods=["DELETE"])
def delete_client(phone_number):
    # init mongo
    current_db = mongo_init()
    clients_collection = current_db["clients"]

    if not clients_collection.find_one({"phone_number": int(phone_number)}):
        return jsonify({"error": f"There is no client with this number - {phone_number}"}), 400

    clients_collection.delete_one({"phone_number": phone_number})

    return jsonify({"message": f"Client with number - {phone_number} successfully deleted"}), 200


@app.route('/add_mailing_list', methods=["POST"])
def add_mailing_list():
    params = request.get_json(force=True)
    start_time_str = params.get("start")
    end_time_str = params.get("end")

    # Преобразование строковых значений в объекты datetime
    try:
        start_time = datetime.strptime(start_time_str, "%d.%m.%Y %H:%M:%S")
        end_time = datetime.strptime(end_time_str, "%d.%m.%Y %H:%M:%S")
    except ValueError:
        return jsonify({"error": "Input start time and end time of mailing list in correct format ('%d.%m.%Y %H:%M:%S')"}), 400

    # init mongo
    current_db = mongo_init()
    mailing_collection = current_db["mailing_lists"]
    mail_id = mailing_collection.estimated_document_count() + 1
    new_mailing_list = {
        "_id": mail_id,
        "start_time": start_time,
        "message_text": params.get("text"),
        "filter": params.get("filter"),
        "end_time": end_time,
        "sent": False
    }
    for k, v in new_mailing_list.items():
        if v is None:
            return jsonify({"error": "Input all data that needs"}), 400
    mailing_collection.insert_one(new_mailing_list)
    return jsonify({"message": f"Mailing list with id - {mail_id} successfully added"}), 200


@app.route('/update_mailing_list', methods=["PUT"])
def update_mailing_list():
    params = request.get_json(force=True)
    mail_id = params.get("id")
    start_time_str = params.get("start")
    end_time_str = params.get("end")
    try:
        start_time = datetime.strptime(start_time_str, "%d.%m.%Y %H:%M:%S")
        end_time = datetime.strptime(end_time_str, "%d.%m.%Y %H:%M:%S")
    except ValueError:
        return jsonify({"error": "Input start time and end time of mailing list in correct format ('%d.%m.%Y %H:%M:%S')"}), 400

    mailing_list = {
        "start_time": start_time,
        "message_text": params.get("text"),
        "filter": params.get("filter"),
        "end_time": end_time,
        "sent": params.get("sent"),
    }
    for k, v in mailing_list.items():
        if v is None:
            return jsonify({"error": "Input all data that needs"}), 400

    # init mongo
    current_db = mongo_init()
    mailing_collection = current_db["mailing_lists"]
    if not mailing_collection.find_one({"_id": int(mail_id)}):
        return jsonify({"error": f"There is no mailing list with this id - {mail_id}"}), 400

    filter = {"_id": int(mail_id)}
    update = {"$set": mailing_list}
    mailing_collection.update_one(filter, update)
    return jsonify({"message": f"Mailing list with id - {mail_id} successfully updated"}), 200


@app.route('/delete_mailing_list/<string:mail_id>', methods=["DELETE"])
def delete_mailing_list(mail_id):
    current_db = mongo_init()
    mailing_collection = current_db["mailing_lists"]

    if not mailing_collection.find_one({"_id": int(mail_id)}):
        return jsonify({"error": f"There is no mailing list with this id - {mail_id}"}), 400

    mailing_collection.delete_one({"_id": int(mail_id)})
    return jsonify({"message": f"Mailing list with id - {mail_id} successfully deleted"}), 200


@app.route('/mails_stats', methods=["GET"])
def mails_stats():
    # mongo
    current_db = mongo_init()

    mailing_collection = current_db["mailing_lists"]
    count = mailing_collection.estimated_document_count()
    sent = mailing_collection.count_documents({"sent": True})
    mailing_data = {
        "count": count,
        "sent": sent,
        "not_sent": count - sent
    }

    messages_collection = current_db["messages"]
    count = messages_collection.estimated_document_count()
    delivered = messages_collection.count_documents({"status": "Delivered"})
    messages_data = {
        "count": count,
        "delivered": delivered,
        "not_delivered": count - delivered
    }

    return jsonify({"mailing_data": mailing_data, "messages_data": messages_data})


@app.route('/mail_stat/<string:mail_id>', methods=["GET"])
def mail_stat(mail_id):
    current_db = mongo_init()
    mailing_collection = current_db["mailing_lists"]
    if not mailing_collection.find_one({"_id": int(mail_id)}):
        return jsonify({"error": f"There is no mailing list with this id - {mail_id}"}), 400

    mail = mailing_collection.find_one({"_id": int(mail_id)})

    messages_collection = current_db["messages"]
    count = messages_collection.count_documents({"mailing_list_id": int(mail_id)})
    delivered = messages_collection.count_documents({"status": "Delivered", "mailing_list_id": int(mail_id)})
    messages_data = {
        "count": count,
        "delivered": delivered,
        "not_delivered": count - delivered
    }
    return jsonify({"mail": mail, "messages_data": messages_data})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
