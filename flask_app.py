#!/bin/env -S poetry run python -OO
# flask --debug --app flask_test run
from contextlib import redirect_stdout
from io import StringIO

from flask import Flask, request

import dance_result_federation_parser

app = Flask(__name__)


@app.route("/", methods=["GET"])  # POST not working like I think
def result() -> str:
    """Build Website and if getURL try to read couples results."""
    #    theurl = "https://tanzen-in-sh.de/ergebnisse/2024/2024-02-24_GLM_MasIV_STD/index.htm"
    theurl: str | None = request.args.get("theurl")
    the_cms_code: str = ""
    if theurl:
        outputcollector = StringIO()
        with redirect_stdout(outputcollector):
            dance_result_federation_parser.eventurl_to_web(theurl)
        the_cms_code: str = outputcollector.getvalue()
    thehtmlpage: str = (
        "<html><head><title>Flask-Test</title></head><body>"
        + '<form action="/" method="get">'
        + "<table><tr>"
        + '<td><label for="fname">Veranstaltungs-URL (inklusive index.html):</label></td>'
        + '<td><input type="text" id="theurl" name="theurl"></td>'
        + "</tr><tr><td></td>"
        + '<td><input type="submit" value="Submit"></td>'
        + "</tr></table>"
        + "</form>"
        + "<p>Copy and paste the contents of the text area into your CMS.</p>"
        + f'<textarea rows="30" cols="130">{the_cms_code}</textarea>'
        + "</body></html>"
    )
    return thehtmlpage


if __name__ == "__main__":
    app.run(debug=__debug__)
