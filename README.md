# rest_core
Simple custom RESTful Framework designed for webapp2


General Usage
-----
See example directory for runnable implementation of a simple Blogpost api.
Have your route handlers extend `rest_core.handlers.RestHandlerBase`. Define your resource rules using existing voluptuous validators or write your own. Then implement `get`, `post`, `put`, or `delete` methods as needed to talk to your own internal apis.

General Best Practices
-----
In general use routes like:
* `/posts`  - Collection of resources, plural with no trailing slash. POST creates new resource, GET fetches resources with optional filters. (No PUT nor DELETE)
* `/posts/<resource_id>` - A single resource. GET fetches single resource, PUT edits resource, DELETE removes resource. (Typically no PUT)

Installation
-----
Upon initial development setup or on consecutive checkouts, to install pip dependencies:
* `cd <path to git checkout>`
* `make install`

Pip Editable Installation
-----
To develop (or debug) a checkout rest_core while installed as a pip dependency in your project follow these steps:

* Be sure you are in your project dir (pwd) and that your virtual environment is active (you really should be using virtual environments)
* `pip uninstall rest_core`
* `pip freeze` // ensure rest_core is gone
* `pip install -e /absolute/path/to/your/checkout/of/rest_core`
* `pip freeze` // ensure rest_core is listed - it may show as github url, `-e` at the beginning is important

Note: Due to a pip bug, you cannot used --editable and --target in the same call. As such, if you use a target, (such as with GAE vendoring), you'll need to symlink.

Note: If using Google Appengine + Vendoring, you additionally need to symlink the editable package into your vendor location. This is due to GAE not including `site-packages/easy-install.pth` in the PYTHON_PATH and thus it needs to be symlink'd to something on the path.
* `ln -s /absolute/path/to/your/checkout/of/rest_core/rest_core /absolute/path/to/vendor/dependencies`


Initial Development Setup
-----
To develop this project, check out `git@github.com:digibodies/rest_core.git`
* Install [virtualenvwrapper](http://virtualenvwrapper.readthedocs.io/en/latest/install.html)
* `cd <path to git checkout>`
* `mkvirtualenv rest_core -a .`
* Once complete be sure to run the following installation steps above


Running Unit Tests
-----
* `cd <path to git checkout>`
* `make unit`

Running Example App
-----
An example application is located at [https://github.com/digibodies/rest_core_demo](https://github.com/digibodies/rest_core_demo)



TODO
-----
* Add unit tests for handler code
* Flesh out example
* Release a 0.1.0 version
* Add code coverage
* Remove all dependency on google appengine
* Add support for exception middleware
* Support debug mode for exception bubbling
* Wrap voluptuous
* Support for caching
