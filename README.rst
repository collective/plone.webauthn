.. This README is meant for consumption by humans and PyPI. PyPI can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on PyPI or github. It is a comment.

.. image:: https://github.com/collective/plone.webauthn/actions/workflows/plone-package.yml/badge.svg
    :target: https://github.com/collective/plone.webauthn/actions/workflows/plone-package.yml

.. image:: https://coveralls.io/repos/github/collective/plone.webauthn/badge.svg?branch=main
    :target: https://coveralls.io/github/collective/plone.webauthn?branch=main
    :alt: Coveralls

.. image:: https://codecov.io/gh/collective/plone.webauthn/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/collective/plone.webauthn

.. image:: https://img.shields.io/pypi/v/plone.webauthn.svg
    :target: https://pypi.python.org/pypi/plone.webauthn/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/status/plone.webauthn.svg
    :target: https://pypi.python.org/pypi/plone.webauthn
    :alt: Egg Status

.. image:: https://img.shields.io/pypi/pyversions/plone.webauthn.svg?style=plastic   :alt: Supported - Python Versions

.. image:: https://img.shields.io/pypi/l/plone.webauthn.svg
    :target: https://pypi.python.org/pypi/plone.webauthn/
    :alt: License

==============
plone.webauthn
==============

webauthn addon for plone

Features
--------

- Register devices using Webauthn and use it later to authenticate without using a password.
- Add or Delete Webauthn Credentials.


Examples
--------

This add-on can be seen in action at the following sites:
- Is there a page on the internet where everybody can see the features?


Documentation
-------------

Full documentation for end users can be found in the "docs" folder and is also available online at http://docs.plone.org/foo/bar


Translations
------------

This product has been translated into

- Klingon (thanks, K'Plai)


Installation
------------

Install plone.webauthn by adding it to your buildout::

    [buildout]

    ...

    eggs =
        plone.webauthn


and then running ``bin/buildout``

Install the PAS plugin using::

    http://localhost:8080/Plone/install-pas

Key management
--------------

    http://localhost:8080/Plone/key-management


Authors
-------

Provided by awesome people ;)


Contributors
------------

Put your name here, you deserve it!

- Pavan Kalyan Thota


Contribute
----------

- Issue Tracker: https://github.com/collective/plone.webauthn/issues
- Source Code: https://github.com/collective/plone.webauthn
- Documentation: https://docs.plone.org/foo/bar


Support
-------

If you are having issues, please let us know.
We have a mailing list located at: project@example.com


License
-------

The project is licensed under the GPLv2.
