import json

from flask import Blueprint, request, Response
import sys
import socketserver, http.server
from threading import Thread
from queue import Queue
from flask_jwt_extended import jwt_required
import ssl

#from Listeners.HTTP.database.models import Listeners
#from Listeners.HTTP.http_listener import start_listener

from core.database.models import S3C2Listener, WebsocketListener
from core.Listeners.WebSocket.server import start_websocket_listener

listener_blueprint = Blueprint('listeners', __name__)
from waitress import serve
import multiprocessing

@listener_blueprint.route('/api/latest/listeners', methods=['GET'])
@jwt_required()
def list_listeners():
    listeners = S3C2Listener.objects().to_json()
    listeners = json.loads(listeners)
    if len(listeners) > 0:
        return {"Listeners": listeners}
    else:
        return {"Listeners": None}

@listener_blueprint.route('/api/latest/listeners', methods=['POST'])
@jwt_required()
def get_listener():
    #body = request.get_json()
    #listener_name = body['listener_name']
    #listener = Listeners.objects.get_or_404(listener_name=listener_name).to_json()
    #return Response(listener, mimetype="application/json", status=200)
    pass

@listener_blueprint.route('/api/latest/listeners', methods=['PUT'])
@jwt_required()
def set_listener():
    body = request.get_json()
    listener_name = body['listener_name']
    apiHost = body['listener_host']
    apiPort = int(body['listener_port'])
    if "databaseHost" in body:
        databaseHost = body['databaseHost']

    if "databasePort" in body:
        databasePort = body['databasePort']

    if "databaseName" in body:
        databaseName = body['databaseName']

    protocol = body['listener_protocol']

    if protocol == "HTTP":
        pass
        """try:
            p = multiprocessing.Process(target=start_listener, args=(apiHost, apiPort, databaseHost, databasePort, databaseName,))
            p.start()
            aws_creds = Listeners(**body).save()

            return {"status:" "started"}, 200
        except Exception as e:
            if "Tried to save duplicate unique keys" in str(e):
                return {"error": "Credentials Exist", 'status_code': 1337}

            return {"error": str(e)}, 500
        """
    elif protocol == "WebSocket":
        try:
            p = multiprocessing.Process(target=start_websocket_listener, args=(apiPort,None,None,))
            p.start()

            wsbody = {
                "listener_name": listener_name,
                "listener_host": apiHost,
                "listener_port": apiPort,
                "listener_protocol": protocol,
                "listener_status": "running"
            }

            if "listener_ssl_cert_path" in body:
                wsbody["listener_ssl_cert_path"] = body["listener_ssl_cert_path"]

            if "listener_ssl_key_path" in body:
                wsbody["listener_ssl_key_path"] = body["listener_ssl_key_path"]

            try:
                WebsocketListener(**wsbody).save()
                return {"status:": "started"}, 200
            except Exception as e:
                if "Tried to save duplicate unique keys" in str(e):
                    return {"error": "Listener Exist"}, 1337
                else:
                    return {"error": str(e)}, 500
        except Exception as e:
            return {"error": str(e)}, 500

@listener_blueprint.route('/api/latest/listeners', methods=['DELETE'])
@jwt_required()
def delete_listener():
    try:
        body = request.get_json()
        listener_name = body['listener_bucket_name']
        S3C2Listener.objects.get_or_404(listener_bucket_name=listener_name).delete()
        return '', 200
    except Exception as e:
        return {"error": str(e)}