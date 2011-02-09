HYDE = hyde/hyde.py
FABRIC = fab
SITE = site
DEPLOY = deploy

ifeq ("$(shell uname -o)","Cygwin")
	PYTHON = "/cygdrive/g/Program Files/Python26/python.exe"
else
	PYTHON = "$(shell which python2)"
endif

all:
	$(PYTHON) $(HYDE) -g -s $(SITE) -d $(DEPLOY)

serve:
	cd $(DEPLOY); $(PYTHON) -m SimpleHTTPServer 8080

deploy: all
	$(FABRIC) deploy
    
clean:
	rm -r $(DEPLOY)