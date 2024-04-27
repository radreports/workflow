import redis
import json
import app.workflow as wf
# red = redis.StrictRedis('localhost',6379,password="m0bdat")
red = redis.StrictRedis('34.170.63.108',6379,password="m0nday",charset="utf-8",decode_responses=True)
sub = red.pubsub()
sub.subscribe("test")
for messages in sub.listen():
    msg = messages.get("data")
    if messages.get("type") == "message":
        msg = json.loads(msg)
        print("int input",msg)
        wf.process(msg)

    # print(type(msg),msg)
    # print("message::", json.loads(msg))
