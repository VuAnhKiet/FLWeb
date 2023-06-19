from waitress import serve
import client
serve(client.app, host='localhost', port=8001)