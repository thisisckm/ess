from xmlrpc import client


class Odoo:

    def __init__(self, url, db, username, password):
        self.url = url
        self.db = db
        self.username = username
        self.password = password

        models = client.ServerProxy('{}/xmlrpc/common'.format(url))
        self.uid = models.authenticate(db, username, password, {})        

    def search(self, model: str, condition: list) -> list:
        models_object = client.ServerProxy('{}/xmlrpc/object'.format(self.url))
        return models_object.execute_kw(self.db, self.uid, self.password, model, 'search', [condition])

    def execute(self, model: str, function_name: str, function_parameter: list):
        models_object = client.ServerProxy('{}/xmlrpc/object'.format(self.url))
        return models_object.execute_kw(self.db, self.uid, self.password, model, function_name, [function_parameter])

    def write(self, model: str, ids: list, data: dict):
        models_object = client.ServerProxy('{}/xmlrpc/object'.format(self.url))
        models_object.execute_kw(self.db, self.uid, self.password, model, 'write',
                                        [ids, data])
