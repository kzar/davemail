(define-key global-map "\C-cm" 'notmuch)
(setq message-kill-buffer-on-exit t
      notmuch-search-oldest-first t
      notmuch-fcc-dirs
      '(("dvandyke@duckduckgo.com" .
         "\"duckduckgo/Sent Items\" +sent +duckduckgo -inbox")
        (".*" . "\"kzar/Sent\" +sent +kzar -inbox"))
      notmuch-crypto-process-mime nil
      notmuch-saved-searches
      '((:name "inbox" :query "tag:inbox" :key "i")
        (:name "inbox work" :query "tag:inbox AND tag:suboptimal" :key "w")
        (:name "travel" :query "tag:travel" :key "t")
        ;(:name "unread" :query "tag:unread" :key "u")
        (:name "flagged" :query "tag:flagged" :key "f")
        (:name "all mail" :query "*" :key "d")))
(eval-after-load "notmuch"
  (lambda ()
    (define-key notmuch-common-keymap "g" 'notmuch-refresh-this-buffer)
    (define-key 'notmuch-show-part-map "d" 'my-notmuch-show-view-as-patch)))

; Modline incoming message notifications
(setq kzar/notmuch-activity-string "")
(add-to-list 'global-mode-string '((:eval kzar/notmuch-activity-string)) t)
(defun kzar/get-notmuch-incoming-count ()
  (string-trim
   (shell-command-to-string
    "notmuch count tag:inbox AND tag:unread")))
(defun kzar/format-notmuch-mode-string (count)
  (let* ((no-email (string= count "0"))
         (email-icon (if no-email "📭" "📬")))
    (concat email-icon "[" (if no-email "" count) "]")))
(defun kzar/update-notmuch-activity-string (&rest args)
  (setq kzar/notmuch-activity-string
        (kzar/format-notmuch-mode-string (kzar/get-notmuch-incoming-count)))
  (force-mode-line-update))

(add-hook 'notmuch-after-tag-hook 'kzar/update-notmuch-activity-string)
(defcustom notmuch-presync-hook nil
  "Hook run before notmuch is synchronised"
  :type 'hook)
(defcustom notmuch-postsync-hook '(kzar/update-notmuch-activity-string)
  "Hook run after notmuch has been synchronised"
  :type 'hook)

(add-hook 'message-setup-hook
          (lambda ()
            (gnus-alias-determine-identity)
            (define-key message-mode-map (kbd "C-c f")
              (lambda ()
                (interactive)
                (message-remove-header "Fcc")
                (message-remove-header "Organization")
                (gnus-alias-select-identity)
                (notmuch-fcc-header-setup)))
            (flyspell-mode)))

; https://notmuchmail.org/emacstips/#index25h2
(defun my-notmuch-show-view-as-patch ()
  "View the the current message as a patch."
  (interactive)
  (let* ((id (notmuch-show-get-message-id))
         (msg (notmuch-show-get-message-properties))
         (part (notmuch-show-get-part-properties))
         (subject (concat "Subject: " (notmuch-show-get-subject) "\n"))
         (diff-default-read-only t)
         (buf (get-buffer-create (concat "*notmuch-patch-" id "*")))
         (map (make-sparse-keymap)))
    (define-key map "q" 'notmuch-bury-or-kill-this-buffer)
    (switch-to-buffer buf)
    (let ((inhibit-read-only t))
      (erase-buffer)
      (insert subject)
      (insert (notmuch-get-bodypart-text msg part nil)))
    (set-buffer-modified-p nil)
    (diff-mode)
    (lexical-let ((new-ro-bind (cons 'buffer-read-only map)))
                 (add-to-list 'minor-mode-overriding-map-alist new-ro-bind))
    (goto-char (point-min))))

; gnus-alias
(autoload 'gnus-alias-determine-identity "gnus-alias" "" t)
(setq gnus-alias-identity-alist
      '(("kzar"
         nil ;; Does not refer to any other identity
         "Dave Vandyke <kzar@kzar.co.uk>"
         nil ;; No organization header
         nil ;; No extra headers
         nil ;; No extra body text
         nil)
        ("duckduckgo"
         nil ;; Does not refer to any other identity
         "Dave Vandyke <dvandyke@duckduckgo.com>"
         "DuckDuckGo"
         nil ;; No extra headers
         nil ;; No extra body text
         nil)))

(setq gnus-alias-default-identity "kzar")
(setq gnus-alias-identity-rules
      '(("@duckduckgo.com" ("any" "@duckduckgo\\.com" both) "duckduckgo")))

; Outgoing email (msmtp + msmtpq)
(setq send-mail-function 'sendmail-send-it
      sendmail-program "/usr/bin/msmtp"
      mail-specify-envelope-from t
      message-sendmail-envelope-from 'header
      mail-envelope-from 'header)

; PGP encrypted email
(setq notmuch-crypto-mime t
      notmuch-crypto-process-mime t
      mml-secure-openpgp-encrypt-to-self t)
