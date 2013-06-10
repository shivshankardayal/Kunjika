import kunjika
from flask import jsonify, g


def generate_url(title):
    length = len(title)
    prev_dash = False
    url = ""
    for i in range(length):
        c = title[i]
        if (c >= 'a' and c <= 'z') or (c >= '0' and c <= '9'):
            url += c
            prev_dash = False
        elif c >= 'A' and c <= 'Z':
            url += c
        elif c == ' ' or c == ',' or c == '.' or c == '/' or c == '\\' or c == '-' or c == '_' or c == '=':
            if not prev_dash and len(url) > 0:
                url += '-'
                prev_dash = True
        elif ord(c) > 160:
            c = c.decode('UTF-8').lower()
            url += c
            prev_dash = False
        if i == 80:
            break

    if prev_dash is True:
        url = url[:-1]

    return url


def accept_answer(idntfr):

    idntfr = idntfr[4:]

    idntfr_list = idntfr.split('-')
    qid = idntfr_list[0]
    aid = idntfr_list[1]

    question = kunjika.qb.get(qid).value

    voter = kunjika.cb.get(g.user.id)

    if int(question['content']['op']) != g.user.id:
        return jsonify({"success": False})
    for answer in question['answers']:
        if answer['aid'] != int(aid):
            if answer['best'] is True:
                answer['poster']['rep'] -= 10
                voter['rep'] -= 2
            answer['best'] = False
        else:
            answer['best'] = True
            answer['poster']['rep'] += 10
            voter['rep'] += 2

    kunjika.qb.replace(qid, question)

    return jsonify({"success": True})

def handle_favorite(idntfr):

    qid = idntfr[3:]

    print qid
    question = kunjika.qb.get(qid).value
    user = kunjika.cb.get(str(g.user.id)).value

    print question
    print user
    if 'users_fav' in question:
        if g.user.id in question['users_fav']:
            question['users_fav'].remove(g.user.id)
        else:
            question['users_fav'].append(g.user.id)
    else:
        question['users_fav'] = []
        question['users_fav'].append(g.user.id)

    if 'fav_q' in user:
        if qid in user['fav_q']:
            user['fav_q'].remove(qid)
        else:
            user['fav_q'].append(qid)
    else:
        user['fav_q'] = []
        user['fav_q'].append(qid)

    kunjika.cb.replace(qid, user)
    kunjika.qb.replace(str(g.user.id), question)

    return jsonify({"success": True})