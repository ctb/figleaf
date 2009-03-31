PYTHON=python
PYINCLUDE = $(shell $(PYTHON) -c 'import os, sys; print os.sep.join((sys.prefix, "include", "python" + sys.version[:3]))')
CFLAGS:=-O2 -Wall -I$(PYINCLUDE) -fPIC $(CFLAGS) -ggdb
CC=gcc $(CFLAGS)

.PHONY: clean

all: _coverage.so

_coverage.so: _coverage.c
	$(CC) -shared -o $@ $^

clean:
	rm -f *.o *.so *.pyc *~
