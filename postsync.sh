#!/bin/sh
notmuch tag +spam folder:Spam
emacsclient -e '(run-hooks `notmuch-postsync-hook)'
