.PHONY: deploy site

SITE=beta.taricorp.net

site:
	jekyll build

deploy: site
	rsync -avz --delete _site/ $(SITE):/var/www/$(SITE)/public_html/
