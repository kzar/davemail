#!/bin/sh
notmuch tag -spam not folder:Spam
notmuch tag +spam folder:Spam
notmuch tag +deleted folder:Trash
notmuch tag -deleted not folder:Trash
notmuch tag -inbox folder:Archive OR folder:Sent
emacsclient -e '(run-hooks `notmuch-postsync-hook)' > /dev/null
