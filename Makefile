HYDE = "hyde/hyde.py"
SITE = "site"
DEPLOY = "deploy"

ifeq ("$(shell uname -o)","Cygwin")
	PYTHON = "/cygdrive/g/Program Files/Python26/python.exe"
else
	PYTHON = "$(shell which python)"
endif

all:
	$(PYTHON) $(HYDE) -g -s $(SITE) -d $(DEPLOY)

watch:
	$(PYTHON) $(HYDE) -g -s $(SITE) -d $(DEPLOY) -k

serve: all
	$(PYTHON) $(HYDE) -w -s $(SITE) -d $(DEPLOY)