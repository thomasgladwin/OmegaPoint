"""websockets_api_example.py — Monitor execution via WebSocket, download via /history."""

import websocket  # pip install websocket-client
import uuid
import json
import urllib.request
import urllib.parse

class ChatBot:
    def __init__(self):
        self.SERVER_ADDRESS = "127.0.0.1:8188"
        self.client_id = str(uuid.uuid4())
        workflow_json_file = 'llm_qwen3_text_gen.json'
        with open(workflow_json_file, 'r') as f:
            self.workflow = json.load(f)

    def queue_prompt(self, prompt, prompt_id):
        p = {"prompt": prompt, "client_id": self.client_id, "prompt_id": prompt_id}
        data = json.dumps(p).encode("utf-8")
        req = urllib.request.Request(
            f"http://{self.SERVER_ADDRESS}/prompt", data=data
        )
        urllib.request.urlopen(req)

    def get_history(self, prompt_id):
        with urllib.request.urlopen(
            f"http://{self.SERVER_ADDRESS}/history/{prompt_id}"
        ) as response:
            return json.loads(response.read())

    def get_response(self, ws, prompt):
        prompt_id = str(uuid.uuid4())
        self.queue_prompt(prompt, prompt_id)

        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message["type"] == "executing":
                    data = message["data"]
                    if data["node"] is None and data["prompt_id"] == prompt_id:
                        break  # Execution done
            #
            #print(message)
            continue
        history = self.get_history(prompt_id)[prompt_id]
        return history['outputs']['5']['text'][0]

    def send_query(self, prompt_text):
        prompt = self.workflow
        prompt['7']['inputs']['prompt'] = prompt_text
        ws = websocket.WebSocket()
        ws.connect(f"ws://{self.SERVER_ADDRESS}/ws?clientId={self.client_id}")
        response = self.get_response(ws, prompt)
        ws.close()
        return response

