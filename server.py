from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from flask import Flask, abort, redirect

from nachrichten import (
    get_heute_video_url_from_page,
    get_latest_heute_page_url_for_date,
    get_latest_tagesschau_page_url_for_date,
    get_tagesschau_video_url_from_page,
)

if TYPE_CHECKING:
    from werkzeug.wrappers import Response


app = Flask(__name__)


@app.route("/tagesschau")
def redirect_tagesschau() -> Response:
    today = datetime.date.today()
    if (tagesschau_url := get_latest_tagesschau_page_url_for_date(today)) :
        if (
            tagesschau_video_url := get_tagesschau_video_url_from_page(tagesschau_url)
        ) :
            return redirect(tagesschau_video_url, code=302)
    abort(503)


@app.route("/heute")
def redirect_heute() -> Response:
    today = datetime.date.today()
    if (heute_url := get_latest_heute_page_url_for_date(today)) :
        if (heute_video_url := get_heute_video_url_from_page(heute_url)) :
            return redirect(heute_video_url, code=302)
    abort(503)
