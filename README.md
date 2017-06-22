ckanext-configpermission

Adds a way for sysadmins to configure CKAN permissions via a web interface and create new organization roles.


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

    nosetests --paster=ckanext-configpermission --nologcapture --with-pylons=test.ini -c /etc/ckan/default/production.ini
