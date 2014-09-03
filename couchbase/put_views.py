import os

os.system("curl -X GET -H 'Content-Type: application/json' 'http://username:password@127.0.0.1:8092/default/_design/dev_qa' -d @default.json")
os.system("curl -X GET -H 'Content-Type: application/json' 'http://username:password@127.0.0.1:8092/kunjika/_design/dev_qa' -d @kunjika.json")
os.system("curl -X GET -H 'Content-Type: application/json' 'http://username:password@127.0.0.1:8092/polls/_design/dev_qa' -d @polls.json")
os.system("curl -X GET -H 'Content-Type: application/json' 'http://username:password@127.0.0.1:8092/questions/_design/dev_qa' -d @questions.json")
os.system("curl -X GET -H 'Content-Type: application/json' 'http://username:password@127.0.0.1:8092/tags/_design/dev_qa' -d @tags.json")
