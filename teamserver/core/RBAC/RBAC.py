from flask_rbac import RBAC, Role, UserMixin

class User(UserMixin):
    def __init__(self, id, role_name):
        self.id = id
        self.role = Role.get(role_name)

def assignRolesToUser(user, role):
    users = {
        '1': User('1', 'admin'),
        '2': User('2', 'editor'),
        '3': User('3', 'viewer')
    }

def get_current_user():
    identity = get_jwt_identity()
    return users.get(identity)

