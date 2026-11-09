# (C) PSK OG Marienheide e.V., VR/Köln 1369
.PHONY: serve build

serve:
	@bash tools/site-build/run.sh serve

build:
	@bash tools/site-build/run.sh build
