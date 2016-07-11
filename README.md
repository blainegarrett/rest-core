# rest-core
Simple custom RESTful Framework designed for webapp2 on Google Appengine


NOTE: This specific codebase is not currently in use and is not complete. Use at your own risk.


Initial Development Setup
-----
To develop this project, check out `git@github.com:blainegarrett/rest-core.git`
* Install (virtualenvwrapper)[http://virtualenvwrapper.readthedocs.io/en/latest/install.html]
* `cd <path to git checkout>`
* `mkvirtualenv rest-core`
* Once complete be sure to run the following installation step

Installation
-----
Upon initial development setup or on consecutive checkouts, to install pip dependencies:
* `cd <path to git checkout>`
* `make install`

Running Unit Tests
-----
* `cd <path to git checkout>`
* `make unit`

Running Example App (not currently a full example)
-----
* cd to check out directory
* `dev_appserver.py .`
Open in browser or a REST application like PAW


TODO
-----
* Add unit tests for handler code
* Flesh out example
* Release a 0.1.0 version
* Add code coverage
* Make a pip installable package
