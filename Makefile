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
	s3cmd -P sync deploy/ s3://www.taricorp.net/
    
clean:
	rm -r $(DEPLOY)
