Introduction
************
Kunjika is just another Q&A framework in the line of http://stackoverflow.com or
http://www.question2answer.org/ or http://www.lampcms.com/ or https://askbot.com
or http://www.osqa.net or http://shapado.com etc to name most popular ones. You
should not count OSQA to be a QA anymore because DZone stopped all development
longtime back a dirty commercial route while they got their testing done by
community. A classic case of betrayal by a company to open-source community.
However, if you still want to avail their facilities you can shell out your money
at http://answerhub.com :-). To each their own.

Kunjika is a word from Sanskrit which means collection of answers. You may ask
why I wrote Kunjika while many are out there. Well, I needed a QA and the existing
ones were not quite satisfying the requirements. For example, I used LampCMS for
some time but it was kind of buggy and sometimes I never got answers even after
long wait on its support forum. Question2Answer and Askbot are not bad actually
they are very good. However, they are deeply tied to SQL which I do not like.
Also, Question2Answer in particular support MySQL only for which Oracle finally
changed licensing term last I was informed so that is out of question. I write
my books and give it for free for study at http://libreprogramming.org and
Kunjika is meant to satisfy the needs for interaction between me and my
readers(I prefer to call them my students).

Kunjika uses Python, Flask, Couchbase for server side and css and jqeury for client
side duties. Templating is done is Jinja2 as supported by Flask. Time to justify
my choices. Well, there were not many. Of all scripting languages I am most
proficient with Python so I chose it. Flask I chose because I could learn it
faster then any other framework and it is not really a micro framework considering
high quality extensions offered by great community of Flask. Since, I was writing
an application and Flask does not tie you with a database like the ORM of Django
does I chose Couchbase because of its features. Well, you may argue that an RDBMS
will make application more acceptable in community but choosing an RDBMS makes
development process slow even with matured ORMs like SQLAlchemy. Also, Couchbase
is much more superior to any RDBMS in most of the areas for such a new database.