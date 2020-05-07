import os
from subprocess import call, check_output
from configobj import ConfigObj
import re
import email

import notmuch

config = ConfigObj(".davemailrc")
for maildir in config:
  # Prevent the new tag from being mapped to a folder.
  if "new" in config[maildir]["tag_folder_mapping"]:
    del config[maildir]["tag_folder_mapping"]["new"]

def move_messages(query_string, maildir, destination_folder):
  with notmuch.Database(mode=notmuch.Database.MODE.READ_WRITE) as db:
    query = db.create_query(query_string)

    for message in query.search_messages():
      old_filename = message.get_filename()
      path, filename = os.path.split(old_filename)
      cur_new = path.split(os.sep)[-1]
      # We strip the ,U=nnn infix from the filename so that mbsync isn't
      # confused when using the native storage scheme.
      # https://sourceforge.net/p/isync/mailman/message/33359742/
      new_filename = os.path.join(db.get_path(), maildir, destination_folder,
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
  for maildir in config:
    if config[maildir].as_bool("maintain_tag_folder_mapping"):
      default_folder = config[maildir]["default_folder"]
      for tag, folder in config[maildir]["tag_folder_mapping"].iteritems():
        # First we move tagged messages into the folder.
        move_messages("tag:%s AND NOT folder:\"%s/%s\" AND path:%s/**" %
                      (tag, maildir, folder, maildir),
                      maildir, folder)
        # Then untagged messages out.
        move_messages("NOT tag:%s AND folder:\"%s/%s\"" %
                      (tag, maildir, folder),
                      maildir, default_folder)

def tag_messages(query_string, tag):
  # We tag/untag the messages by calling the notmuch command here since
  # the Python notmuch API doesn't provide a way to tag messages without
  # iterating through them.
  call(["notmuch", "tag", tag, query_string])

def tag_moved_and_new_messages():
  for maildir in config:
    # Tag messages based on their maildir
    tag_messages("path:%s/**" % (maildir), "+" + maildir)

    for tag, folder in config[maildir]["tag_folder_mapping"].iteritems():
      if config[maildir].as_bool("maintain_tag_folder_mapping"):
        # Tag / untag all messages if maintaining tag to folder mapping
        tag_messages("NOT folder:\"%s/%s\" AND path:%s/**" %
                     (maildir, folder, maildir), "-" + tag)
        tag_messages("folder:\"%s/%s\"" %
                     (maildir, folder), "+" + tag)
      elif config[maildir].as_bool("tag_new_messages"):
        # Otherwise only tag new messages which were already filed e.g. spam
        tag_messages("folder:\"%s/%s\" AND tag:new" %
                     (maildir, folder), "+" + tag)

def tag_muted_threads():
  # New messages in muted threads won't have the muted tag yet, so to avoid
  # those showing up in searches we take care to tag them now.
  # See https://notmuchmail.org/excluding/
  muted_threads = check_output(
    ["notmuch", "search", "--output=threads", "tag:muted"]
  ).decode("utf-8").replace(os.linesep, " ").strip()
  tag_messages(muted_threads, "+muted")

def header_matches(filename, header_name, regexp):
  with open(filename, "r") as f:
    message = email.message_from_file(f)

    for header_value in message.get_all(header_name, []):
      if regexp.match(header_value):
        return True
    return False

# Occasionally it's useful to tag messages based on a header value which notmuch
# doesn't index. For the messages matching the query, assign the tag if the
# message header exists and matches the given regexp. *Warning slow!*
def tag_other_header_match(query_string, header_name, regexp, tags):
  regexp = re.compile(regexp)
  with notmuch.Database(mode=notmuch.Database.MODE.READ_WRITE) as db:
    query = db.create_query(query_string)
    for message in query.search_messages():
      if header_matches(message.get_filename(), header_name, regexp):
        for tag in tags.split():
          if tag[0] == "+":
            message.add_tag(tag[1:])
          elif tag[0] == "-":
            message.remove_tag(tag[1:])

def update_database():
  call(["notmuch", "new"])

def run_emacs_hook(hook_name):
  with open(os.devnull, "w") as devnull:
    call(["emacsclient", "-e", "(run-hooks '" + hook_name + ")"],
         stdout=devnull, stderr=devnull)
