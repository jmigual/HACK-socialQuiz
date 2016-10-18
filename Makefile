FOLDER = frontend

EXCLUDE = $(wildcard $(FOLDER)/*-compiled*)
SRC = $(filter-out $(EXCLUDE), $(wildcard $(FOLDER)/*.js))
MIN_FILES = $(SRC:.js=-compiled.min.js)

BABEL = ${CURDIR}/node_modules/.bin/babel
BABEL_OPTS = --presets es2015

UGLIFY = ${CURDIR}/node_modules/.bin/uglifyjs
UGLIFY_OPTS = --compress --mangle


.PHONY: all

all: $(MIN_FILES)

rebuild: clean all

%-compiled.min.js: %.js
	$(BABEL) $(BABEL_OPTS) $< | $(UGLIFY) $(UGLIFY_OPTS) -o $@

setup:
	npm install babel-cli babel-preset-es2015
	npm install uglify-js

clean:
	rm $(FOLDER)/*compiled*

clean-deps:
		rm -rf node_modules