import json
from http.server import HTTPServer, BaseHTTPRequestHandler

import json
from http.server import HTTPServer, BaseHTTPRequestHandler

USERS_LIST = [
    {
        "id": 1,
        "username": "theUser",
        "firstName": "John",
        "lastName": "James",
        "email": "john@email.com",
        "password": "12345",
    }
]


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def _set_response(self, status_code=200, body=None):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(body if body else {}).encode('utf-8'))

    def _pars_body(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        return json.loads(self.rfile.read(content_length).decode('utf-8'))  # <--- Gets the data itself

    def do_GET(self):
        global USERS_LIST

        if self.path == '/reset':
            USERS_LIST = [
                {
                 "id": 1,
                 "username": "theUser",
                 "firstName": "John",
                 "lastName": "James",
                 "email": "john@email.com",
                 "password": "12345",
                }
            ]
            self._set_response(200, {"message": "Reset successful"})

        elif self.path == '/users':
            self._set_response(200, USERS_LIST)

        elif self.path.startswith('/user/'):
            requested_username = self.path.split('/')[-1]
            found_user = None
            for user in USERS_LIST:
                if user.get('username') == requested_username:
                    found_user = user
                    break

            if found_user:
                self._set_response(200, found_user)
            else:
                self._set_response(400, {'error': 'User not found'})

        else:
            self._set_response(404, {'error': 'Endpoint not found'})

    def do_POST(self):
        global USERS_LIST

        try:
            body = self._pars_body()
        except Exception:
            self._set_response(400, {})
            return

        def valid_user(user_data):
            if not isinstance(user_data, dict):
                return False

            expected_schema = {
                "id": int,
                "username": str,
                "firstName": str,
                "lastName": str,
                "email": str,
                "password": str
            }

            if len(user_data) != len(expected_schema):
                return False

            for k, v in expected_schema.items():
                if k not in user_data or not isinstance(user_data[k], v):
                    return False

            return True

        if self.path == '/user':
            if not valid_user(body):
                self._set_response(400, {})
                return

            if any(user.get('id') == body.get('id') for user in USERS_LIST):
                self._set_response(400, {})
                return

            USERS_LIST.append(body)
            self._set_response(201, body)

        elif self.path == '/user/createWithList':
            if not isinstance(body, list):
                self._set_response(400, {})
                return

            for user_data in body:
                if not valid_user(user_data):
                    self._set_response(400, {})
                    return

            new_ids = [user.get("id") for user in body]
            existing_ids = [user.get("id") for user in USERS_LIST]

            if any(new_id in existing_ids for new_id in new_ids):
                self._set_response(400, {})
                return

            USERS_LIST.extend(body)
            self._set_response(201, body)

        else:
            self._set_response(404, {'error': 'Endpoint not found'})

    def do_PUT(self):
        global USERS_LIST

        try:
            body = self._pars_body()
        except Exception:
            self._set_response(400, {"error": "not valid request data"})
            return

        def valid_put_data(data):
            if not isinstance(data, dict):
                return False

            expected_schema = {
                "username": str,
                "firstName": str,
                "lastName": str,
                "email": str,
                "password": str
            }

            if len(data) != len(expected_schema):
                return False

            for k, v in expected_schema.items():
                if k not in data or not isinstance(data[k], v):
                    return False

            return True

        if self.path.startswith('/user/'):
            id_str = self.path.split('/')[-1]

            try:
                user_id = int(id_str)
            except ValueError:
                self._set_response(404, {"error": "User not found"})
                return

            if not valid_put_data(body):
                self._set_response(400, {"error": "not valid request data"})
                return

            found_user = None
            for user in USERS_LIST:
                if user.get('id') == user_id:
                    found_user = user
                    break

            if found_user:
                for key, value in body.items():
                    found_user[key] = value
                self._set_response(200, found_user)
            else:
                self._set_response(404, {"error": "User not found"})

        else:
            self._set_response(404, {"error": "Endpoint not found"})

    def do_DELETE(self):
        global USERS_LIST

        if self.path.startswith('/user/'):
            id_str = self.path.split('/')[-1]

            try:
                user_id = int(id_str)
            except ValueError:
                self._set_response(404, {"error": "User not found"})
                return

            found_user = None
            for user in USERS_LIST:
                if user.get('id') == user_id:
                    found_user = user
                    break

            if found_user:
                USERS_LIST.remove(found_user)
                self._set_response(200, {})
            else:
                self._set_response(404, {"error": "User not found"})

        else:
            self._set_response(404, {"error": "User not found"})


def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, host='localhost', port=8000):
    server_address = (host, port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on {host}:{port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    print("\nStopping server...")
    httpd.server_close()


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()