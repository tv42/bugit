=======
 Bugit
=======

Logo::

           .----.
        .--+-.  |
	|bu|g|it|
	|  `-+--'
	`----'

Track bugs in a separate disconnected history in the same git
repository that houses your code.

The bugs themselves can be elsewhere, such as Trac, the first step is
tracking what commit fixes what.

Tree layout::

     bugit/seen/<bug_id>/yes/<sha-1>
     bugit/seen/<bug_id>/no/<sha-1>

(alternate names: found/notfound, seen/notseen, hasbug/nobug)

(ponder on prefix, a good one

Zero length files.

Check out debbugs version tracking.


Bug reproducability as tags in git
==================================

- packed tags make feasible
- tags point to commit
  - have to repeat commit in tag name for uniqueness
- bugit bisect <bug_id>
- bugit/tickets/<bug_id>/summary
- bugit/tickets/<bug_id>/comment/...
- bugit/tickets/<bug_id>/depends/...

