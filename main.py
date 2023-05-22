import pymongo as pymongo
from flask import Flask, request, jsonify
from datetime import datetime
import re
import logging
from conf import log_level
import yaml

logging.basicConfig(level=log_level)

# flask init
app = Flask(__name__)


# mongo init
def mongo_init():
    logging.debug("mongo init")
    db_client = pymongo.MongoClient("mongodb://mongo:mongo@mongo:27017/?authMechanism=DEFAULT")
    current_db = db_client["distribution"]
    current_db.clients.create_index([('phone_number', 1)], unique=True)
    return current_db


def validate_phone_number(number):
    logging.debug("try to validate phone number")
    pattern = r'^7\d{10}$'
    match = re.match(pattern, number)
    if match:
        return True
    else:
        return False


# response page
@app.route('/add_client', methods=["POST"])
def add_client():
    logging.debug("try to add client")
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
        logging.error('not valid number')
        return jsonify({"error": "Wrong number"}), 400

    elif clients_collection.find_one({"phone_number": int(new_client["phone_number"])}):
        logging.error(f'client with number {new_client["phone_number"]} already exist')
        return jsonify({"error": f"Client with number -  {new_client['phone_number']} already exist"}), 400

    for k, v in new_client.items():
        if v is None:
            logging.error('not all data in request')
            return jsonify({"error": "Input all data that needs"}), 400
    logging.debug("try to add client in mongo")
    clients_collection.insert_one(new_client)
    logging.info(f"client with number:{new_client['phone_number']} added")
    return jsonify({"message": f"Client with number - {new_client['phone_number']} successfully added."}), 200


@app.route('/update_client', methods=["PUT"])
def update_client():
    logging.debug("try to update client")
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
        logging.error('not valid number')
        return jsonify({"error": f"There is no client with this number - {changed_client['phone_number']}"}), 400

    for k, v in changed_client.items():
        if v is None:
            logging.error('not all data in request')
            return jsonify({"error": "Input all data that needs"}), 400

    filter = {"phone_number": changed_client["phone_number"]}
    update = {"$set": changed_client}
    logging.debug("try to update client in mongo")
    clients_collection.update_one(filter, update)
    logging.info(f"client with number:{changed_client['phone_number']} updated")
    return jsonify({"message": f"Client with number - {changed_client['phone_number']} successfully updated"}), 200


@app.route('/delete_client/<string:phone_number>', methods=["DELETE"])
def delete_client(phone_number):
    logging.debug("try to delete client")

    # init mongo
    current_db = mongo_init()
    clients_collection = current_db["clients"]

    if not clients_collection.find_one({"phone_number": int(phone_number)}):
        logging.error('number is not exist')
        return jsonify({"error": f"There is no client with this number - {phone_number}"}), 400

    logging.debug("try to delete client in mongo")
    clients_collection.delete_one({"phone_number": int(phone_number)})
    logging.info(f"client with number:{phone_number} deleted")
    return jsonify({"message": f"Client with number - {phone_number} successfully deleted"}), 200


@app.route('/add_mailing_list', methods=["POST"])
def add_mailing_list():
    logging.debug("try to add mailing list")

    params = request.get_json(force=True)
    start_time_str = params.get("start")
    end_time_str = params.get("end")

    # transform str to datetime and validate format
    try:
        start_time = datetime.strptime(start_time_str, "%d.%m.%Y %H:%M:%S")
        end_time = datetime.strptime(end_time_str, "%d.%m.%Y %H:%M:%S")
    except ValueError:
        logging.error('wrong format date')
        return jsonify(
            {"error": "Input start time and end time of mailing list in correct format ('%d.%m.%Y %H:%M:%S')"}), 400

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
            logging.error('not all data in request')
            return jsonify({"error": "Input all data that needs"}), 400

    logging.debug("try to add mailing list in mongo")
    mailing_collection.insert_one(new_mailing_list)
    logging.info(f"mailing list added mail_id:{mail_id}")
    return jsonify({"message": f"Mailing list with id - {mail_id} successfully added"}), 200


@app.route('/update_mailing_list', methods=["PUT"])
def update_mailing_list():
    logging.debug("try to update mailing list")

    params = request.get_json(force=True)
    mail_id = params.get("id")
    start_time_str = params.get("start")
    end_time_str = params.get("end")
    # transform str to datetime and validate format
    try:
        start_time = datetime.strptime(start_time_str, "%d.%m.%Y %H:%M:%S")
        end_time = datetime.strptime(end_time_str, "%d.%m.%Y %H:%M:%S")
    except ValueError:
        logging.error('wrong format date')
        return jsonify(
            {"error": "Input start time and end time of mailing list in correct format ('%d.%m.%Y %H:%M:%S')"}), 400

    mailing_list = {
        "start_time": start_time,
        "message_text": params.get("text"),
        "filter": params.get("filter"),
        "end_time": end_time,
        "sent": params.get("sent"),
    }
    for k, v in mailing_list.items():
        if v is None:
            logging.error('not all data in request')
            return jsonify({"error": "Input all data that needs"}), 400

    # init mongo
    current_db = mongo_init()
    mailing_collection = current_db["mailing_lists"]
    if not mailing_collection.find_one({"_id": int(mail_id)}):
        logging.error('wrong id of mailing list')
        return jsonify({"error": f"There is no mailing list with this id - {mail_id}"}), 400

    filter = {"_id": int(mail_id)}
    update = {"$set": mailing_list}
    logging.debug("try to update mailing list in mongo")
    mailing_collection.update_one(filter, update)
    logging.info(f"mailing list updated mail_id:{mail_id}")
    return jsonify({"message": f"Mailing list with id - {mail_id} successfully updated"}), 200


@app.route('/delete_mailing_list/<string:mail_id>', methods=["DELETE"])
def delete_mailing_list(mail_id):
    logging.debug("try to delete mailing list")

    current_db = mongo_init()
    mailing_collection = current_db["mailing_lists"]

    if not mailing_collection.find_one({"_id": int(mail_id)}):
        logging.error('wrong id of mailing list')
        return jsonify({"error": f"There is no mailing list with this id - {mail_id}"}), 400

    logging.debug("try to delete mailing list in mongo")
    mailing_collection.delete_one({"_id": int(mail_id)})
    logging.info(f"mailing list deleted mail_id:{mail_id}")
    return jsonify({"message": f"Mailing list with id - {mail_id} successfully deleted"}), 200


@app.route('/mails_stats', methods=["GET"])
def mails_stats():
    logging.debug("try to give statistics about mails")

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
    logging.debug("try to give extended statistics about mail")

    current_db = mongo_init()
    mailing_collection = current_db["mailing_lists"]
    if not mailing_collection.find_one({"_id": int(mail_id)}):
        logging.error('wrong id of mailing list')
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


@app.route('/docs', methods=["GET"])
def docs():
    logging.debug("try to give swagger.yaml")
    with open("swagger.yaml", "r", encoding="utf-8") as file:
        return jsonify(yaml.safe_load(file))


if __name__ == "__main__":
    logging.info("start app")
    app.run(host="0.0.0.0", port=5000)
