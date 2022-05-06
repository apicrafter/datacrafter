========================================================================================
pumpilo -- a data extraction and packaging tool with autodocumentation and NoSQL support
========================================================================================


pumpilo is a command line tool that helps to extract NoSQL data from data sources and to package it for future use.
Its goal is to make ETL tool with advanced features like automatic documentation, type conversion and so on.
It provides a simple ``pumpilo`` command that allows run pipelines and to extract data from files and API, autodocument and process it.


.. contents::

.. section-numbering::



Main features
=============




Installation
============


macOS
-----


On macOS, pumpilo can be installed via `Homebrew <https://brew.sh/>`_
(recommended):

.. code-block:: bash

    $ brew install pumpilo


A MacPorts *port* is also available:

.. code-block:: bash

    $ port install pumpilo

Linux
-----

Most Linux distributions provide a package that can be installed using the
system package manager, for example:

.. code-block:: bash

    # Debian, Ubuntu, etc.
    $ apt install pumpilo

.. code-block:: bash

    # Fedora
    $ dnf install pumpilo

.. code-block:: bash

    # CentOS, RHEL, ...
    $ yum install pumpilo

.. code-block:: bash

    # Arch Linux
    $ pacman -S pumpilo


Windows, etc.
-------------

A universal installation method (that works on Windows, Mac OS X, Linux, вЂ¦,
and always provides the latest version) is to use pip:


.. code-block:: bash

    # Make sure we have an up-to-date version of pip and setuptools:
    $ pip install --upgrade pip setuptools

    $ pip install --upgrade pumpilo


(If ``pip`` installation fails for some reason, you can try
``easy_install pumpilo`` as a fallback.)


Python version
--------------

Python version 3.6 or greater is required.



Usage
=====


Synopsis:

.. code-block:: bash

    $ pumpilo [flags] [command] 


See also ``pumpilo --help``.


Commands
========

