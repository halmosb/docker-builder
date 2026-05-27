SPHINXBUILD = sphinx-build
SOURCEDIR   = docs
BUILDDIR    = docs/_build

.PHONY: html clean

html: clean
	$(SPHINXBUILD) -b html $(SOURCEDIR) $(BUILDDIR)/html
	@echo "Docs built: $(BUILDDIR)/html/index.html"

clean:
	rm -rf $(BUILDDIR)
