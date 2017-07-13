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
tag_folder_mapping = dict(config.items("tag_folder_mapping"))

old_folder = config.get("old_message_archival", "old_folder")
date_filter = "date:" + config.get("old_message_archival", "date_since") + ".."

# Prevent the new tag from being mapped to a folder since it's a special case.
if "new" in tag_folder_mapping:
  del tag_folder_mapping["new"]

# Also prevent mapping to the folder where old messages are archived.
for tag in tag_folder_mapping.keys():
  if tag_folder_mapping[tag] == old_folder:
    del tag_folder_mapping[tag]

def move_messages(query_string, destination_folder):
  with notmuch.Database(mode=notmuch.Database.MODE.READ_WRITE) as db:
    query = db.create_query(query_string)

    for message in query.search_messages():
      old_filename = message.get_filename()
      path, filename = os.path.split(old_filename)
      cur_new = path.split(os.sep)[-1]
      # We strip the ,U=nnn infix from the filename so that mbsync isn't
      # confused when using the native storage scheme.
      # https://sourceforge.net/p/isync/mailman/message/33359742/
      new_filename = os.path.join(db.get_path(), destination_folder,
                                  cur_new, re.sub(",U=[0-9]+", "", filename))
      # If the old file no longer exists, or the new one already does then we
      # simply skip this message for now.
      try:
        os.renames(old_filename, new_filename)
      except OSError:
        continue
      # We add the new filename to the notmuch database before removing the old
      # one so that the notmuch tags are preserved for the message.
      db.add_message(new_filename)
      db.remove_message(old_filename)

def move_tagged_messages():
  for tag, folder in tag_folder_mapping.items():
    # First we move tagged messages into the folder.
    move_messages("tag:%s AND NOT folder:%s AND %s" %
                  (tag, folder, date_filter), folder)
    # Then untagged messages out.
    move_messages("NOT tag:%s AND folder:%s AND %s" %
                  (tag, folder, date_filter), default_folder)

def tag_messages(query_string, tag):
  call(["notmuch", "tag", tag, query_string])

def tag_moved_messages():
  for tag, folder in tag_folder_mapping.items():
    # We tag/untag the messages by calling the notmuch command here since the
    # Python notmuch API doesn't provide a way to tag messages without
    # iterating through them.
    tag_messages("NOT folder:%s AND %s" % (folder, date_filter), "-" + tag)
    tag_messages("folder:%s AND %s" % (folder, date_filter), "+" + tag)

def archive_old_messages():
  1
  # FIXME
  #   - First make sure the message isn't in old_folder or any
  #     folder within that.
  #   - Do we want to move INBOX -> Old.INBOX, or just INBOX -> Old?
  #   - I guess we don't want to archive old messages in other folders,
  #     for example in travel?
  # move_messages("NOT " + date_filter, old_folder)

def update_database():
  call(["notmuch", "new"])

def run_emacs_hook(hook_name):
  with open(os.devnull, "w") as devnull:
    call(["emacsclient", "-e", "(run-hooks '" + hook_name + ")"],
         stdout=devnull, stderr=devnull)
