from flask import flash, render_template, Blueprint, url_for, redirect, request, jsonify, g, abort
from forms import *
from uuid import uuid1
from time import time
import kunjika
import urllib2
import json
import utility

test_series = Blueprint('test_series', __name__, template_folder='templates')

@test_series.route('/tests')
def tests():
    try:
        user = g.user.user_doc
    except:
        flash('You need to be logged in to take tests.', 'error')
        return redirect(url_for('questions'))
    return render_template('tests.html', title='Tests', user=user, name=g.user.name, role=g.user.role, user_id=g.user.id)

@test_series.route('/getcat')
def getcat():
    if g.user.id == 1:
        tech=request.args.get('lang')
        if tech == 'C':
            return jsonify({
                'basics': 'Basics',
                'control_flow': 'Control Flow',
                'oae': 'Operators and Expressions',
                'funcs': 'Functions',
                'arrays': 'Arrays',
                'pointers': 'Pointers',
                'strings': 'Strings',
                'sue': 'Structures, Unions and Eums',
                'io': 'IO',
                'cli': 'Command Line Arguments',
                'bitop': 'Bitwise Operators',
                'typedef': 'Typedef',
                'const': 'Const',
                'memalloc': 'Memory Allocation',
                'vararg': 'Variable Arguments',
                'lib': 'Library Functions',
                'threading': 'Multithreading',
                'macros': 'Macros'
            })
        elif tech == 'C++':
            return jsonify({
                'basics': 'Basics',
                'control_flow': 'Control Flow',
                'oae': 'Operators and Expressions',
                'funcs': 'Functions',
                'arrays': 'Arrays',
                'pointers': 'Pointers',
                'strings': 'Strings',
                'sue': 'Structures, Unions and Eums',
                'io': 'IO',
                'cli': 'Command Line Arguments',
                'bitop': 'Bitwise Operators',
                'typedef': 'Typedef',
                'const': 'Const',
                'memalloc': 'Memory Allocation',
                'vararg': 'Variable Arguments',
                'lib': 'Library Functions',
                'threading': 'Multithreading',
                'classes': 'Classes',
                'inheritance': 'Inheritance',
                'polymorphism': 'Polymorphism',
                'exceptions': 'Exceptions',
                'rtti': 'RTTI',
                'templates': 'Templates',
                'stl': 'STL',
                'references': 'References'
            })
        elif tech == 'Java':
            return jsonify({
                'basics': 'Basics',
                'control_flow': 'Control Flow',
                'oae': 'Operators and Expressions',
                'funcs': 'Functions',
                'arrays': 'Arrays',
                'strings': 'Strings',
                'io': 'IO',
                'cli': 'Command Line Arguments',
                'bitop': 'Bitwise Operators',
                'memalloc': 'Memory Allocation',
                'lib': 'Library Functions',
                'threading': 'Multithreading',
                'classes': 'Classes',
                'inheritance': 'Inheritance',
                'polymorphism': 'Polymorphism',
                'exceptions': 'Exceptions',
                'generics': 'Generics',
                'packages': 'Packages',
                'interfaces': 'Interfaces',
                'networking': 'Network Programming'
            })
        elif tech == 'Python':
            return jsonify({
                'basics': 'Basics',
                'control_flow': 'Control Flow',
                'oae': 'Operators and Expressions',
                'funcs': 'Functions',
                'ds': 'Data Structures',
                'modules': 'Modules',
                'io': 'IO',
                'exceptions': 'Exceptions',
                'classes': 'Classes',
                'at': 'Advanced Topics',
                'lib': 'Python Library'
            })
        elif tech == 'Perl':
            return jsonify({
                'basics': 'Basics',
                'control_flow': 'Control Flow',
                'oae': 'Operators and Expressions',
                'funcs': 'Built-In Functions',
                'ds': 'Data Structures',
                'modules': 'Modules',
                'io': 'IO',
                'classes': 'Classes',
                'at': 'Advanced Topics',
                'lib': 'Perl Library',
                'regex': 'Regular Expressions'
            })
    else:
        return jsonify({"success": False})

