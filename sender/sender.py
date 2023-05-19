import pymongo
import datetime
import time
import requests
# import settings
from conf import token, check_base_rate
print(token)
# headers and url for requests
HEADERS = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
URL = "https://probe.fbrq.cloud/v1/send/"


# init mongo
def mongo_init():
    db_client = pymongo.MongoClient("mongodb://mongo:mongo@mongo:27017/?authMechanism=DEFAULT")
    distribution = db_client["distribution"]
    return distribution


# function for
def send(mailing_row):
    current_db = mongo_init()
    messages_collection = current_db["messages"]
    msg_id = messages_collection.estimated_document_count()

    clients_collection = current_db["clients"]
    clients = clients_collection.find({"tag": mailing_row["filter"]})

    for client in clients:
        msg_id += 1
        json = {
            "id": msg_id,
            "phone": client["phone_number"],
            "text": mailing_row["message_text"]
        }
        try:
            response = requests.post(URL + str(msg_id), headers=HEADERS, json=json)
            if response.status_code != 200:
                deliver_status = f"Not delivered, status code - {response.status_code}"
                if response.status_code == 401:
                    deliver_status += f", message - {response.json()['message']}"
            else:
                deliver_status = "Delivered"
        except requests.exceptions.ConnectionError:
            deliver_status = "Not delivered, message - connection aborted"

        # save in mongo messages
        message = {
            "id": msg_id,
            "send_time": datetime.datetime.now(),
            "status": deliver_status,
            "mailing_list_id": mailing_row["_id"],
            "client_id": client["_id"],
        }
        messages_collection.insert_one(message)


while True:
    time_now = datetime.datetime.now()
    distribution = mongo_init()
    mailing_collection = distribution["mailing_lists"]
    result = mailing_collection.find({"start_time": {"$lte": time_now}, "end_time": {"$gt": time_now}})
    for row in result:
        if not row["sent"]:
            print(f"!!!!!!!!!!!!!!!!!!{row}")
            send(row)
            filter_query = {"_id": row["_id"]}
            update_query = {"$set": {"sent": True}}
            mailing_collection.update_one(filter_query, update_query)

    time.sleep(int(check_base_rate))
