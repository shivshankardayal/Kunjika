import kunjika
from flask import Flask, render_template

def handle_edit(element):
    ##print element
    element = element[3:]
    arg_list = element.split('-')
    qid = 0
    cid = 0
    aid = 0

    if len(arg_list) == 1:
        qid = arg_list[0]
    elif len(arg_list) == 2:
        qid = arg_list[0]
        aid = arg_list[1]
    else:
        qid = arg_list[0]
        aid = arg_list[1]
        cid = arg_list[2]
        
    question = kunjika.qb.get(qid).value

    return [question, qid, aid, cid]
