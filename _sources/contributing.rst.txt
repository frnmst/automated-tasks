Contributing
============

Git branches
------------

What follows is a table of the git branches used in this repository.

.. important:: Open pull requests on the ``dev`` target branch.
               Use ``bugfix-${fix_name}`` or ``newfeature-${new_feature_name}`` as names.

=====================================   ====================================================   ==============================
Branch                                  Description                                            Update schedule
=====================================   ====================================================   ==============================
``master``                              the main branch                                        every new release
``dev``                                 recent changes are merged here before a new release    at will
``gh-pages``                            contains the built documentation only                  every new release
``bugfix-${fix_name}``                  a generic bug fix
``newfeature-${new_feature_name}``      a generic new feature
=====================================   ====================================================   ==============================

Dependencies
------------

First of all install `pipenv <https://pipenv.readthedocs.io/en/latest/>`_ and then
install the software requirements from the Pipfile in the repository's root:


::


    $ make install-dev


Documentation
-------------

You can edit and rebuild all this documentation with:


::


    $ make doc


TODO and FIXME
--------------

Go in the repository's root and then:


::

    $ grep -e TODO -e FIXME -n */*.py


Contribution Steps
------------------

1. clone the repository
2. install the requirements
3. write code
4. update relevant documentation, if necessary
5. pull request
