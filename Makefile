APPNAMEID?="com.github.yucefsourani.pysavetube"
DESTDIR?=/
PREFIX?=$(DESTDIR)/usr
datadir?=$(PREFIX)/share
INSTALL=install
PYTHON=/usr/bin/python3

all:  icons pos

icons:
	for i in 8 16 22 24 32 36 48 64 72  96 128 256 512; do \
	mkdir -p icons/hicolor/$${i}x$${i}/apps;\
	convert pixmaps/$(APPNAMEID).png -resize $${i}x$${i} icons/hicolor/$${i}x$${i}/apps/$(APPNAMEID).png;done
pos:

	make -C po all
pot:

	make -C po pysavetube.pot

installall: all
	$(PYTHON) setup.py install --prefix=$(PREFIX)

install: 
	$(PYTHON) setup.py install --prefix=$(PREFIX)
	
flatpakinstall:
	$(PYTHON) setup.py install --prefix=/app

clean:
	rm -fr  icons

