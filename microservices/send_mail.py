from flask import Flask, request, jsonify, Response
from werkzeug.exceptions import BadRequest
import logging
from flask_cors import CORS


# Flask constructor takes the name of 
# current module (__name__) as argument.
app = Flask(__name__)
CORS(app)   # Allows all origins
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_json_content(my_request):
    try:
        data = my_request.get_json()
        if data is None:
            logging.error('Invalid JSON')
            raise BadRequest('Invalid JSON')
        return data, ''
    except BadRequest as e:
        logging.error('Invalid JSON')
        return {}, jsonify({'error': 'Invalid JSON'})
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return {}, jsonify({'error': str(e)})


@app.route('/api/send_email/', methods=['POST'])
def send_email():
    if request.method == 'POST':
        if request.content_type == 'application/json':
            content, msg = get_json_content(request)
            if len(content) == 0:
                return msg, 400
            # Display in log the content gotten
            logging.info(f"Content gotten: {str(content)}")
        return jsonify({'mensaje': f'Correo Enviado'}), 200
    else:
        logging.error('Method not supported')
        return jsonify({'error': 'Method not supported'}), 400

# main driver function
if __name__ == '__main__':
    # on the local development server.
    app.run(debug=False, port=5000)