all: pylint-src black pytest mypy

pylint-src:
	pylint pyppy/

pylint-test:
	pylint test/

black:
	black pyppy/

pytest:
	pytest test/

mypy:
	mypy pyppy/

htmldoc:
	cd docs && \
	make clean && \
	sphinx-apidoc --force -e -o ./source ../pyppy && \
 	cd .. && \
 	rm README.rst || true && \
 	m2r README.md && \
 	mv README.rst docs/source/readme.rst && \
 	cd docs && \
 	make html