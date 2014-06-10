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
from flask import Flask, render_template

def handle_edit(element):
    ###print element
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
