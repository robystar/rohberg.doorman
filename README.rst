==================
rohberg.doorman
==================


What is rohberg.doorman ?
=========================

This package provides Plone sites with a configuration of a custom password policy.

It also lets you configure a Plone site to force password reset after defined time.

Non-Members can be disclosed from entering Site.

Works with
==========

* Plone 4

Configuration
==============

Open the security control panel of your Plone site. New fields let you 
define your custom password policy via regular expressions and define password expiration.


Password Policy
=============================

As long as no custom policy is configured, default policy as defined in this package is effective. You can review and edit the effective password policy on security control panel.

Password Duration
============================

If an expiration of password is defined in security control panel and user has not reset his password during defined expiration time reset password form is presented to user after login attempt which is rejected.

Private RSS Feeds
========================

Prevent redirect to login page for paths mentioned in control panel


Links
=====

Cheeseshop
  http://pypi.python.org/pypi/rohberg.doorman

Git repository
  https://github.com/ksuess/rohberg.doorman

Issue tracker
  https://github.com/ksuess/rohberg.doorman/issues

Contributors
============

* Katja Süss

Credits
============

Thanks to Dylan Jay, Daniel Nouri and BlueDynamics for PAS plugin stuff of PasswordStrength.

Thanks to Nathan Van Gheem for annotation stuff of PloneTrueGallery.

Thanks to Bertrand Mathieu, Thomas Desvenain, Gilles Lenfant, Elisabeth Leddy for 
control panel stuff of iw.rejectanonymous

License
=======

Distributed under the GPL.

See LICENSE.txt and LICENSE.GPL for details.

Tests
======

done!
