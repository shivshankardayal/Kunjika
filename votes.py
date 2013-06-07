#from kunjika import qb, cb
import json
from flask import request, g, jsonify
import re

def handle_vote(request):
    id = request.args.get('id')
    vote_count = request.args.get('vote_count')
    direction = request.args.get('direction')

    print request

    id = id[3:]

    return jsonify({'id':id})
