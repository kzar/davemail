import davemail
from hacks.rietveld import fix_rietveld_emails

if __name__ == "__main__":
  # Take care to move messages which were tagged after synchronisation started.
  davemail.move_tagged_messages()
  # Now we can update the database.
  davemail.update_database()
  # The codereview tool we use called Rietveld doesn't get threading
  # headers or line wrapping right. To make my life easier I fix those
  # here, but it's a huge hack! Both mbsync and notmuch consider messages
  # immutable so modifying them is a bad idea, don't do this at home! :(
  fix_rietveld_emails("tag:new subject:issue subject:by " +
                      "https://codereview.adblockplus.org")
  # Tidy up our tags, removing "new" and adding others based on folder.
  davemail.tag_moved_messages()
  davemail.tag_messages("tag:new", "-new")
  davemail.run_emacs_hook("notmuch-postsync-hook")
