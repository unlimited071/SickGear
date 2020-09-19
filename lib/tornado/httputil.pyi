import collections
import datetime
import http.cookies
import time
import typing
import unittest
from asyncio import Future
from collections import namedtuple
from tornado_py3.escape import native_str as native_str, parse_qs_bytes as parse_qs_bytes, utf8 as utf8
from tornado_py3.log import gen_log as gen_log
from tornado_py3.util import ObjectDict as ObjectDict, unicode_type as unicode_type
from typing import Any, AnyStr, Awaitable, Dict, Iterable, Iterator, List, Mapping, Optional, Tuple, Union

class _NormalizedHeaderCache(dict):
    size: Any = ...
    queue: Any = ...
    def __init__(self, size: int) -> None: ...
    def __missing__(self, key: str) -> str: ...

class HTTPHeaders(collections.abc.MutableMapping):
    def __init__(self, __arg: Mapping[str, List[str]]) -> None: ...
    def __init__(self, __arg: Mapping[str, str]) -> None: ...
    def __init__(self, *args: Tuple[str, str]) -> None: ...
    def __init__(self, **kwargs: str) -> None: ...
    def __init__(self, *args: typing.Any, **kwargs: str) -> None: ...
    def add(self, name: str, value: str) -> None: ...
    def get_list(self, name: str) -> List[str]: ...
    def get_all(self) -> Iterable[Tuple[str, str]]: ...
    def parse_line(self, line: str) -> None: ...
    @classmethod
    def parse(cls: Any, headers: str) -> HTTPHeaders: ...
    def __setitem__(self, name: str, value: str) -> None: ...
    def __getitem__(self, name: str) -> str: ...
    def __delitem__(self, name: str) -> None: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[typing.Any]: ...
    def copy(self) -> HTTPHeaders: ...
    __copy__: Any = ...
    __unicode__: Any = ...

class HTTPServerRequest:
    path: str = ...
    query: str = ...
    method: Any = ...
    uri: Any = ...
    version: Any = ...
    headers: Any = ...
    body: Any = ...
    remote_ip: Any = ...
    protocol: Any = ...
    host: Any = ...
    host_name: Any = ...
    files: Any = ...
    connection: Any = ...
    server_connection: Any = ...
    arguments: Any = ...
    query_arguments: Any = ...
    body_arguments: Any = ...
    def __init__(self, method: str=..., uri: str=..., version: str=..., headers: HTTPHeaders=..., body: bytes=..., host: str=..., files: Dict[str, List[HTTPFile]]=..., connection: HTTPConnection=..., start_line: RequestStartLine=..., server_connection: object=...) -> None: ...
    @property
    def cookies(self) -> Dict[str, http.cookies.Morsel]: ...
    def full_url(self) -> str: ...
    def request_time(self) -> float: ...
    def get_ssl_certificate(self, binary_form: bool=...) -> Union[None, Dict, bytes]: ...

class HTTPInputError(Exception): ...
class HTTPOutputError(Exception): ...

class HTTPServerConnectionDelegate:
    def start_request(self, server_conn: object, request_conn: HTTPConnection) -> HTTPMessageDelegate: ...
    def on_close(self, server_conn: object) -> None: ...

class HTTPMessageDelegate:
    def headers_received(self, start_line: Union[RequestStartLine, ResponseStartLine], headers: HTTPHeaders) -> Optional[Awaitable[None]]: ...
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]: ...
    def finish(self) -> None: ...
    def on_connection_close(self) -> None: ...

class HTTPConnection:
    def write_headers(self, start_line: Union[RequestStartLine, ResponseStartLine], headers: HTTPHeaders, chunk: bytes=...) -> Future[None]: ...
    def write(self, chunk: bytes) -> Future[None]: ...
    def finish(self) -> None: ...

def url_concat(url: str, args: Union[None, Dict[str, str], List[Tuple[str, str]], Tuple[Tuple[str, str], ...]]) -> str: ...

class HTTPFile(ObjectDict): ...

def parse_body_arguments(content_type: str, body: bytes, arguments: Dict[str, List[bytes]], files: Dict[str, List[HTTPFile]], headers: HTTPHeaders=...) -> None: ...
def parse_multipart_form_data(boundary: bytes, data: bytes, arguments: Dict[str, List[bytes]], files: Dict[str, List[HTTPFile]]) -> None: ...
def format_timestamp(ts: Union[int, float, tuple, time.struct_time, datetime.datetime]) -> str: ...

RequestStartLine = namedtuple('RequestStartLine', ['method', 'path', 'version'])

def parse_request_start_line(line: str) -> RequestStartLine: ...

ResponseStartLine = namedtuple('ResponseStartLine', ['version', 'code', 'reason'])

def parse_response_start_line(line: str) -> ResponseStartLine: ...
def encode_username_password(username: Union[str, bytes], password: Union[str, bytes]) -> bytes: ...
def doctests() -> unittest.TestSuite: ...
def split_host_and_port(netloc: str) -> Tuple[str, Optional[int]]: ...
def qs_to_qsl(qs: Dict[str, List[AnyStr]]) -> Iterable[Tuple[str, AnyStr]]: ...
def parse_cookie(cookie: str) -> Dict[str, str]: ...