@test_series.route('/add_objective_question', methods=['GET', 'POST'])
def add_objective_question():
    oqForm = OQForm(request.form)

    class ChoiceForm(Form):
        tech = SelectField('Technology', choices=[('c', 'C'), ('cpp', 'C++'), ('java', 'Java'), ('perl', 'Perl'), \
        ('python', 'Python')])
        cat = SelectField('Category', choices=[('arrays', 'Arrays'), ('basics', 'Basics'), ('bitop', 'Bitwise Operators'),
            ('cli', 'Command Line Arguments'), ('const', 'Const'), ('control_flow', 'Control Flow'),
            ('funcs', 'Functions'), ('io', 'IO'), ('lib', 'Library Functions'), ('macros', 'Macros'), ('memalloc', 'Memory Allocation'),
            ('oae', 'Operators and Expressions'), ('pointers', 'Pointers'), ('strings', 'Strings'),
            ('sue', 'Structures, Unions and Eums'), ('threading', 'Multithreading'), ('typedef', 'Typedef'),
            ('vararg', 'Variable Arguments')])
        option = RadioField('What type of question do you want?', choices=[('Single choice', 'Single Choice'),
                                                                           ('Multiple choice', 'Multiple choice')])
        description = TextAreaField('', [validators.Length(min=20, max=5000), validators.DataRequired()])
        option_1 = StringField('Question', [validators.Length(min=1, max=200), validators.DataRequired()])
        option_2 = StringField('Question', [validators.Length(min=1, max=200), validators.DataRequired()])
        option_3 = StringField('Question', [validators.Length(min=1, max=200), validators.Optional()])
        option_4 = StringField('Question', [validators.Length(min=1, max=200), validators.Optional()])
        option_5 = StringField('Question', [validators.Length(min=1, max=200), validators.Optional()])
        option_6 = StringField('Question', [validators.Length(min=1, max=200), validators.Optional()])
        answers = StringField('Answers', [validators.Length(min=1, max=200), validators.DataRequired()])

    questionForm = ChoiceForm(request.form)

    choices = []

    if g.user.id == 1:
        if oqForm.validate_on_submit() and request.method == 'POST':
            for i in range(0, int(oqForm.oq_answers.data)):
                choices.append(str(i+1))

            return render_template('create_oq.html', title='Create Objective Question', form=questionForm, options=choices, ppage=True, name=g.user.name, role=g.user.role,
                       user_id=g.user.id)

        if questionForm.validate_on_submit() and request.method == 'POST':
            tech = questionForm.tech.data
            cat = questionForm.cat.data
            option =  questionForm.option.data
            option_1 =  questionForm.option_1.data
            option_2 =  questionForm.option_2.data

            question = {}
            question['tech'] = tech
            question['cat'] = cat
            question['content'] = {}
            question['content']['description'] = questionForm.description.data
            question['answers'] = questionForm.answers.data

            if option == 'Single choice':
                question['content']['sc'] = True
            else:
                question['content']['mc'] = True

            question['content']['options'] = []
            question['content']['options'].append(option_1)
            question['content']['options'].append(option_2)

            if questionForm.option_3.data != "":
                question['content']['options'].append(questionForm.option_3.data)
                if questionForm.option_4.data != "":
                    question['content']['options'].append(questionForm.option_4.data)
                    if questionForm.option_5.data != "":
                        question['content']['options'].append(questionForm.option_5.data)
                        if questionForm.option_6.data != "":
                            question['content']['options'].append(questionForm.option_6.data)

            question['content']['ts'] = int(time())
            question['updated'] = question['content']['ts']
            question['content']['ip'] = request.remote_addr
            question['qid'] = 'tq-' + str(uuid1())  # tq stands for test question. prefix is used for increasing period
                                                   # before uuid will repeat
            question['_type'] = 'tq'

            #print str(question['qid'])
            kunjika.kb.add(question['qid'], question)

            return redirect(url_for('administration'))

        return render_template('oq.html', title='Create Objective Question', form=oqForm, ppage=True, name=g.user.name, role=g.user.role,
                               user_id=g.user.id)
    else:
        return redirect(url_for('login'))

