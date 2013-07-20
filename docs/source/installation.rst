Installation Guide
******************
Debian/Ubuntu/Mint like deb based Linux
=======================================
This is the only type of installation I will cover as I do not run it on
any other type of machine. May be over time I will add more as I get content
from community. Basically it is a flask application and the way you deploy
a flask application on other platforms you can deploy Kunjika as well.

You need Python 2.7, a mail server like Postfix which I use, Couchbase.
For web server we will use nginx and uwsgi will act as our application
server. I have found nginx and uwsgi combination to be a mature, stable
and high performing. Also, nginx can be used to scale later as layer 7
load balancer.

Python 2.7 will definitely be installed on your GNU/Linux system. Let us get
started by installing pip, git, virtualenv, nginx, postfix and python-dev.

.. code-block:: verbatim

   sudo apt-get install python-pip git python-virtualenv nginx postfix python-dev

Now we may need to create **/var/www** directory as it may not be there. You can
choose **internet site** for Postfix configuration window and then close port
25 and 587 with iptables. Configuration of Postfix is out of scope and is very well
documented at `Postfix documentation <http://www.postfix.org/documentation.html>`_.

.. code-block:: verbatim

   sudo mkdir /var/www
   cd /var/www

Clone Kunjika from `Kunjika's git repository <https://github.com/shivshankardayal/Kunjika>`_.

.. code-block:: verbatim

   sudo git clone https://github.com/shivshankardayal/Kunjika

Now we need to install various packages which can be installed using **install-packages.sh**
script bundled with Kunjika but before that we need to install couchbase and **libcouchbase**.
Download Couchbase at `Download page <http://www.couchbase.com/download>`_. As of now 2.1.0
enterprise edition is there for community edition you can choose 2.0.1. Download one and
then install using dpkg.

.. code-block:: verbatim

   sudo dpkg -i couchbase-server*.deb

Now we need libcouchbase which we can install using instructions from `getting stared page at couchbase
<http://www.couchbase.com/communities/c/getting-started>`_.

Now we can install packages after which you change ownership of entire folder to www-data.

.. code-block:: verbatim

   sudo sh install-packages.sh
   sudo chown -R www-data:www-data .

The above command will prepare venv and install all necessary packages.

Now we need to install **uwsgi**. Even though it is there in repository it is better to get it
from project website and compile from source as I have always encountered problems with
repository copy. To get it you can go to `uwsgi's projetc page <http://projects.unbit.it/uwsgi/>`_.
Go to **Get it** section and download the tarball. As of now version 1.9.13 is there but it keeps
changing.

.. code-block:: verbatim

   wget http://projects.unbit.it/downloads/uwsgi-1.9.13.tar.gz
   tar -xzf uwsgi-1.9.13.tar-gz
   cd uwsgi-1.9.13
   make

Now you have a choice that you can make a link or copy the binary. You can do one of following:

.. code-block:: verbatim

   sudo ln -s /path-to-uwsgi-1.9.13/uwsgi /usr/local/bin
   sudo cp /path-to-uwsgi-1.9.13/uwsgi /usr/local/bin

Now we need to configure nginx and uwsgi. For nginx you may want to delete **default** in
**/etc/nginx/sites-enabled** and **/etc/nginx/sites-available** directories. Anyway, just dump
following in one file say kunjika **/etc/nginx/sites-available**.

.. code-block:: verbatim

   sudo vi /etc/nginx/sites-available/kunjika

   server {
     listen       80;
     server_name  kunjika;
 
     location /static {
         alias /var/www/Kunjika/static;
     }
 
     location / {
         include uwsgi_params;
         uwsgi_pass unix:/tmp/uwsgi.sock;
         uwsgi_param UWSGI_PYHOME /var/www/Kunjika/venv;
         uwsgi_param UWSGI_CHDIR /var/www/Kunjika;
         uwsgi_param UWSGI_MODULE kunjika;
         uwsgi_param UWSGI_CALLABLE kunjika;
     }
   }

   sudo ln -s /etc/nginx/sites-available/kunjika /etc/nginx/sites-enabled/kunjika

You may also choose to run it on port 443 for ssh for which you will need ssl certificates.
Free ssl certificates are available from `cacert <http://www.cacert.org/>`_. Just that you will
have to ask your users to import cacert's root certificate in their browser to remove that
annoying warning about unknown signing authority. How to generate cacert certificate is documented
at cacert's website. You just need to generate a csr(certificate signing request). In the
above configuration replace **server_name** from your DNS. Like I keep it as 
**kunjika.libreprogramming.org**.

For uwsgi we need to create a upstart file. Just paste the following in **/etc/init/uwsgi.conf:

.. code-block:: verbatim

   description "uWSGI"
   start on runlevel [2345]
   stop on runlevel [06]

   respawn

   exec uwsgi --master --processes 4 -b 8192 --die-on-term --uid 33 --gid 33 --socket /tmp/uwsgi.sock  --vhost --logto /var/log/uwsgi.log

Note that uid 33 and gid 33 refers to www-data. You can see this in **/etc/passwd** file with which
nginx runs. This is needed so that nginx can read/write to this socket. And of course you do not want
to run uwsgi or nginx as root. The -b option is needed because google's response is greater than
4096 which is default for uwsgi.

Let us talk about main nginx.conf. The default file looks like following:

.. code-block:: verbatim

   user www-data;
   worker_processes 4;
   pid /run/nginx.pid;

   events {
   	worker_connections 768;
	# multi_accept on;
   }

   http {

	##
	# Basic Settings
	##

	sendfile on;
	tcp_nopush on;
	tcp_nodelay on;
	keepalive_timeout 65;
	types_hash_max_size 2048;
	# server_tokens off;

	# server_names_hash_bucket_size 64;
	# server_name_in_redirect off;

	include /etc/nginx/mime.types;
	default_type application/octet-stream;

	##
	# Logging Settings
	##

	access_log /var/log/nginx/access.log;
	error_log /var/log/nginx/error.log;

	##
	# Gzip Settings
	##

	gzip on;
	gzip_disable "msie6";

	# gzip_vary on;
	# gzip_proxied any;
	# gzip_comp_level 6;
	# gzip_buffers 16 8k;
	# gzip_http_version 1.1;
	# gzip_types text/plain text/css application/json application/x-javascript text/xml application/xml application/xml+rss text/javascript;

	##
	# nginx-naxsi config
	##
	# Uncomment it if you installed nginx-naxsi
	##

	#include /etc/nginx/naxsi_core.rules;

	##
	# nginx-passenger config
	##
	# Uncomment it if you installed nginx-passenger
	##
	
	#passenger_root /usr;
	#passenger_ruby /usr/bin/ruby;

	##
	# Virtual Host Configs
	##

	include /etc/nginx/conf.d/*.conf;
	include /etc/nginx/sites-enabled/*;
   }

Commented portion below this is ommitted for brevity. Note that nginx and uwsgi both will
spawn four workers in default configuration. If you are low in RAM you can make that 2
even 1. You can make it more in case you have large user base and you need to serve more
connections. I will give load balacing configurations later.

You should keep checking **/var/log/uwsgi.log** from time to time that your response time is
not worsening in case of load. Then you need more workers and more hardware probably. You
can even make **gzip_comp_level** to 9 because pages are so small that gzip will have no
problem and users with slow connections will benefit greatly.

Now you should restart nginx, uwsgi and postfix(not needed for this really) once. And voila you
should have everything running.

In case of any issues with this doc let me know at `my email address <shivshankar.dayal@gmail.com>`_.

Hey where are you going you need to read next part. Configuring Kunjika itself.
