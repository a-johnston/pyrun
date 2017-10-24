#!/usr/bin/env python3.6
import importlib.machinery
import inspect
import json
import sys
import re


_USAGE_ = 'Usage:\n    pyrun FILE METHOD [ARGS]...\n'

_PARAM_PREFIX = ':param '
_TYPE_PREFIX = ':type '

_ARGS = 'POSITIONAL_OR_KEYWORD'
_VARARGS = 'VAR_POSITIONAL'
_KWARGS = 'VAR_KEYWORD'


def _get_val(x):
    try:
        return json.loads(x)
    except json.decoder.JSONDecodeError:
        return x.strip()


def _get_args(param_info, param_kind):
    return [p[0] for p in param_info.values() if p[0].kind.name == param_kind]


def _get_type(param):
    if param.annotation == inspect._empty:
        return None
    return param.annotation.__name__


def _parse_docstring(method):
    docstring = method.__doc__ or ''
    docstring = filter(lambda x: x, map(str.strip, docstring.split('\n')))
    params = list(inspect.signature(method).parameters.values())
    param_info = {
        param.name: [param, None, _get_type(param)] for param in params
    }
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


def _parse_args(args):
    i = 0
    posargs = {}
    varargs = []
    kwargs = {}
    while i < len(args):
        if args[i].startswith('--'):
            name = args[i][2:].strip()
            i += 1
            value = _get_val(args[i])
            posargs[name] = value
        elif '=' in args[i] and re.match('[a-zA-Z][a-zA-Z0-9]*=.*', args[i]):
            name, value = args[i].split('=')
            kwargs[_get_val(name)] = _get_val(value)
        else:
            varargs.append(_get_val(args[i]))
        i += 1
    return posargs, varargs, kwargs


def _print_usage_str(method, param_info, info_str):
    """Test usage str
    """
    usage = 'Usage:\n    ' + method.__name__ + ' '
    for param in _get_args(param_info, _ARGS):
        if param.default != inspect._empty:
            usage += '[--{}] '.format(param.name)
        else:
            usage += '--{} '.format(param.name)
    for vararg in _get_args(param_info, _VARARGS):
        usage += '[{}]... '.format(vararg.name)
    for kwarg in _get_args(param_info, _KWARGS):
        usage += '[name=value]...'
    usage = usage.strip()
    param_str = ''
    if any([x[2] for x in param_info.values()]):
        longest_type = max([len(x[2]) for x in param_info.values() if x[2]])
    for param in param_info:
        param_type = param_info[param][2]
        if param_type == inspect._empty:
            param_type = None
        elif param_type and isinstance(param_type, type):
            param_type = param_type.__name__
        param_desc = param_info[param][1]
        if param_type or param_desc:
            param_str += '\n    ' + param
            if param_type:
                param_str += ' ({})'.format(param_type)
                param_str += ' ' * (longest_type - len(param_type))
            if param_desc:
                param_str += ' : ' + param_desc
    if param_str:
        usage += '\n' + param_str
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
    args, varargs, kwargs = _parse_args(args)  # TODO: validate types
    co_varnames = method.__code__.co_varnames
    named = set([x.name for x in _get_args(param_info, _ARGS)])
    named &= set(co_varnames)
    named_args = [None] * len(named)
    for name in sorted(named, key=lambda name: co_varnames.index(name)):
        default = param_info[name][0].default
        value = args.get(name) or default
        if value == inspect._empty:
            named_args[co_varnames.index(name)] = varargs.pop(0)
        else:
            named_args[co_varnames.index(name)] = value
    print(json.dumps(method(*(named_args + varargs), **kwargs)))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(_USAGE_)
        sys.exit(0)
    loader = importlib.machinery.SourceFileLoader('module', sys.argv[1])
    module = loader.load_module('module')
    method = getattr(module, sys.argv[2])
    args = sys.argv[3:]
    run(method, args)
