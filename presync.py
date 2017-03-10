import os
from subprocess import call
import time
import uuid

import notmuch

with open(os.devnull, "w") as devnull:
  call(["emacsclient", "-e", "(run-hooks 'notmuch-presync-hook)"],
       stdout=devnull)

db = notmuch.Database()
maildir_path = os.path.realpath(os.path.expanduser("~/Maildir"))

previous_queries = []

def new_name(old_name):
  # Most of my email files are named like suggested here[1]. For those we can
  # replace the timestamp part with the current time.
  # [1] - http://cr.yp.to/proto/maildir.html
  first_dot = old_name.find(".")
  if first_dot > -1:
    return str(int(time.time())) + old_name[first_dot:]

  # Otherwise we just use a UUID, preserving the flag part if present.
  first_colon = old_name.find(":")
  if first_colon > -1:
    return str(uuid.uuid1()) + old_name[first_colon:]
  return str(uuid.uuid1())

def move_messages(query_string, destination):
  # Avoid trying to move the same messages multiple times
  previously_moved = " OR ".join(previous_queries)
  previous_queries.append("(" + query_string + ")")
  if previously_moved:
    query_string += " AND NOT (" + previously_moved + ")"
  # Move them
  query = db.create_query(query_string)
  for message in query.search_messages():
    old_filename = message.get_filename()
    path, filename = os.path.split(old_filename)
    cur_new = path.split(os.sep)[-1]
    new_filename = os.path.join(maildir_path, destination,
                                cur_new, new_name(filename))
    # Note this might fail if the filename already exists. That's extremely
    # unlikely however, and the file will be renamed next time this script runs
    # anyway.
    os.rename(old_filename, new_filename)

# Move any junk to the Spam / Trash folders
move_messages("tag:spam AND NOT folder:Spam", "Spam")
move_messages("tag:deleted AND NOT folder:Trash", "Trash")

# Archive any messages in INBOX which no longer have the inbox tag
move_messages("NOT tag:inbox AND folder:INBOX", "Archive")
