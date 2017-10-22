#!/usr/bin/env python3.6
import importlib
import inspect
import json
import sys


_USAGE_ = 'Usage: pyrun MODULE METHOD [ARGS]...'

_PARAM_PREFIX = ':param '
_TYPE_PREFIX = ':type '


_ARGS = 'POSITIONAL_OR_KEYWORD'
_VARARGS = 'VAR_POSITIONAL'
_KWARGS = 'VAR_KEYWORD'


def _get_args(param_info, param_kind):
    return [p[0] for p in param_info.values() if p[0].kind.name == param_kind]


def _parse_docstring(method):
    docstring = method.__doc__ or ''
    docstring = filter(lambda x: x, map(str.strip, docstring.split('\n')))
    params = list(inspect.signature(method).parameters.values())
    param_info = {param.name: [param, None, None] for param in params}
    info_strs = []

    for line in docstring:
        if line.startswith(_PARAM_PREFIX):
            name, info = map(str.strip, line[len(_PARAM_PREFIX):].split(':'))
            param_info[name][1] = info
        elif line.startswith(_TYPE_PREFIX):
            name, info = map(str.strip, line[len(_TYPE_PREFIX):].split(':'))
            param_info[name][2] = info
        else:
            info_strs.append(line)
    return param_info, '\n'.join(info_strs).strip()


def _print_usage_str(method, param_info, info_str):
    """Test usage str
    """
    usage = 'Usage:\n\t' + method.__name__ + ' '
    for param in _get_args(param_info, _ARGS):
        if param.default != inspect._empty:
            usage += '[--' + param.name + '] '
        else:
            usage += '--' + param.name + ' '
    for vararg in _get_args(param_info, _VARARGS):
        usage += '[ARGS]... '
    for kwarg in _get_args(param_info, _KWARGS):
        usage += '[name=value]...'
    usage = usage.strip()
    if info_str:
        usage += '\n\n' + info_str
    usage += '\n'
    print(usage)


def run(method, args):
    args = args or []
    param_info, info_str = _parse_docstring(method)
    if '-h' in args or '--help' in args:
        _print_usage_str(method, param_info, info_str)
        sys.exit(0)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(_USAGE_)
        sys.exit(0)
    module = importlib.import_module(sys.argv[1])
    method = getattr(module, sys.argv[2])
    args = sys.argv[3:]
    run(method, args)
