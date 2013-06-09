import kunjika
from flask import g, jsonify
from pprint import pprint

def handle_vote(request):
    id = request.args.get('id')
    vote_count = request.args.get('vote_count')
    direction = request.args.get('direction')

    id = id[3:]
    print id
    vote_dict = {}
    vote_dict['id'] = id

    id_list = id.split('-')

    qid = 0
    aid = 0

    if len(id_list) == 2:
        qid = id_list[0]
        aid = id_list[1]
    elif len(id_list) == 1:
        qid = id_list[0]

    if aid != 0:
        question = kunjika.qb.get(qid).value
        answer = question['answers'][int(aid) - 1]
        if answer['poster'] == g.user.id:
            return jsonify({'vote_count':answer['votes']})
        else:
            user = kunjika.cb.get(str(g.user.id)).value
            pprint(user)
            if 'votes' in user:
                for votes in user['votes']:
                    if votes['id'] == id:
                        if direction == 'up' and votes['value'] != 1:
                            answer['votes'] += 1
                            votes['value'] += 1
                            kunjika.cb.replace(str(g.user.id), user)
                            kunjika.qb.replace(str(qid), question)
                            return jsonify({'vote_count':answer['votes']})
                        elif direction == 'up' and votes['value'] == 1:
                            return jsonify({'vote_count':answer['votes']})
                        elif direction == 'down' and votes['value'] != -1:
                            answer['votes'] -= 1
                            votes['value'] -= 1
                            kunjika.cb.replace(str(g.user.id), user)
                            kunjika.qb.replace(str(qid), question)
                            return jsonify({'vote_count':answer['votes']})
                        elif direction == 'down' and votes['value'] == -1:
                            return jsonify({'vote_count':answer['votes']})

                vote = {}
                vote['id'] = id
                if direction == 'up' and votes['value'] != 1:
                    answer['votes'] += 1
                    vote['value'] = 1
                    user['votes'].append(vote)
                    kunjika.cb.replace(str(g.user.id), user)
                    kunjika.qb.replace(str(qid), question)
                    return jsonify({'vote_count':answer['votes']})
                elif direction == 'up' and votes['value'] == 1:
                    return jsonify({'vote_count':answer['votes']})
                elif direction == 'down' and votes['value'] != -1:
                    answer['votes'] -= 1
                    votes['value'] = -1
                    user['votes'].append(vote)
                    kunjika.cb.replace(str(g.user.id), user)
                    kunjika.qb.replace(str(qid), question)
                    return jsonify({'vote_count':answer['votes']})
                elif direction == 'down' and votes['value'] == -1:
                    return jsonify({'vote_count':answer['votes']})
                else:
                    votes = []
                    vote = {}
                    vote['id'] = id
                    if direction == 'up':
                        vote['value'] = 1
                        answer['votes'] += 1
                    else:
                        vote['value'] = -1
                        answer['votes'] -= 1
                        
                    votes.append(vote)

                    user['votes'] = votes
                    
                    kunjika.cb.replace(str(g.user.id), user)
                    kunjika.qb.replace(str(qid), question)
                    
                    return jsonify({'vote_count':answer['votes']})

    else:
        #print "aid= " + str(aid)
        question = kunjika.qb.get(qid).value
        if str(g.user.id) == question['content']['op']:
            return jsonify({'vote_count':question['votes']})
        else:
            user = kunjika.cb.get(str(g.user.id)).value
            if 'votes' in user:
                for votes in user['votes']:
                    if votes['id'] == id:
                        if direction == 'up' and votes['value'] != 1:
                            question['votes'] += 1
                            votes['value'] += 1
                            kunjika.cb.replace(str(g.user.id), user)
                            kunjika.qb.replace(str(qid), question)
                            return jsonify({'vote_count':question['votes']})
                        elif direction == 'up' and votes['value'] == 1:
                            return jsonify({'vote_count':question['votes']})
                        elif direction == 'down' and votes['value'] != -1:
                            question['votes'] -= 1
                            votes['value'] -= 1
                            kunjika.cb.replace(str(g.user.id), user)
                            kunjika.qb.replace(str(qid), question)
                            return jsonify({'vote_count':question['votes']})
                        elif direction == 'down' and votes['value'] == -1:
                            return jsonify({'vote_count':question['votes']})
                else:
                    vote = {}
                    vote['id'] = id
                    if direction == 'up' and votes['value'] != 1:
                        pprint(answer)
                        quesion['votes'] += 1
                        vote['value'] += 1
                        user['votes'].append(vote)
                        kunjika.cb.replace(str(g.user.id), user)
                        kunjika.qb.replace(str(qid), question)
                        return jsonify({'vote_count':question['votes']})
                    elif direction == 'up' and votes['value'] == 1:
                        return jsonify({'vote_count':question['votes']})
                    elif direction == 'down' and votes['value'] != -1:
                        question['votes'] -= 1
                        votes['value'] -= 1
                        user['votes'].append(vote)
                        kunjika.cb.replace(str(g.user.id), user)
                        kunjika.qb.replace(str(qid), question)
                        return jsonify({'vote_count':question['votes']})
                    elif direction == 'down' and votes['value'] == -1:
                        return jsonify({'vote_count':question['votes']})
            else:
                votes = []
                vote = {}
                vote['id'] = id
                if direction == 'up':
                    vote['value'] = 1
                    question['votes'] += 1
                else:
                    vote['value'] = -1
                    question['votes'] -= 1

                votes.append(vote)

                user['votes'] = votes

                kunjika.cb.replace(str(g.user.id), user)
                kunjika.qb.replace(str(qid), question)

                return jsonify({'vote_count':question['votes']})

