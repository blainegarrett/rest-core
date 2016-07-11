clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

install:
	pip install -r requirements_dev.txt
	linkenv $(PYTHON_SITE_PACKAGES_PATH) ./external
	@echo "Yay! Everything installed."


unit:
	nosetests -sv -a is_unit --with-gae --gae-application=rest_core --with-yanc
