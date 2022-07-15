import argparse
import logging
import os
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException
from pymongo import MongoClient
from bson.objectid import ObjectId
from CRS_user_with_previous_action import crs_with_previous_action
from dotenv import load_dotenv
load_dotenv()


# creating the default parser arguments
def create_argument_parser():
    parser = argparse.ArgumentParser(description='parser arguments')

    parser.add_argument(
        '-H', '--host',
        type=str,
        default='0.0.0.0',
        help='hostname to listen on')

    parser.add_argument(
        '-P', '--port',
        type=int,
        default=5000,
        help='server port')
    parser.add_argument(
        '--debug',
        action='store_true',
        default=False,
        help='if given, enable or disable debug mode')

    return parser


# creating_app using the flask
def create_app(test_config=None):
    # create and configure the app
    flask_app = Flask(__name__)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        # load configs
        config_class = os.getenv('FK_APP_CONFIG',
                                 'configs.DefaultConfig')
        flask_app.config.from_object(config_class)

    else:
        # load the test config if passed in
        flask_app.config.from_mapping(test_config)

    business_client = flask_app.config['BUSINESS_CLIENT']
    client = MongoClient(os.environ['DB_URI'])
    db = client[os.environ['DB_NAME']]

    client_collection = db['clients']

    @flask_app.errorhandler(ValueError)
    def handle_value_error(ex):
        flask_app.logger.error(f"{ex}")
        response = jsonify({
            "message": f"{ex}"
        })
        response.status_code = 404
        return response

    @flask_app.errorhandler(KeyError)
    def handle_key_error(ex):
        flask_app.logger.error(f"{ex}")
        response = jsonify({
            "message": f"{ex}"
        })
        response.status_code = 404
        return response

    @flask_app.errorhandler(HTTPException)
    def handle_exception(ex):
        flask_app.logger.error(str(ex))
        response = jsonify({
            "message": ex.description
        })
        response.status_code = ex.code
        return response


    @flask_app.errorhandler(Exception)
    def handle_exception(ex):
        flask_app.logger.exception(f"Unexpected runtime error: {ex}")
        response = jsonify({
            "message": "Unexpected runtime error"
        })
        response.status_code = 500
        return response

    # health check
    @flask_app.route('/', methods=['GET', 'POST'])
    def hello():
        return "Hello from CRS model serving app"

    # predict channel relevance score
    @flask_app.route(f'/{business_client}/channelrelevancescore/api/v1/<pattern_level>', methods=['POST'])
    def get_channel_relevance_score(pattern_level):
        output_list = []
        req_json = request.get_json() if request.is_json else dict()
        users = req_json.get('users', []) if req_json else []
        for user in users:
            # checking the input request format
            if not user.__contains__('clientId') or not user.__contains__('channels'):
                return jsonify({"Code": 400, "Message": "Invalid Input"})

            # Checking the client id details in the database.
            try:
                data = client_collection.find_one({"_id": ObjectId(user['clientId'])}, {"_id": 1})
            except:
                data = None
            if not data:
                return jsonify({"Code": 400, "Message": "The client id is not available. Please check!"})
            if data:
                predictions = crs_with_previous_action(user, pattern_level)

            output_list.append(predictions)

        flask_app.config['JSON_SORT_KEYS'] = False
        rsp = jsonify(output_list)
        flask_app.config['JSON_SORT_KEYS'] = True
        return rsp

    # return app object
    return flask_app


if __name__ == '__main__':
    "run server"

    arg_parser = create_argument_parser()
    cmdline_args = arg_parser.parse_args()

    logging.getLogger().setLevel(logging.INFO)

    app = create_app()
    app.run(host=cmdline_args.host, port=cmdline_args.port, debug=cmdline_args.debug)
