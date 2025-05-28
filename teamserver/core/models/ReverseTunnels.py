from flask import Blueprint
from flask import Response, request
from flask_jwt_extended import jwt_required, get_jwt_identity

import flask_mongoengine
from core.database.models import ReverseTunnels

from core.proxies.socks4a.server.SOCKS4aProxyServer import main

reverse_tunnels_blueprint = Blueprint('reverse_tunnels', __name__)
@reverse_tunnels_blueprint.route('/api/latest/reverse_tunnels', methods=['GET'])
@jwt_required()
def list_reverse_tunnels():
    reverse_tunnels = ReverseTunnels.query.all()
    return reverse_tunnels

@reverse_tunnels_blueprint.route('/api/latest/reverse_tunnels', methods=['POST'])
@jwt_required()
def get_reverse_tunnel():
    body = request.get_json()
    id = body['id']
    reverse_tunnel = ReverseTunnels.query.filter_by(id=id).first()
    return reverse_tunnel

@reverse_tunnels_blueprint.route('/api/latest/reverse_tunnels', methods=['PUT'])
@jwt_required()
def start_reverse_tunnel():
    try:
        body = request.get_json()
        listener = body['listener']
        socksport = body['socksport']
        mgmtsport = body['mgmtsport']
        listeningport = body['listeningport']

        main(socksport=socksport, mgmtsport=mgmtsport, listeningport=listeningport)

        dbdata = {
            "teamserver_reverse_tunnel_listener": listener,
            "teamserver_reverse_tunnel_status": True,
            "teamserver_reverse_tunnel_listening_port": listeningport,
            "teamserver_reverse_tunnel_mgmt_port": mgmtsport,
            "teamserver_reverse_tunnel_socks_port": socksport
        }
        ReverseTunnels(**dbdata).save()
        return {"status": f"SOCK Proxy Server started on port {socksport}"}
    except Exception as e:
        return {"error": f"Error from starting Socks Proxy Server: {str(e)}"}

"""@reverse_tunnels_blueprint.route('/api/latest/reverse_tunnels', methods=['DELETE'])
@jwt_required
def delete_reverse_tunnel(id):
    args = particle_args.parse_args()
    host = args['host']
    port = args['port']
    module = args['module']

    listener = ReverseTunnels(
        id=id,
        host=host,
        port=port,
        module=module
    )

    db.add(listener)
    db.commit()"""