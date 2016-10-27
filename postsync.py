from subprocess import call

# FIXME Add some tagging here?

call(["emacsclient", "-e", "(run-hooks 'notmuch-postsync-hook)"])
