Features
********
TODO
====

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
    forum.
29. Flash messages for user feedback.
30. Error pages are there.
31. File based rotated logging.

Postponed for later
===================
1. Search using Sphinx.
2. Similar questions.
3. Extra cloning of stackoverflow.
4. Feed for users.
5. Sitemap generation
6. Following questions, tags and users.
7. Stop DOS.(This should not reach application and must be filtered at web server level or before).
8. Memcached implementation is deferred as I do not see an immediate need for this because
   of Couchbase architecture should provide quite quick response itself. Also, memcached server
   replication etc is pain.
