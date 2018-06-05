all:
	pwd
	make clean
	# make test
	make --output-sync=line -B lfclone
	

# .PHONY: lfclone, platformer

lfclone: lfclone/main.py
	cd .. && python -m Component.lfclone.main

platformer:
	cd .. && python -m Component.platformer.main

test:
	python component.py --test
	python vector.py --test

clean:
	$(RM) *.pyc
	$(RM) *.log
	$(RM) -r ./__pycache__

