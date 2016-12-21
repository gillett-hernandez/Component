all:
	make test
	python main.py

lfclone:
	python lfclone.py

test:
	python component.py --test
	python vector.py

clean:
	rm *.pyc *.log
	rm -r ./__pycache__
