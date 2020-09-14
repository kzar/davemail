import davemail

if __name__ == "__main__":
  # Take care to move messages which were tagged after synchronisation started.
  davemail.move_tagged_messages()
  # Now we can update the database.
  davemail.update_database()
  # Tidy up our tags, removing "new" and adding others based on folder.
  davemail.tag_moved_and_new_messages()
  davemail.tag_messages("tag:new AND from:feedback@slack.com AND " +
                        "subject:'reminder'", "+muted")
  davemail.tag_other_header_match("tag:new",
                                  "X-Original-Delivered-to",
                                  ".*suboptimal\.co\.uk$", "+suboptimal")
  davemail.tag_muted_threads()
  davemail.tag_messages("tag:new", "-new")
  davemail.run_emacs_hook("notmuch-postsync-hook")
