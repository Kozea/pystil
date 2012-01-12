====================
 User Documentation
====================

:Author: Arthur Vuillard

:Date: 2012-01-11

:Abstract: This document is a short description for installing and using the
 Pystil web traffic analyzer.

.. contents::

Installation
============

Download
--------

At the time, you can only download Pystil via git. To do so, you should 
first install git and then::

  git clone https://github.com/Kozea/pystil.git

Requirements
------------

The server side of Pystil is written in Python. It needs some libraries :

- flask (>=0.8)
- flask-sqlalchemy
- CSStyle
- pika
- gevent
- pygeoip
- log_colorizer
- psycopg2

It also need a working PostgreSQL server (with hstore extension) and a 
RabbitMQ server.

Libraries
---------

You should install the different libraries with easy_install. As root, 
type::

  easy_install flask flask-sqlalchemy pika gevent pygeoip CSStyle psycopg2
  
.. note::
   In order to install gevent, you should first install some tools like gcc 
   and some development files like libevent and python headers.

.. note::
   In order to install psycopg2, you should first install libraries like 
   postgresql-server development files.

To install log_colorizer, as root, from the pystil dir, do::

  pip install -r requirements.txt
  
Servers
-------

PostgreSQL
~~~~~~~~~~

You should install postgresql version 9.1 and its hstore extension.

In Ubuntu 11.10, type::

  sudo apt-get install postgresql postgresql-contrib

RabbitMQ
~~~~~~~~

Just install RabbitMQ server.

In Ubuntu 11.10, type::

  sudo apt-get install rabbitmq-server
  
Setup
=====

PostgreSQL schema
-----------------

First of all, you should log in postgresql with a super user. 
Then, import file sql/pystil.sql::

  \i sql/pystil.sql
  
By default, it create a pystil user whose password is "pystil". If you
want to change it to "your_new_password", just enter::

  ALTER ROLE pystil PASSWORD 'your_new_password';

Pystil configuration
--------------------

Copy the file .pystil-secrets (present in the pystil directory from git) to 
your home, and edit it::

  cp .pystil-secrets ~
  edit ~/.pystil-secrets 
  	
You must now generate a secret key and enter it in the file. You should also 
enter your PostgreSQL password that you entered in the create role statement 
(if you just followed this lines, it should be "pystil").

If you want to use LDAP as an authentication backend, you should also fill 
the fields "LDAP_HOST" and "LDAP_PATH". 

Logging
-------

.. warning::
   TODO
   
