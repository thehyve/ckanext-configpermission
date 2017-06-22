=============
ckanext-configpermission
=============

.. Put a description of your extension here:
   What does it do? What features does it have?
   Consider including some screenshots or embedding a video!


------------
Requirements
------------

Tested on CKAN 2.5


------------
Installation
------------

.. Add any additional install steps to the list below.
   For example installing any non-Python dependencies or adding any required
   config settings.

To install ckanext-configpermission:

1. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

2. Install the ckanext-configpermission Python package into your virtual environment::

     pip install ckanext-configpermission

3. Add ``configpermission`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     sudo service apache2 reload


5. Run database init
   paster --plugin=ckanext-configpermission init -c /etc/ckan/default/production.ini

6. Create default data
   paster --plugin=ckanext-configpermission defaultdata -c /etc/ckan/default/production.ini


---------------
Config Settings
---------------

Select the permissions to be managed in the ckan configuration file. Like so
    ckan.configpermission.permissions = package_show member_delete group_create resource_update package_show resource_show


------------------------
Development Installation
------------------------

To install ckanext-configpermission for development, activate your CKAN virtualenv and
do::

    git clone https://github.com/thehyve/ckanext-configpermission.git
    cd ckanext-configpermission
    python setup.py develop
    pip install -r dev-requirements.txt


-----------------
Running the Tests
-----------------

To run the tests, do::

    nosetests --nologcapture --with-pylons=test.ini

To run the tests and produce a coverage report, first make sure you have
coverage installed in your virtualenv (``pip install coverage``) then run::

    nosetests --nologcapture --with-pylons=test.ini --with-coverage --cover-package=ckanext.configpermission --cover-inclusive --cover-erase --cover-tests


---------------------------------
Registering ckanext-configpermission on PyPI
---------------------------------

ckanext-configpermission should be availabe on PyPI as
https://pypi.python.org/pypi/ckanext-configpermission. If that link doesn't work, then
you can register the project on PyPI for the first time by following these
steps:

1. Create a source distribution of the project::

     python setup.py sdist

2. Register the project::

     python setup.py register

3. Upload the source distribution to PyPI::

     python setup.py sdist upload

4. Tag the first release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.1 then do::

       git tag 0.0.1
       git push --tags


----------------------------------------
Releasing a New Version of ckanext-configpermission
----------------------------------------

ckanext-configpermission is availabe on PyPI as https://pypi.python.org/pypi/ckanext-configpermission.
To publish a new version to PyPI follow these steps:

1. Update the version number in the ``setup.py`` file.
   See `PEP 440 <http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers>`_
   for how to choose version numbers.

2. Create a source distribution of the new version::

     python setup.py sdist

3. Upload the source distribution to PyPI::

     python setup.py sdist upload

4. Tag the new release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.2 then do::

       git tag 0.0.2
       git push --tags
