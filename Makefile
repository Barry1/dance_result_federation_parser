
OBJS=dtvprocessing.py resultParser.py stringprocessing.py topturnierprocessing.py tpsprocessing.py

pylint:
	pylint $(OBJS)

mypy:
	mypy --install-types --non-interactive $(OBJS)