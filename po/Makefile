POTFILE=$(shell cat POTFILES.in)
SOURCES=$(addprefix ../, $(POTFILE))
POFILES=$(wildcard *.po)
MOFILES=$(patsubst %.po,%.mo,$(POFILES))
all: $(MOFILES)

pysavetube.pot: $(SOURCES)
	intltool-update -g pysavetube -p

%.mo: %.po
	msgfmt $*.po -o $*.mo
	mkdir -p ../locale/$*/LC_MESSAGES/ || :
	cp $*.mo ../locale/$*/LC_MESSAGES/pysavetube.mo

%.po: pysavetube.pot
	intltool-update -g pysavetube -d $*

