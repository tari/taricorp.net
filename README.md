## TODO

[x] Post timestamps should include the year
[ ] show the subtitle from front matter under titles
[x] Make post titles on the front page link to the full post page
[x] Increase max width of text as modded in wordpress
[x] unstick top bar as modded in wordpress
[ ] fix colors of highlighted code to be readable
[ ] Support hugo summaries (<!-- more -->) in template
[x] get /post/ out of post URLs
[ ] broken post permalinks, eg hodorCSE and older
[x] pagination styling
[ ] include last updated time next to first published time
[ ] responsive reflow seems wonky, xref wordpress (maybe just take the whole
    wordpress stylesheet
[ ] change searchform.html to use ddg (or a choice?)
[ ] figures are wonky (xref matroishka)
[ ] audit jquery use (functions.js in particular)
[ ] xref header link tags against current
[ ] what's up with \_pages?

## Optimization

Set up to minify resources with `gulp`. First `npm install`, then invoke `gulp`
to (by default) copy Hugo's output to the `public-min` directory and minify the
appropriate resources.

Borrowed from https://github.com/bonnici/gulp-hugo-workflow/. Also supports
watching for updates and automatically reloading which might be interesting to
try out.

## Images

optimage: https://github.com/sk-/optimage
In particular zopflipng gets good compression

butteraugli makes it easier to evaluate lossy compressions:
https://github.com/google/butteraugli

pngquant can do nice possibly-lossless compression of PNGs,
pngcrush too
