Features
********
TODO
====
1. Create private discussion group.
2. Chat, just like Stack Overflow, that only users with a certain reputation may participate
    in, or any registered member can join.
3. Sending private messages between registered members, and email notification when a private
    message is received.
4. Automatic private message to users upon successful email activation.
5. Moderator on 500 points.
6. Hide inappropriate question, answer or comment.
7. Restore previous versions of question.
8. Test series implementation.

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
14. Simple tags display.
15. Users page.
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
33. "Similar question" feature just like Stack Overflow.
34. Search using Elasticsearch.
35. Similar questions.
36. Following questions, tags and users. As of now if user is involved in a question you will get an email
    if something happens in that question. For tags and users implementation will come as more content and
    users come.
37. Memcached implementation is not needed as couchbase is very fast for key based access and almost entire
    code related to database has been changed for this.
38. Admin can create an announcement post that is then broadcast by email to all registered
    users. Give users the option to opt out of such messages from their profile page.
39. Admin can send bulk email or private messages to members.
40. Users can receive an email when someone quotes them, replies to their posts, or mentions
    their @username. (@username is not done because sometimes last name is missing and anyway user involved in
    a question will get an email.)
41. Related questions tag that embeds related questions at the end of a discussion.
42. Users can send invitation emails from their profile page.
43. Preview of questions on mouse hover on links on home page of questions.
44. Test series creation for objective questions. (Generating tests to be done.)
45. Tag suggestion(autocomplete).
46. Bookmarking questions and view on profile.
47. Skills and endorsements on profile page.
48. Images are now stored as base64 strings in database for distributed storage.
49. Articles are now implemented.
50. Tags in meta for questions and articles page.
51. Ability to take site offline (maintenance mode).
52. Questions are versioned now. Every edit creates a new version.(restore to be done.)
53. Sitemap generation
54. Drafts feature for article authors.
55. Visual notification of new questions/comments/answers when a user is browsing any part of
    the forum. e.g "A new question/comment/answer has been posted, click here to read it." Or
    "4 new questions/comments/answers have just been posted. Click here to read them."
56. Question, answers and comments should be editable only by poster.
