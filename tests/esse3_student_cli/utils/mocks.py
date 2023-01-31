from pathlib import Path

import pytest
from pytest_localserver.http import WSGIServer

from esse3_student_cli.esse3_wrapper import ESSE3_SERVER, LOGIN_URL, LOGOUT_URL, EXAMS_URL, RESERVATIONS_URL, \
    change_esse3_server, BOOKLET_URL, TAXES_URL

TRACE = False


def read_html(filename):
    file = (Path(__file__).parent / "html/filename").with_name(filename)
    if TRACE:
        if not file.exists():
            print("TRACE(read_html)", f"missing file {file}")
        else:
            print("TRACE(read_html)", f"serving file {file}")
    return open(file).read()


def endpoint(url):
    return url.replace(ESSE3_SERVER, '').replace("https://", "disable://").replace("http://", "disable://")


MOCK_ESSE3_STATE = {
    "add exam cod completed": False,
    "register ae empty": True,
    "theses signed": False,
}


def mock_esse3_app(environ, start_response):
    status = "200 OK"
    response_headers = [('Content-type', 'text/html')]
    method = environ["REQUEST_METHOD"]
    url = environ["REQUEST_URI"]
    if TRACE and url.startswith("/auth/"):
        print('TRACE(mock_esse3_app)', method, url)
    server = f'{environ["wsgi.url_scheme"]}://{environ["HTTP_HOST"]}'
    start_response(status, response_headers)
    html = None
    if method == "GET":
        if url == endpoint(LOGIN_URL):
            html = read_html("login.html")
        elif url == endpoint(LOGOUT_URL):
            html = read_html("logout.html")
        elif url == endpoint(RESERVATIONS_URL):
            html = read_html("reservations.html")
        elif url == endpoint(EXAMS_URL):
            html = read_html("exams.html")
        elif url == endpoint(BOOKLET_URL):
            html = read_html("booklet.html")
        elif url == endpoint(TAXES_URL):
            html = read_html("taxes-1.html")

    if TRACE and url.startswith("/auth/") and html is None:
        print('TRACE(mock_esse3_app)', 'missing page')
    return [html.replace(
        '<base href="https://unical.esse3.cineca.it/">',
        f'<base href="{server}">',
    ).encode()]


@pytest.fixture
def test_server(request):
    server = WSGIServer(application=mock_esse3_app)
    server.start()
    request.addfinalizer(server.stop)
    change_esse3_server(server.url)
    return server
