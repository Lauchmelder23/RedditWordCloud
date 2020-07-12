import argparse
import json

parser = argparse.ArgumentParser(description="Creates a config.json from your client_id and secret")
parser.add_argument("client_id", type=str)
parser.add_argument("secret", type=str)

args = parser.parse_args()

data = {"client_id": args.client_id, "secret": args.secret}
with open("config.json") as file:
    json.dump(data, file)
