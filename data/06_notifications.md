# Email Notifications

## Missing messages
Notification emails are sent from `notify@northstar.example`. Confirm the recipient is active, notifications are enabled for the relevant event, and the address is not on the organization suppression list. Ask the mail administrator to allow the sender and check quarantine logs.

## Bounces and suppression
A hard bounce places the address on the suppression list to protect delivery reputation. An organization administrator can view suppression status, but only support can remove a suppression after the mailbox is confirmed valid. Suppression removal is an account-sensitive operation and requires escalation.

## Delivery evidence
Collect the recipient domain, event time, notification type, and message ID shown in the audit log. Do not request the contents of private emails.

