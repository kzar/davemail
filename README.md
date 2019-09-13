# Davemail

## Introduction

My email setup, now under source control as it is getting rather complex!

0. My personal emails come into my [FastMail][1] account, work ones into Gmail.
1. [mbsync][2] is used to keep a local copy of my emails synchronised using
   IMAP. (Much more efficient and reliably than [offlineimap][3] once set up
   correctly. Unfortunately setting it up correctly [wasn't trivial][4]).
2. My pre and post synchronisation scripts are run which take care of
   the tag to folder mapping as specified in .davemailrc. For example,
   a message with the tag `inbox` should be moved to the `INBOX` folder, and a
   message with no relevant tags should be moved to the `Archive` folder.
   For my work emails new messages are tagged (e.g. spam), but the folder to tag
   mapping isn't maintained.
3. Those scripts also run my pre and post synchronisation hooks in Emacs, which
   I then use to update my modeline display etc.
4. [Notmuch][6] Emacs client is then used for reading and tagging message.
   [Gnus alias][7] for handling my different email identities + signatures.
5. Outgoing emails are sent using [msmtp][8] ~~and the [msmtpq][9] script~~,
   back out via FastMail or Gmail's servers.
6. [vdirsyncer][10] synchronises my contacts and calendars with FastMail so
   that I have a local copy to use for address completion etc.

## Usage

_(Not actually supposed to be used by other people...)_

1. Install Emacs, Notmuch, msmtp, msmtpq, isync, gpg, libsecret-tools,
   vdirsyncer etc.
2. Install Python and configobj.
3. Set up [my Emacs config][5].
4. Store email server passwords e.g.
   `secret-tool store --label="Email: kzar@kzar.co.uk" email kzar@kzar.co.uk`
5. Set up symlinks for the configuration files:
```
ln -s ~/path/to/davemail/.mbsyncrc ~/
ln -s ~/path/to/davemail/.msmtprc ~/
ln -s ~/path/to/davemail/.notmuch-config ~/
ln -s ~/path/to/davemail/.vdirsyncerrc ~/.vdirsyncer/config
```

- Run `./syncmail` to do a complete mail synchronisation every two minutes.
- Press Enter to have the script synchronise again immediately.
- Run `vdirsyncer sync` to synchronise personal contacts and calendar with
  Fastmail.

## TODO

- Figure out how to consider the address the original email was to when
  forwarding emails. Currently, the wrong alias is often used.
- Figure out why forwarded messages sometimes get mangled.
- Ditch webmail/mobile email completely?!
- [Set up imapnotify to trigger mbsync, rather than polling.][11]
- If sending fails and the mail is later sent from the msmtp queue the Fcc copy
  to the Sent folder is not written.
- Sending emails using msmtp blocks Emacs, which sucks when the connection to
  Fastmail is slow.
- Finish the old message archiving functionality?
- Figure out how to delete emails from Gmail properly and fix the folder to
  tag mapping there.
- Perhaps replace some of davemail.py with [imapfilter][12]?
- Have notmuch use my local copy of my contacts [for address completion][13] as
  well as the notmuch database. (See `notmuch-address-command`.)
- Use [syncmaildir][14] instead of IMAP?
- Replace msmtp and msmtpq with [nullmailer][15]?

[1]: https://fastmail.com
[2]: http://isync.sourceforge.net/mbsync.html
[3]: http://www.offlineimap.org
[4]: http://isync.sourceforge.net/mbsync.html#INHERENT%20PROBLEMS
[5]: https://github.com/kzar/emacs.d
[6]: https://notmuchmail.org/
[7]: https://www.emacswiki.org/emacs/GnusAlias
[8]: http://msmtp.sourceforge.net/
[9]: https://www.emacswiki.org/emacs/GnusMSMTP#toc3
[10]: https://vdirsyncer.pimutils.org/en/stable/index.html
[11]: https://martinralbrecht.wordpress.com/2016/05/30/handling-email-with-emacs/
[12]: https://raymii.org/s/blog/Filtering_IMAP_mail_with_imapfilter.html
[13]: https://notmuchmail.org/emacstips/#index13h2
[14]: http://syncmaildir.sourceforge.net/
[15]: http://www.troubleshooters.com/linux/nullmailer/
