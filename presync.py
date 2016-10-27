import os
from subprocess import call

import notmuch

call(["emacsclient", "-e", "(run-hooks 'notmuch-presync-hook)"])

db = notmuch.Database()
maildir_path = os.path.realpath(os.path.expanduser("~/Maildir"))

# Archive any messages under INBOX*/ which no longer have the inbox tag
inbox_folders = " OR ".join(["folder:" + path
                             for path in os.listdir(maildir_path)
                             if path.startswith("INBOX")])
query = db.create_query("NOT tag:inbox AND (" + inbox_folders + ")")
for message in query.search_messages():
  old_filename = message.get_filename()
  path, filename = os.path.split(old_filename)
  cur_new = path.split(os.sep)[-1]
  new_filename = os.path.join(maildir_path, "Archive", cur_new, filename)
  os.rename(old_filename, new_filename)
