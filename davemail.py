import os
from subprocess import call
import time
import uuid
from ConfigParser import SafeConfigParser
import re

import notmuch

config = SafeConfigParser()
config.read(".davemailrc")

default_folder = config.get("general", "default_folder")
tag_folder_mapping = config.items("tag_folder_mapping")

def move_messages(query_string, destination_folder):
  db = notmuch.Database(mode=notmuch.Database.MODE.READ_WRITE)
  query = db.create_query(query_string)

  for message in query.search_messages():
    old_filename = message.get_filename()
    path, filename = os.path.split(old_filename)
    cur_new = path.split(os.sep)[-1]
    # We strip the ,U=nnn infix from the filename so that mbsync isn't confused
    # when using the native storage scheme.
    # https://sourceforge.net/p/isync/mailman/message/33359742/
    new_filename = os.path.join(db.get_path(), destination_folder,
                                cur_new, re.sub(",U=[0-9]+", "", filename))
    # If the old file no longer exists, or the new one already does then we
    # simply skip this message for now.
    try:
      os.rename(old_filename, new_filename)
    except OSError:
      continue
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
