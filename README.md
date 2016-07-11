# rest-core
Simple custom RESTful Framework designed for webapp2 on Google Appengine

Initial Development Setup
-----
To develop this project, check out `git@github.com:blainegarrett/rest-core.git`
* Install (virtualenvwrapper)[http://virtualenvwrapper.readthedocs.io/en/latest/install.html]
* `cd <path to git checkout>`
* mkvirtualenv rest-core

Installation
-----
Upon initial development setup or on consecutive checkouts, to install pip dependencies:
* `make install`

Running Unit Tests
-----
`make unit`

Running Example App
-----
* cd to check out directory
* `dev_appserver.py example`
Open in browser or a REST application like PAW



TODO
-----
* Release a 0.1.0 version
* Add code coverage
* Make a pip installable package
