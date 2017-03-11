import os
from subprocess import call
import time
import uuid
from ConfigParser import SafeConfigParser

import notmuch

config = SafeConfigParser()
config.read(".davemailrc")

default_folder = config.get("general", "default_folder")
tag_folder_mapping = config.items("tag_folder_mapping")

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

def move_messages(query_string, destination_folder):
  db = notmuch.Database(mode=notmuch.Database.MODE.READ_WRITE)
  query = db.create_query(query_string)

  for message in query.search_messages():
    old_filename = message.get_filename()
    path, filename = os.path.split(old_filename)
    cur_new = path.split(os.sep)[-1]
    new_filename = os.path.join(db.get_path(), destination_folder,
                                cur_new, new_name(filename))
    # Note this might fail if the filename already exists. That's unlikely
    # however, and the file will be renamed next time this script runs anyway.
    os.rename(old_filename, new_filename)
    # We add the new filename to the notmuch database before removing the old
    # one so that the notmuch tags are preserved for the message.
    db.add_message(new_filename)
    db.remove_message(old_filename)

def move_tagged_messages():
  for tag, folder in tag_folder_mapping:
    # First we move tagged messages into the folder.
    move_messages("tag:%s AND NOT folder:%s" % (tag, folder), folder)
    # Then untagged messages out.
    move_messages("NOT tag:%s AND folder:%s" % (tag, folder), default_folder)

def tag_moved_messages():
  for tag, folder in tag_folder_mapping:
    # We tag/untag the messages by calling the notmuch command here since the
    # Python notmuch API doesn't provide a way to tag messages without
    # iterating through them.
    call(["notmuch", "tag", "-" + tag, "NOT folder:" + folder])
    call(["notmuch", "tag", "+" + tag, "folder:" + folder])

def run_emacs_hook(hook_name):
  with open(os.devnull, "w") as devnull:
    call(["emacsclient", "-e", "(run-hooks '" + hook_name + ")"],
         stdout=devnull, stderr=devnull)
