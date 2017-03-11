# Davemail

## Introduction

My email setup, now under source control as it is getting rather complex!

0. My emails come in to my [FastMail][1] account.
1. [mbsync][2] is used to keep a local copy of my emails synchronised using
   IMAP. (Much more efficient and reliably than [offlineimap][3] once set up
   correctly. Unfortunately setting it up correctly [wasn't trivial][4]).
2. My pre and post synchronisation scripts are run which take care of keeping
   enforcing the tag to folder mapping as specified in .davemailrc. For example
   a message with the tag `inbox` should be moved to the `INBOX` folder and a
   message with no relevant tags should be moved to the `Archive` folder.
3. Those scripts also run my pre and post synchronisation hooks in Emacs, which
   I then use to update my modeline display etc. (See [my Emacs config][5].)
4. [Notmuch][6] Emacs client is then used for reading and tagging message.
   [Gnus alias][7] for handling my different email identities + signatures.
5. Outgoing emails are sent using [msmtp][8] and the [msmtpq][9] script, back
   out via FastMail's servers.


## Usage

_(Not actually supposed to be used by other people...)_

- Set up [my Emacs config][5].
- Create `password.gpg` with the FastMail password.

- Run `./syncmail` to do a complete mail synchronisation every two minutes.
- Run `./syncmail 1` to fetch incoming emails every 30 seconds.
- Press Enter to have the script synchronise again immediately.


## TODO

- Figure out why forwarded messages sometimes get mangled.
- Ditch webmail / mobile email completely?!
- [Set up imapnotify to trigger mbsync, rather than polling.][10]
- Fix up Rietveld emails:
 - Quoted text is often wrapped too eagerly.
 - No thread ID is given so messages aren't kept together.


[1]: https://fastmail.com
[2]: http://isync.sourceforge.net/mbsync.html
[3]: http://www.offlineimap.org
[4]: http://isync.sourceforge.net/mbsync.html#INHERENT%20PROBLEMS
[5]: https://github.com/kzar/emacs.d
[6]: https://notmuchmail.org/
[7]: https://www.emacswiki.org/emacs/GnusAlias
[8]: http://msmtp.sourceforge.net/
[9]: https://www.emacswiki.org/emacs/GnusMSMTP#toc3
[10]: https://martinralbrecht.wordpress.com/2016/05/30/handling-email-with-emacs/
