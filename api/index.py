import requests
import random
from flask import Flask, jsonify, request
import json
import os


class GameInfo:
    def __init__(self):
        self.TitleId: str = "1123E0"
        self.SecretKey: str = "UBQQHD54FIGNWPQB5DKICRKCMKADZC6WXHMH1U3E5QW6FRZ8BB"
        self.ApiKey: list[str] = [
            "OC|9766745833430521|ec2803ae8ecfec90ae795333f1c49d8b",
        ]
        Webhook = "https://discord.com/api/webhooks/1442371714754281565/n9xqrZYtg9R2KkcAL1YTqOhdIRye04xqMyYDwvnd2tbCtRo3Ri8_cKbWdwKgqdt13laG"

    def get_auth_headers(self):
        return {"content-type": "application/json", "X-SecretKey": self.SecretKey}


settings = GameInfo()
app = Flask(__name__)


def return_function_json(data, funcname, funcparam={}):
    user_id = data["FunctionParameter"]["CallerEntityProfile"]["Lineage"][
        "TitlePlayerAccountId"
    ]

    response = requests.post(
        url=f"https://{settings.TitleId}.playfabapi.com/Server/ExecuteCloudScript",
        json={
            "PlayFabId": user_id,
            "FunctionName": funcname,
            "FunctionParameter": funcparam,
        },
        headers=settings.get_auth_headers(),
    )

    if response.status_code == 200:
        return (
            jsonify(response.json().get("data").get("FunctionResult")),
            response.status_code,
        )
    else:
        return jsonify({}), response.status_code


@app.route("/", methods=["POST", "GET"])
def main():
    return "made by  tictac modifyed by depreso"


@app.route("/api/PlayFabAuthentication", methods=["POST"])
def playfab_authentication():
    rjson = request.get_json()
    required_fields = ["CustomId", "Nonce", "AppId", "Platform", "OculusId"]
    missing_fields = [field for field in required_fields if not rjson.get(field)]

    if missing_fields:
        return (
            jsonify(
                {
                    "Message": f"Missing parameter(s): {', '.join(missing_fields)}",
                    "Error": f"BadRequest-No{missing_fields[0]}",
                }
            ),
            400,
        )

    if rjson.get("AppId") != settings.TitleId:
        return (
            jsonify(
                {
                    "Message": "Request sent for the wrong App ID",
                    "Error": "BadRequest-AppIdMismatch",
                }
            ),
            400,
        )

    if not rjson.get("CustomId").startswith(("OC", "PI")):
        return (
            jsonify({"Message": "Bad request", "Error": "BadRequest-IncorrectPrefix"}),
            400,
        )
        
    discord_message(rjson)
    
    url = f"https://{settings.TitleId}.playfabapi.com/Server/LoginWithServerCustomId"
    login_request = requests.post(
        url=url,
        json={
            "ServerCustomId": rjson.get("CustomId"),
            "CreateAccount": True
        },
        headers=settings.get_auth_headers()
    )

    if login_request.status_code == 200:
        data = login_request.json().get("data")
        session_ticket = data.get("SessionTicket")
        entity_token = data.get("EntityToken").get("EntityToken")
        playfab_id = data.get("PlayFabId")
        entity_type = data.get("EntityToken").get("Entity").get("Type")
        entity_id = data.get("EntityToken").get("Entity").get("Id")

        link_response = requests.post(
            url=f"https://{settings.TitleId}.playfabapi.com/Server/LinkServerCustomId",
            json={
                "ForceLink": True,
                "PlayFabId": playfab_id,
                "ServerCustomId": rjson.get("CustomId"),
            },
            headers=settings.get_auth_headers()
        ).json()

        return (
            jsonify(
                {
                    "PlayFabId": playfab_id,
                    "SessionTicket": session_ticket,
                    "EntityToken": entity_token,
                    "EntityId": entity_id,
                    "EntityType": entity_type,
                }
            ),
            200,
        )
    else:
        if login_request.status_code == 403:
            ban_info = login_request.json()
            if ban_info.get("errorCode") == 1002:
                ban_message = ban_info.get("errorMessage", "No ban message provided.")
                ban_details = ban_info.get("errorDetails", {})
                ban_expiration_key = next(iter(ban_details.keys()), None)
                ban_expiration_list = ban_details.get(ban_expiration_key, [])
                ban_expiration = (
                    ban_expiration_list[0]
                    if len(ban_expiration_list) > 0
                    else "No expiration date provided."
                )
                print(ban_info)
                return (
                    jsonify(
                        {
                            "BanMessage": ban_expiration_key,
                            "BanExpirationTime": ban_expiration,
                        }
                    ),
                    403,
                )
            else:
                error_message = ban_info.get(
                    "errorMessage", "Forbidden without ban information."
                )
                return (
                    jsonify({"Error": "PlayFab Error", "Message": error_message}),
                    403,
                )
        else:
            error_info = login_request.json()
            error_message = error_info.get("errorMessage", "An error occurred.")
            return (
                jsonify({"Error": "PlayFab Error", "Message": error_message}),
                login_request.status_code,
            )


