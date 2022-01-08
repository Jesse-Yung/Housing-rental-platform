from typing import Any, Union, Optional
from datetime import date, datetime
from urllib.parse import quote, unquote
from re import split


def _escape_null(val: str) -> str:
    if val == 'null':
        return '`null`'
    elif val == 'Null':
        return '`Null`'
    elif val == 'NULL':
        return '`NULL`'
    elif val == 'nil':
        return '`nil`'
    elif val == 'None':
        return '`None`'
    else:
        return val


def _unescape_null(val: str) -> Optional[str]:
    if val == '`null`':
        return 'null'
    elif val == '`Null`':
        return 'Null'
    elif val == '`NULL`':
        return 'NULL'
    elif val == '`nil`':
        return 'nil'
    elif val == '`None`':
        return 'None'
    elif val == 'null':
        return None
    elif val == 'Null':
        return None
    elif val == 'NULL':
        return None
    elif val == 'nil':
        return None
    elif val == 'None':
        return None
    else:
        return val


def _gen_tokens(items: list[str], value: Any) -> list[str]:
    result: list[str] = []
    if value is True:
        return [f'{_gen_key(items)}=true']
    elif value is False:
        return [f'{_gen_key(items)}=false']
    elif value is None:
        return [f'{_gen_key(items)}=null']
    elif isinstance(value, list):
        for i, v in enumerate(value):
            result.extend(_gen_tokens(items + [str(i)], v))
        return result
    elif isinstance(value, dict):
        for k, v in value.items():
            result.extend(_gen_tokens(items + [str(k)], v))
        return result
    elif isinstance(value, datetime):
        return [f'{_gen_key(items)}={quote(value.isoformat(timespec="milliseconds")[:23] + "Z")}']
    elif isinstance(value, date):
        return [f'{_gen_key(items)}={str(value)}']
    elif type(value) is str:
        return [f'{_gen_key(items)}={quote(_escape_null(value))}']
    else:
        return [f'{_gen_key(items)}={quote(str(value))}']


def _gen_key(items: list[str]) -> str:
    return f'{items[0]}[{"][".join(items[1:])}]'.removesuffix('[]')


def _assign_to_result(result: Union[dict[str, Any], list[Any]],
                     items: list[str],
                     value: str) -> None:
    if len(items) == 1:
        if isinstance(result, dict):
            result[items[0]] = _unescape_null(unquote(value))
        else:
            result.append(_unescape_null(unquote(value)))
        return
    if isinstance(result, dict) and items[0] not in result:
        if len(items) > 1 and items[1] == '0':
            result[items[0]] = []
        else:
            result[items[0]] = {}
    if isinstance(result, list) and int(items[0]) >= len(result):
        if len(items) > 1 and items[1] == '0':
            result.append([])
        else:
            result.append({})
    if isinstance(result, dict):
        _assign_to_result(result[items[0]], items[1:], value)
    else:
        _assign_to_result(result[int(items[0])], items[1:], value)
    return


def stringify(obj: dict[str, Any]) -> str:
    tokens: list[str] = []
    for key, value in obj.items():
        tokens.extend(_gen_tokens([key], value))
    return '&'.join(tokens)


def parse(qs: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    if qs == '':
        return result
    tokens = qs.split('&')
    for token in tokens:
        key, value = token.split('=')
        items = split('\]?\[', key.removesuffix(']'))
        _assign_to_result(result, items, value)
    return result
