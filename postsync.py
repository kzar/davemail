import davemail

if __name__ == "__main__":
  davemail.tag_moved_messages()
  davemail.run_emacs_hook("notmuch-postsync-hook")
