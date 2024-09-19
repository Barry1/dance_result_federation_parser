# flask --debug --app flask_test run
from contextlib import redirect_stdout
from io import StringIO

from flask import Flask, request

import dance_result_federation_parser

app = Flask(__name__)


@app.route("/", methods=["GET"])  # POST not working like I think
def result() -> str:
    #    theurl = "https://tanzen-in-sh.de/ergebnisse/2024/2024-02-24_GLM_MasIV_STD/index.htm"
    theurl: str | None = request.args.get("theurl")
    theCMScode: str = ""
    if theurl:
        outputcollector = StringIO()
        with redirect_stdout(outputcollector):
            dance_result_federation_parser.eventurl_to_web(theurl)
        theCMScode: str = outputcollector.getvalue()
    thehtmlpage: str = (
        "<html><head><title>Flask-Test</title></head><body>"
        + '<form action="/" method="get">'
        + '<label for="fname">Veranstaltungs-URL:</label>'
        + '<input type="text" id="theurl" name="theurl">'
        + '<input type="submit" value="Submit">'
        + "</form>"
        + "<p>Copy and paste the contents of the text area into your CMS.</p>"
        + f'<textarea rows="30" cols="130">{theCMScode}</textarea>'
        + "</body></html>"
    )
    return thehtmlpage


if __name__ == "__main__":
    app.run(debug=__debug__)
