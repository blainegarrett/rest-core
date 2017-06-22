clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

install:
	pip install -Ur requirements_dev.txt
	pip install -Ur requirements.txt -t ./external
	@echo "Dependencies for rest_core installed."

unit:
ifeq ($(filter-out $@,$(MAKECMDGOALS)), "")
	@echo "Running all unit tests"
else
	@echo "Running only tests in $(filter-out $@,$(MAKECMDGOALS))"
endif
	nosetests -sv -a is_unit --with-gae --gae-application=rest_core --with-yanc $(filter-out $@,$(MAKECMDGOALS))

integrations:
ifeq ($(filter-out $@,$(MAKECMDGOALS)), "")
	@echo "Running all integration tests"
else
	@echo "Running only integration tests in $(filter-out $@,$(MAKECMDGOALS))"
endif
	nosetests -sv --with-gae --gae-application=rest_core --with-yanc $(filter-out $@,$(MAKECMDGOALS))

run:
	dev_appserver.py example --port=8080