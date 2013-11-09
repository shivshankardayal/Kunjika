Kunjika
=======

"It is software made up of bugs."

Stackoverflow clone. I am using Flask framework so obviously Python as well.
Couchbase for database and Memcahced funcitonality.

We have some functionality working now. Still not even alpha. This project
has been started to scratch my own itch. OSQA's development has been stopped.
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

Release 0.2 alpha is done. Please test while I am fixing bugs and working on new
features.

I am working on documentation which you can read at http://libreprogramming.org/docs/kunjika/
The documentation covers installation and configuration as of now. Code
documentation is yet to be put there. The documentation is not update though.

github is again home of Kunjika. 

At present I am working on Couchbase optimization for Kunjika and I have
decided that it will remain purely a QA platform with little or no social
features.

I believe that keeping it minimalistic is best and very few new features will
be introduced. The atom feed is the best way to watch the QA activity. In few
days I will freeze the new features and do a final alpha release.
