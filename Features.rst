Features
********
TODO
====
1.  Automatic upgrade check and 1-click site upgrade.
2.  Automatic site and DB backup, with backup scheduling to remote or cloud server.
3.  Ability to take site offline (maintenance mode).
4.  Forum statistics (page views, active members, new members, etc) from the Admin page.
5.  HTML fields to embed code, like Piwik Web Analytics, AdSense or any other display ad
    integration into specific part of a the site or in template files.
6.  Built-in firewall and IDS/IPS system.
7.  Prevent remote access to core files except from a specified IP/user.
8.  Banning IP/IP range.
9.  Akismet or Defensio anti-spam integration.
10. Built-in website scanner to scan template files for malware and unauthorized modifications,
    with email notification to admin to report suspected modifications
11. Backup core files to a locked down directory, with the ability to restore modified files
    to the originals from this directory
12. Login Security & Monitoring (notify admin when a user with admin privileges logs in, etc).
13. Lock and Unlock core files from admin page.
14. jQuery lightbox integration.
15. Visual notification of new questions/comments/answers when a user is browsing any part of
    the forum. e.g "A new question/comment/answer has been posted, click here to read it." Or
    "4 new questions/comments/answers have just been posted. Click here to read them."
16. Create private discussion group.
17. Continuous rendering of questions like discourse.org which can be configured from configuration.
28. Option for members to complete their social network profiles on their profile page, and give
    them the option to choose which one(s) to auto-post to. 
19. Chat, just like Stack Overflow, that only users with a certain reputation may participate
    in, or any registered member can join.
20. Sending private messages between registered members, and email notification when a private
    message is received.
21. Automatic private message to users upon successful email activation.
22. Blog module, with a liveblogging feature similar to ScribbleLive.
23. WordPress module, to embed Kunjika forum in a WP site.
24. Gallery module to enable creation of a gallery page (a blog for galleries).

DONE
====
1.  Question posting.
2.  Answer posting.
3.  Comment posting on either.
4.  Syntax highlighting and image upload in questions, answers or comments.
5.  Voting on answers and questions.
6.  Editing questions, answers and comments.
7.  Accepting answers.
8.  Profile page.
9.  Unanswered url.
10. Showing views using very simple algorithm which people may not like.
11. Reputation system.

    a. 1 point for asking question
    b. 1 point for doing voting up -1 for down.
    c. 2 points for getting vote up -2 for down.
    d. 1 point for editing.
    e. 10 points for accepted answer
    f. 2 points for accepting answer.
    g. 4 points for answering.

12. Making questions favorite for one user.
13. Search on question title/contents using Google's custom search. Note that
    crawler crawls depending upon activity so new stuff wont reflect immediately.
14. Simple tags display.(Allow editing of excerpt)
15. Users page.(edit link does not work.)
16. Simple count of questions, answers, tags and users.
17. Popular tags display on main page in side bar.
18. Code attachments also .zip source attachments up to 2MB.
19. Atom feed for questions.
20. OpenID integration.(take care of GET of create_profile)
21. Email notification at registration.
22. Flagging inappropriate questions, answers and comments.
23. Banning/unbanning users.
24. Tag wiki implementation.
25. Reset password.
26. Complete Markdown help with MathJax coverage and some detailed documentation on how to use MathJax.
27. Stop brute force password attack.
28. Configurable no. of questions, answers, comments from one user per min, hour and day etc.
    This feature is needed to abuse from automated spam. It is done in a very bad now but can be
    improved easily later. For now it should work for normal operating conditions on a normal QA
    forum. (This is held back even though code was written. It needs more testing in an automated fashion.)
29. Flash messages for user feedback.
30. Error pages are there.
31. File based rotated logging.
32. Automatic private message to users upon registration.
19. "Similar question" feature just like Stack Overflow.
20. Search using Elasticsearch.
21. Similar questions.
22. Following questions, tags and users. As of now if user is involved in a question you will get an email
    if something happens in that question. For tags and users implementation will come as more content and
    users come.
23. Memcached implementation is not needed as couchbase is very fast for key based access and almost entire
    code related to database has been changed for this.
14. Admin can create an announcement post that is then broadcast by email to all registered
    users. Give users the option to opt out of such messages from their profile page.
23. Admin can send bulk email or private messages to members.
24. Users can receive an email when someone quotes them, replies to their posts, or mentions
    their @username. (@username is not done because sometimes last name is missing and anyway user involved in
    a question will get an email.)
17. Related questions tag that embeds related questions at the end of a discussion.
21. Users can send invitation emails from their profile page.

Postponed for later
===================
1. Extra cloning of stackoverflow.
2. Feed for users.
3. Sitemap generation
4. Stop DOS.(This should not reach application and must be filtered at web server level or before).
