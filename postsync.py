import davemail

if __name__ == "__main__":
  # Take care to move messages which were tagged after synchronisation started.
  davemail.move_tagged_messages()
  # Now we can update the database and make sure the tags are up to date.
  davemail.update_database()
  davemail.tag_moved_messages()
  davemail.run_emacs_hook("notmuch-postsync-hook")
