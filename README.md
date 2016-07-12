# rest-core
Simple custom RESTful Framework designed for webapp2 on Google Appengine

NOTE: This specific codebase is not currently in use and is not production grade. Use at your own risk. If you'd like me to continue developing it, let me know or make a pull request.

General Usage
-----
See example directory for runnable implementation of a simple Blogpost api.
Have your route handlers extend `rest_core.RestHandlerBase`. Define your resource rules using existing voluptuous validators or write your own. Then implement _get, _post, _put, or _delete handlers as needed to talk to your own internal api.

General Best Practices
-----
In general use routes like:
* `/posts`  - Collection of resources, plural with no trailing slash. POST creates new resource, GET fetches resources with optional filters. (No PUT nor DELETE)
* `/posts/<resource_id>` - A single resource. GET fetches single resource, PUT edits resource, DELETE removes resource. (Typically no PUT)


Initial Development Setup
-----
To develop this project, check out `git@github.com:blainegarrett/rest-core.git`
* Install [virtualenvwrapper](http://virtualenvwrapper.readthedocs.io/en/latest/install.html)
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
* `cd to check out directory`
* `dev_appserver.py .`
* Open in browser or a REST application like PAW.
* Collection endpoint is located at `/posts`


TODO
-----
* Add unit tests for handler code
* Remove various mplsart.com specific bits for whitelisting, etc
* Flesh out example
* Release a 0.1.0 version
* Add code coverage
* Make a pip installable package
