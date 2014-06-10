# Copyright (c) 2013 Shiv Shankar Dayal
# This file is part of Kunjika.
#
# Kunjika is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# Kunjika is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.

import kunjika
from flask import g, jsonify
from p#print import p#print


def handle_vote(request):
    id = request.args.get('id')
    vote_count = request.args.get('vote_count')
    direction = request.args.get('direction')
    ##print id
    ##print direction
    id = id[3:]
    ###print id
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

    question = kunjika.qb.get(qid).value

    if aid != 0:
        answer = question['answers'][int(aid) - 1]
        if answer['poster'] == g.user.id:
            return jsonify({'vote_count': answer['votes']})
        else:
            user = kunjika.cb.get(str(g.user.id)).value
            receiver = kunjika.cb.get(str(answer['poster'])).value
            #for votes in user['votes']:
            for votes in answer['votes_list']:
                if votes['uid'] == g.user.id:
                    if direction == 'up' and votes['value'] != 1:
                        answer['votes'] += 1
                        votes['value'] += 1
                        user['rep'] += 1
                        receiver['rep'] += 2

                        if votes['value'] == 1:
                            user['votes_count']['up'] += 1
                            user['votes_count']['answers'] += 1
                        elif votes['value'] == 0:
                            user['votes_count']['down'] -= 1
                            user['votes_count']['answers'] -= 1

                        kunjika.cb.replace(str(g.user.id), user)
                        kunjika.cb.replace(str(answer['poster']), receiver)
                        kunjika.qb.replace(str(qid), question)
                        return jsonify({'vote_count': answer['votes']})
                    elif direction == 'up' and votes['value'] == 1:
                        return jsonify({'vote_count': answer['votes']})
                    elif direction == 'down' and votes['value'] != -1:
                        answer['votes'] -= 1
                        votes['value'] -= 1
                        user['rep'] -= 1
                        receiver['rep'] -= 2

                        if votes['value'] == -1:
                            user['votes_count']['down'] += 1
                            user['votes_count']['answers'] += 1
                        elif votes['value'] == 0:
                            user['votes_count']['up'] -= 1
                            user['votes_count']['answers'] -= 1

                        kunjika.cb.replace(str(g.user.id), user)
                        kunjika.cb.replace(str(answer['poster']), receiver)
                        kunjika.qb.replace(str(qid), question)
                        return jsonify({'vote_count': answer['votes']})
                    elif direction == 'down' and votes['value'] == -1:
                        return jsonify({'vote_count': answer['votes']})

            vote = {}
            vote['uid'] = g.user.id
            vote['value'] = 0
            if direction == 'up':
                answer['votes'] += 1
                vote['value'] = 1
                user['rep'] += 1
                receiver['rep'] += 2
                user['votes_count']['up'] += 1
                user['votes_count']['answers'] += 1

                answer['votes_list'].append(vote)
                kunjika.cb.replace(str(g.user.id), user)
                kunjika.cb.replace(str(answer['poster']), receiver)
                kunjika.qb.replace(str(qid), question)
                return jsonify({'vote_count': answer['votes']})
            else:
                answer['votes'] -= 1
                vote['value'] = -1
                user['rep'] -= 1
                receiver['rep'] -= 2
                user['votes_count']['down'] += 1
                user['votes_count']['answers'] += 1

                answer['votes_list'].append(vote)

                kunjika.cb.replace(str(g.user.id), user)
                kunjika.cb.replace(str(answer['poster']), receiver)
                kunjika.qb.replace(str(qid), question)
                return jsonify({'vote_count': answer['votes']})

    else:
        if str(g.user.id) == question['content']['op']:
            return jsonify({'vote_count': question['votes']})
        else:
            user = kunjika.cb.get(str(g.user.id)).value
            receiver = kunjika.cb.get(question['content']['op']).value
            #for votes in user['votes']:
            for votes in question['votes_list']:
                if votes['uid'] == g.user.id:
                    if direction == 'up' and votes['value'] != 1:
                        question['votes'] += 1
                        votes['value'] += 1
                        user['rep'] += 1
                        receiver['rep'] += 2
                        if votes['value'] == 1:
                            user['votes_count']['up'] += 1
                            user['votes_count']['question'] += 1
                        elif votes['value'] == 0:
                            user['votes_count']['down'] -= 1
                            user['votes_count']['question'] -= 1
                        kunjika.cb.replace(str(g.user.id), user)
                        kunjika.cb.replace(str(question['content']['op']), receiver)
                        kunjika.qb.replace(str(qid), question)
                        return jsonify({'vote_count': question['votes']})
                    elif direction == 'up' and votes['value'] == 1:
                        return jsonify({'vote_count': question['votes']})
                    elif direction == 'down' and votes['value'] != -1:
                        question['votes'] -= 1
                        votes['value'] -= 1
                        user['rep'] -= 1
                        receiver['rep'] -= 2
                        if votes['value'] == -1:
                            user['votes_count']['down'] += 1
                            user['votes_count']['question'] += 1
                        elif votes['value'] == 0:
                            user['votes_count']['up'] -= 1
                            user['votes_count']['question'] -= 1

                        kunjika.cb.replace(str(g.user.id), user)
                        kunjika.cb.replace(str(question['content']['op']), receiver)
                        kunjika.qb.replace(str(qid), question)
                        return jsonify({'vote_count': question['votes']})
                    elif direction == 'down' and votes['value'] == -1:
                        return jsonify({'vote_count': question['votes']})

            vote = {}
            vote['uid'] = g.user.id
            vote['value'] = 0
            if direction == 'up':
                #p##print(answer)
                question['votes'] += 1
                vote['value'] = 1
                user['rep'] += 1
                receiver['rep'] += 2
                user['votes_count']['up'] += 1
                user['votes_count']['question'] += 1

                question['votes_list'].append(vote)
                kunjika.cb.replace(str(g.user.id), user)
                kunjika.cb.replace(str(question['content']['op']), receiver)
                kunjika.qb.replace(str(qid), question)
                return jsonify({'vote_count': question['votes']})
            elif direction == 'down':
                question['votes'] -= 1
                vote['value'] = -1
                user['rep'] -= 1
                receiver['rep'] -= 2
                user['votes_count']['down'] += 1
                user['votes_count']['question'] += 1

                question['votes_list'].append(vote)
                kunjika.cb.replace(str(g.user.id), user)
                kunjika.cb.replace(str(question['content']['op']), receiver)
                kunjika.qb.replace(str(qid), question)
                return jsonify({'vote_count': question['votes']})