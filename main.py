import pymongo as pymongo
from flask import Flask, request, jsonify
from datetime import datetime

# flask init
app = Flask(__name__)


# mongo init
def mongo_init():
    db_client = pymongo.MongoClient("mongodb://mongo:mongo@mongo:27017/?authMechanism=DEFAULT")
    current_db = db_client["distribution"]
    current_db.clients.create_index([('phone_number', 1)], unique=True)
    return current_db


# response page
@app.route('/add_client', methods=["POST"])
def add_client():
    params = request.form
    new_client = {
        "phone_number": params.get("number"),
        "operator_code": params.get("operator"),
        "tag": params.get("tag"),
        "time_zone": params.get("time"),
    }
    # init mongo
    current_db = mongo_init()
    clients_collection = current_db["clients"]
    clients_collection.insert_one(new_client)

    return f"Client with number {new_client['phone_number']} successfully added."


@app.route('/update_client', methods=["PUT"])
def update_client():
    params = request.form
    changed_client = {
        "phone_number": params.get("number"),
        "operator_code": params.get("operator"),
        "tag": params.get("tag"),
        "time_zone": params.get("time"),
    }
    current_db = mongo_init()
    clients_collection = current_db["clients"]
    filter = {"phone_number": changed_client["phone_number"]}
    update = {"$set": changed_client}
    clients_collection.update_one(filter, update)
    return f"Client with number {changed_client['phone_number']} successfully updated"


@app.route('/delete_client/<string:phone_number>', methods=["DELETE"])
def delete_client(phone_number):
    # init mongo
    current_db = mongo_init()
    clients_collection = current_db["clients"]
    clients_collection.delete_one({"phone_number": phone_number})

    return f"Client with number {phone_number} successfully deleted"


@app.route('/add_mailing_list', methods=["POST"])
def add_mailing_list():
    params = request.form
    start_time_str = params.get("start")
    end_time_str = params.get("end")

    # Преобразование строковых значений в объекты datetime
    start_time = datetime.strptime(start_time_str, "%d.%m.%Y %H:%M:%S")
    end_time = datetime.strptime(end_time_str, "%d.%m.%Y %H:%M:%S")


    # init mongo
    current_db = mongo_init()
    mailing_collection = current_db["mailing_lists"]
    mail_id = mailing_collection.estimated_document_count()+1
    new_mailing_list = {
        "_id": mail_id,
        "start_time": start_time,
        "message_text": params.get("text"),
        "filter": params.get("filter"),
        "end_time": end_time,
        "sent": False
    }
    mailing_collection.insert_one(new_mailing_list)
    return f"Mailing list successfully added"


@app.route('/update_mailing_list', methods=["PUT"])
def update_mailing_list():
    params = request.form
    mail_id = params.get("id")
    mailing_list = {
        "start_time": params.get("start"),
        "message_text": params.get("text"),
        "filter": params.get("filter"),
        "end_time": params.get("end"),
        "sent": params.get("sent"),
    }
    # init mongo
    current_db = mongo_init()
    mailing_collection = current_db["mailing_lists"]
    filter = {"_id": int(mail_id)}
    update = {"$set": mailing_list}
    mailing_collection.update_one(filter, update)
    return f"Mailing list with id {mail_id} successfully updated"


@app.route('/delete_mailing_list/<string:id>', methods=["DELETE"])
def delete_mailing_list(id):
    current_db = mongo_init()
    mailing_collection = current_db["mailing_lists"]
    mailing_collection.delete_one({"_id": int(id)})
    return f"Mailing list with id {id} successfully deleted"


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
