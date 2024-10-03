from uagents import Agent, Task
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import pandas as pd
import threading


class CommunicationAgent(Agent):
    def __init__(
        self,
        name,
        data_file,
        prediction_agent,
        host="0.0.0.0",
        port=5000,
        jwt_secret="your-secret-key",
    ):
        super().__init__(name)
        self.data_file = data_file
        self.prediction_agent = (
            prediction_agent  # Reference to PredictionAgent to get latest prediction
        )
        self.host = host
        self.port = port
        self.app = Flask(name)
        self.app.config["JWT_SECRET_KEY"] = jwt_secret
        self.jwt = JWTManager(self.app)
        CORS(self.app)  # Configure appropriately for production
        self.data_lock = threading.Lock()
        self.setup_routes()

    def setup_routes(self):
        @self.app.route("/login", methods=["POST"])
        def login():
            from flask import request

            username = request.json.get("username", None)
            password = request.json.get("password", None)
            # Implement your user verification logic here
            if username != "admin" or password != "password":
                return jsonify({"msg": "Bad username or password"}), 401

            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token), 200

        @self.app.route("/data", methods=["GET"])
        @jwt_required()
        def get_data():
            with self.data_lock:
                try:
                    df = pd.read_csv(self.data_file)
                    data = df.to_dict(orient="records")
                    return jsonify(data), 200
                except Exception as e:
                    return jsonify({"error": str(e)}), 500

        @self.app.route("/prediction", methods=["GET"])
        @jwt_required()
        def get_prediction():
            if self.prediction_agent.latest_prediction is not None:
                return (
                    jsonify({"prediction": self.prediction_agent.latest_prediction}),
                    200,
                )
            else:
                return jsonify({"prediction": "No prediction available yet."}), 200

    def run(self):
        self.app.run(host=self.host, port=self.port)


if __name__ == "__main__":
    from prediction_agent import PredictionAgent

    prediction_agent = PredictionAgent(
        name="PredictionAgent",
        data_file="../data.csv",
        model_file="../model.pkl",
        interval=300,  # 5 minutes
    )
    communication_agent = CommunicationAgent(
        name="CommunicationAgent",
        data_file="../data.csv",
        prediction_agent=prediction_agent,
        host="0.0.0.0",
        port=5000,
        jwt_secret="your-secret-key",
    )
    # Run agents in separate threads
    import threading

    t1 = threading.Thread(target=prediction_agent.run)
    t2 = threading.Thread(target=communication_agent.run)

    t1.start()
    t2.start()

    t1.join()
    t2.join()
