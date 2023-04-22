from waitress import serve
import main_server
serve(main_server.app, host='localhost', port=8000)