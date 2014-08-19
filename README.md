Kunjika
=======

"It is software made up of bugs."

It started as Stackoverflow clone but now I have implemented some features which
are not there in Stackoverflow so calling Kunjika a clone is not appropriate.
It has skills and endorsement features like linked in. I am also going to implement
articles feature which can act as a knowledge base portion for a QA site.
I am using Flask framework so obviously Python as well.
Couchbase for database and Memcahced funcitonality.

This project has been started to scratch my own itch. OSQA's development has been stopped.
I used LampCMS for sometime but found it buggy. Question2Answer is good and
decent but is in PHP which I do not know so I decided to roll my own.
Askbot could substitute OSQA but all these are turning commercial which is bad
and ugly. Cannot trust how long they will develop open source version. DZone
actually used open source community to test their product and then take away
all of it.

I never learned SQL and the schema thing is a pain for me. So I chose Couchbase
which provided nice replication, auto-sharding and memcached functionality apart
from document based database. So one query for question, one for user and one
for tag and it is done.

I am working on documentation which you can read at http://libreprogramming.org/docs/kunjika/
The documentation covers installation and configuration as of now. Code
documentation is yet to be put there.
The documentation is out of date and I will update that soon.

I am working on a series of tests for different topics related to programming language
which should be accessible in near future.

Kunjika is quite stable now and a beta release has been done.