@test_series.route('/browse_objective_questions', defaults={'page': 1}, methods=['GET', 'POST'])
@test_series.route('/browse_objective_questions/page/<int:page>')
def browse_objective_questions(page=None):
    boqForm = BOQForm(request.form)

    if g.user.id == 1:
        if boqForm.validate_on_submit() and request.method == 'POST':
            skip = (page - 1) * kunjika.QUESTIONS_PER_PAGE
            tech = boqForm.tech.data
            cat = boqForm.cat.data
            questions = urllib2.urlopen(kunjika.DB_URL + 'kunjika/_design/dev_qa/_view/get_by_ts?limit=' +
                                        str(kunjika.QUESTIONS_PER_PAGE) + '&skip=' + str(skip) + '&key="' +
                                        urllib2.quote(str(tech)) + '"&reduce=false').read()
            count = urllib2.urlopen(kunjika.DB_URL + 'kunjika/_design/dev_qa/_view/get_by_ts?key="' +
                                    urllib2.quote(str(tech)) + '"&reduce=true').read()
            count = json.loads(count)['rows']
            if len(count) != 0:
                count = count[0]['value']
            else:
                count = 0
            questions = json.loads(questions)
            qids = []
            if len(questions) > 0:
                for row in questions['rows']:
                    qids.append(str(row['id']))
            if len(qids) > 0:
                val_res = kunjika.kb.get_multi(qids)
            questions_list = []
            for qid in qids:
                questions_list.append(val_res[str(qid)].value)

            questions_list = [question for question in questions_list if question['cat'] == cat]

            #count = len(questions_list)
            if not questions_list and page != 1:
                abort(404)
            pagination = utility.Pagination(page, kunjika.QUESTIONS_PER_PAGE, int(count))

            return render_template('browse.html', title='Questions', qpage=True, questions=questions_list,
                                   pagination=pagination, name=g.user.name, role=g.user.role,
                                   user_id=g.user.id, tech=tech, cat=cat)

        return render_template('browse_form.html', title='Browse Question Form', form=boqForm, ppage=True, name=g.user.name, role=g.user.role,
                       user_id=g.user.id)
    return redirect(url_for('login'))

@test_series.route('/edit_test/<element>', methods=['GET', 'POST'])
def edit_test(element):
    question = kunjika.kb.get(element).value
    options = len(question['content']['options'])
    class ChoiceForm(Form):
        option = RadioField('What type of question do you want?', choices=[('Single choice', 'Single Choice'),
                                                                           ('Multiple choice', 'Multiple choice')])
        description = TextAreaField('', [validators.Length(min=20, max=5000), validators.DataRequired()])
        option_1 = StringField('Question', [validators.Length(min=1, max=200), validators.DataRequired()])
        option_2 = StringField('Question', [validators.Length(min=1, max=200), validators.DataRequired()])
        option_3 = StringField('Question', [validators.Length(min=1, max=200), validators.Optional()])
        option_4 = StringField('Question', [validators.Length(min=1, max=200), validators.Optional()])
        option_5 = StringField('Question', [validators.Length(min=1, max=200), validators.Optional()])
        option_6 = StringField('Question', [validators.Length(min=1, max=200), validators.Optional()])
        answers = StringField('Answers', [validators.Length(min=1, max=200), validators.DataRequired()])

    form = ChoiceForm(request.form)
    choices = []
    for i in range(0, options):
        choices.append(str(i+1))

    if g.user.id == 1:
        if form.validate_on_submit() and request.method == 'POST':
            #print "editing test question"
            option =  form.option.data
            option_1 =  form.option_1.data
            option_2 =  form.option_2.data

            question['content'] = {}
            question['content']['description'] = form.description.data
            question['answers'] = form.answers.data

            if option == 'Single choice':
                question['content']['sc'] = True
                question['content']['mc'] = False
            else:
                question['content']['mc'] = True
                question['content']['sc'] = False

            question['content']['options'] = []
            question['content']['options'].append(option_1)
            question['content']['options'].append(option_2)

            if form.option_3.data != "":
                question['content']['options'].append(form.option_3.data)
                if form.option_4.data != "":
                    question['content']['options'].append(form.option_4.data)
                    if form.option_5.data != "":
                        question['content']['options'].append(form.option_5.data)
                        if form.option_6.data != "":
                            question['content']['options'].append(form.option_6.data)

            question['content']['ts'] = int(time())
            question['updated'] = question['content']['ts']
            question['content']['ip'] = request.remote_addr

            kunjika.kb.replace(question['qid'], question) # tq stands for test question. prefix is used for increasing period
                                                  # before uuid will repeat

            return redirect(url_for('test_series.browse_objective_questions'))

        return render_template('edit_test.html', title='Edit Objective Question', form=form, ppage=True, name=g.user.name, role=g.user.role,
                               user_id=g.user.id, question=question, options=zip(choices, question['content']['options']))
    else:
        return render_template('login')