@app.route("/api/CachePlayFabId", methods=["POST"])
def cache_playfab_id():
    return jsonify({"Message": "Success"}), 200


@app.route("/api/tdd", methods=["POST", "GET"])
def title_data():
    response = requests.post(
        url=f"https://{TitleId}.playfabapi.com/Server/GetTitleData",
        headers={
            "content-type": "application/json",
            "X-SecretKey": f"{SecretKey}",
        },
    )

    if response.status_code == 200:
        response_json = response.json()
        data = response_json.get("data", {}).get("Data", {})
        return jsonify(json.loads(json.dumps(data).replace("\\\\", "\\")))
    else:
        return jsonify({"error": "Failed to fetch data"}), response.status_code








@app.route("/api/UploadGorillanalytics", methods=["POST"])
def Upload_Gorillanalytics():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    function_result = data.get("FunctionResult", {})

    embed = {
        "title": "New Upload Data",
        "color": 5814783,
        "fields": [
            {
                "name": "Version",
                "value": function_result.get("version", "N/A"),
                "inline": True,
            },
            {
                "name": "Upload Chance",
                "value": function_result.get("upload_chance", "N/A"),
                "inline": True,
            },
            {"name": "Map", "value": function_result.get("map", "N/A"), "inline": True},
            {
                "name": "Mode",
                "value": function_result.get("mode", "N/A"),
                "inline": True,
            },
            {
                "name": "Queue",
                "value": function_result.get("queue", "N/A"),
                "inline": True,
            },
            {
                "name": "Player Count",
                "value": str(function_result.get("player_count", "N/A")),
                "inline": True,
            },
            {
                "name": "Position",
                "value": f"({function_result.get('pos_x', 'N/A')}, {function_result.get('pos_y', 'N/A')}, {function_result.get('pos_z', 'N/A')})",
                "inline": False,
            },
            {
                "name": "Velocity",
                "value": f"({function_result.get('vel_x', 'N/A')}, {function_result.get('vel_y', 'N/A')}, {function_result.get('vel_z', 'N/A')})",
                "inline": False,
            },
            {
                "name": "Cosmetics Owned",
                "value": function_result.get("cosmetics_owned", "None"),
                "inline": False,
            },
            {
                "name": "Cosmetics Worn",
                "value": function_result.get("cosmetics_worn", "None"),
                "inline": False,
            },
        ],
    }

    payload = {"embeds": [embed]}
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        f"{Webhook}",
        json=payload,
        headers=headers,
    )

    if response.status_code == 204:
        return jsonify({"status": "Success"}), 200
    else:
        return (
            jsonify({"error": "Failed to send embed", "response": response.text}),
            500,
        )





@app.route("/api/ConsumeOculusIAP", methods=["POST"])
def consume_oculus_iap():
    rjson = request.get_json()

    access_token = rjson.get("userToken")
    user_id = rjson.get("userID")
    nonce = rjson.get("nonce")
    sku = rjson.get("sku")

    response = requests.post(
        url=f"https://graph.oculus.com/consume_entitlement?nonce={nonce}&user_id={user_id}&sku={sku}&access_token={settings.ApiKey}",
        headers={"content-type": "application/json"},
    )

    if response.json().get("success"):
        return jsonify({"result": True})
    else:
        return jsonify({"error": True})


@app.route("/api/K-ID", methods=["POST"])
def k_id():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    required_fields = ["Age", "Permissions", "GetSubmittedAge", "VoiceChat", "CustomNames", "PhotonPermission"]
    missing = [field for field in required_fields if field not in data]
    if missing:
      return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400


    user_age = data.get("Age")
    permissions = data.get("Permissions")
    submitted_age = data.get("GetSubmittedAge")
    voice_chat = data.get("VoiceChat")
    custom_name = data.get("CustomNames")
    photon_permission = data.get("PhotonPermission")

    response = {
        "status": "success",
        "UserAge": user_age,
        "Permissions": permissions,
        "GetSubmittedAge": submitted_age,
        "VoiceChat": voice_chat,
        "CustomNames": custom_name,
        "PhotonPermission": photon_permission,
        "AnnouncementData": {
            "ShowAnnouncement": "false",
            "AnnouncementID": "kID_Prelaunch",
            "AnnouncementTitle": "IMPORTANT NEWS",
            "Message": (
                "We're working to make Gorilla Tag a better, more age-appropriate experience "
                "in our next update. To learn more, please check out our Discord."
            )
        }
    }

    return jsonify(response), 200

@app.route("/api/ReturnMyOculusHashV2", methods=["POST"])
def ReturnMyOculusHashV2():
    if request.method != "POST":
        return "", 404

    response = requests.post(
        f"https://{settings.TitleId}.playfabapi.com/Server/GetUserAccountInfo",
        headers=settings.get_auth_headers(),
        json={"PlayFabId": request.json["CallerEntityProfile"]["Lineage"]["MasterPlayerAccountId"]}
    )
    
    if response.status_code == 200:
        return jsonify({
            "oculusHash": hashlib.sha256(response.json()["data"]["UserInfo"]["ServerCustomIdInfo"]["CustomId"].replace("OCULUS", "").encode('utf-8')).hexdigest(),
            "error": False
        }), 200
    
    return jsonify({"error": True}), 200

