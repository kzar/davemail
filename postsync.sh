#!/bin/sh
notmuch tag +spam folder:Spam
notmuch tag -inbox folder:Archive OR folder:Sent
emacsclient -e '(run-hooks `notmuch-postsync-hook)'
