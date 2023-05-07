import redis
import json

red = redis.StrictRedis('localhost',6379,password="m0bdat",charset="utf-8",decode_responses=True)
res = {
     "Task":"liver",
     "pacs_url": "",
     "study_id": "1234",
     "mask":2
}
red.publish("test",json.dumps(res))
