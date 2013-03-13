==================
rohberg.doorman
==================


What is rohberg.doorman ?
=========================

This package provides you with a configuration of a custom password policy.

Works with
==========

* Plone 4

Installation
============

If you are using zc.buildout and the plone.recipe.zope2instance
recipe to manage your project, you can do this:

* Add ``rohberg.doorman`` to the list of eggs to install, e.g.:

    [buildout]
    ...
    eggs =
        ...
        rohberg.doorman
       
* Tell the plone.recipe.zope2instance recipe to install a ZCML slug:

    [instance]
    recipe = plone.recipe.zope2instance
    ...
    zcml =
        rohberg.doorman
      
* Re-run buildout, e.g. with:

    $ ./bin/buildout
        
You can skip the ZCML slug if you are going to explicitly include the package
from another package's configure.zcml file.

Then open the "Security" control panel of your Plone site. A new field lets you 
define your custom password policy via regular expressions.


Default Password Policy
=============================

As long no custom policy is configured, default policy as defined in this package is effective. You can review and edit the effective password policy on security control panel.

Links
=====

Cheeseshop
  http://pypi.python.org/pypi/rohberg.doorman

Git repository
  https://github.com/rohberg/rohberg.doorman

Issue tracker
  https://github.com/rohberg/rohberg.doorman/issues

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
