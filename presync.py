import davemail

if __name__ == "__main__":
  davemail.run_emacs_hook("notmuch-presync-hook")
  davemail.move_tagged_messages()
  davemail.archive_old_messages()