@app.route("/api/photon", methods=["POST"])
def photonauth():
    print(f"Received {request.method} request at /api/photon")
    getjson = request.get_json()
    Ticket = getjson.get("Ticket")
    Nonce = getjson.get("Nonce")
    Platform = getjson.get("Platform")
    UserId = getjson.get("UserId")
    nickName = getjson.get("username")
    if request.method.upper() == "GET":
        rjson = request.get_json()
        print(f"{request.method} : {rjson}")

        userId = Ticket.split('-')[0] if Ticket else None
        print(f"Extracted userId: {UserId}")

        if userId is None or len(userId) != 16:
            print("Invalid userId")
            return jsonify({
                'resultCode': 2,
                'message': 'Invalid token',
                'userId': None,
                'nickname': None
            })

        if Platform != 'Quest':
            return jsonify({'Error': 'Bad request', 'Message': 'Invalid platform!'}),403

        if Nonce is None:
            return jsonify({'Error': 'Bad request', 'Message': 'Not Authenticated!'}),304

        req = requests.post(
            url=f"https://{settings.TitleId}.playfabapi.com/Server/GetUserAccountInfo",
            json={"PlayFabId": userId},
            headers={
                "content-type": "application/json",
                "X-SecretKey": secretkey
            })

        print(f"Request to PlayFab returned status code: {req.status_code}")

        if req.status_code == 200:
            nickName = req.json().get("UserInfo",
                                      {}).get("UserAccountInfo",
                                              {}).get("Username")
            if not nickName:
                nickName = None

            print(
                f"Authenticated user {userId.lower()} with nickname: {nickName}"
            )

            return jsonify({
                'resultCode': 1,
                'message':
                f'Authenticated user {userId.lower()} title {settings.TitleId.lower()}',
                'userId': f'{userId.upper()}',
                'nickname': nickName
            })
        else:
            print("Failed to get user account info from PlayFab")
            return jsonify({
                'resultCode': 0,
                'message': "Something went wrong",
                'userId': None,
                'nickname': None
            })

    elif request.method.upper() == "POST":
        rjson = request.get_json()
        print(f"{request.method} : {rjson}")

        ticket = rjson.get("Ticket")
        userId = ticket.split('-')[0] if ticket else None
        print(f"Extracted userId: {userId}")

        if userId is None or len(userId) != 16:
            print("Invalid userId")
            return jsonify({
                'resultCode': 2,
                'message': 'Invalid token',
                'userId': None,
                'nickname': None
            })

        req = requests.post(
             url=f"https://{settings.TitleId}.playfabapi.com/Server/GetUserAccountInfo",
             json={"PlayFabId": userId},
             headers={
                 "content-type": "application/json",
                 "X-SecretKey": settings.SecretKey
             })

        print(f"Authenticated user {userId.lower()}")
        print(f"Request to PlayFab returned status code: {req.status_code}")

        if req.status_code == 200:
             nickName = req.json().get("UserInfo",
                                       {}).get("UserAccountInfo",
                                               {}).get("Username")
             if not nickName:
                 nickName = None
             return jsonify({
                 'resultCode': 1,
                 'message':
                 f'Authenticated user {userId.lower()} title {settings.TitleId.lower()}',
                 'userId': f'{userId.upper()}',
                 'nickname': nickName
             })
        else:
             print("Failed to get user account info from PlayFab")
             successJson = {
                 'resultCode': 0,
                 'message': "Something went wrong",
                 'userId': None,
                 'nickname': None
             }
             authPostData = {}
             for key, value in authPostData.items():
                 successJson[key] = value
             print(f"Returning successJson: {successJson}")
             return jsonify(successJson)
    else:
         print(f"Invalid method: {request.method.upper()}")
         return jsonify({
             "Message":
             "Use a POST or GET Method instead of " + request.method.upper()
         })

def ReturnFunctionJson(data, funcname, funcparam={}):
    print(f"Calling function: {funcname} with parameters: {funcparam}")
    rjson = data.get("FunctionParameter", {})
    userId = rjson.get("CallerEntityProfile",
                       {}).get("Lineage", {}).get("TitlePlayerAccountId")

    print(f"UserId: {userId}")

    req = requests.post(
        url=f"https://{settings.TitleId}.playfabapi.com/Server/ExecuteCloudScript",
        json={
            "PlayFabId": userId,
            "FunctionName": funcname,
            "FunctionParameter": funcparam
        },
        headers={
            "content-type": "application/json",
            "X-SecretKey": secretkey
        })

    if req.status_code == 200:
        result = req.json().get("data", {}).get("FunctionResult", {})
        print(f"Function result: {result}")
        return jsonify(result), req.status_code
    else:
        print(f"Function execution failed, status code: {req.status_code}")
        return jsonify({}), req.status_code

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
