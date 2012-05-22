# -*- coding: utf-8 -*-


# Biryani -- A conversion and validation toolbox
# By: Emmanuel Raviart <eraviart@easter-eggs.com>
#
# Copyright (C) 2009, 2010, 2011 Easter-eggs
# http://packages.python.org/Biryani/
#
# This file is part of Biryani.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Base Conversion Functions

.. note:: Most converters do only one operation and can fail when given wrong data. To ensure that they don't fail, they
   must be combined with other converters.

.. note:: Most converters work on unicode strings. To use them you must first convert your strings to unicode. By using
   converter :func:`decode_str`, for example.
"""


import re

from . import states, strings


__all__ = [
    'bool_to_str',
    'catch_error',
    'check',
    'clean_str_to_bool',
    'clean_str_to_email',
    'clean_str_to_url_path_and_query',
    'cleanup_empty',
    'cleanup_line',
    'cleanup_text',
    'condition',
    'decode_str',
    'default',
    'encode_str',
    'exists',
    'extract_when_singleton',
    'fail',
    'first_match',
    'function',
    'get',
    'guess_bool',
    'item_or_sequence',
    'make_clean_str_to_url',
    'make_item_to_singleton',
    'make_str_to_normal_form',
    'make_str_to_slug',
    'make_str_to_url',
    'new_mapping',
    'new_sequence',
    'new_struct',
    'noop',
    'pipe',
    'python_data_to_bool',
    'python_data_to_float',
    'python_data_to_int',
    'python_data_to_str',
    'rename_item',
    'set_value',
    'str_to_bool',
    'str_to_email',
    'str_to_float',
    'str_to_int',
    'str_to_slug',
    'str_to_url_name',
    'str_to_url_path_and_query',
    'struct',
    'structured_mapping',
    'structured_sequence',
    'switch',
    'test',
    'test_between',
    'test_conv',
    'test_equals',
    'test_exists',
    'test_greater_or_equal',
    'test_in',
    'test_is',
    'test_isinstance',
    'test_less_or_equal',
    'test_missing',
    'test_not_in',
    'translate',
    'uniform_mapping',
    'uniform_sequence',
    ]

domain_re = re.compile(r'''
    (?:[a-z0-9][a-z0-9\-]{0,62}\.)+ # (sub)domain - alpha followed by 62max chars (63 total)
    [a-z]{2,}$                      # TLD
    ''', re.I | re.VERBOSE)
html_id_re = re.compile(r'[A-Za-z][-A-Za-z0-9_:.]+$')
html_name_re = html_id_re
N_ = lambda message: message
username_re = re.compile(r"[^ \t\n\r@<>()]+$", re.I)


# Level-1 Converters


def bool_to_str(value, state = states.default_state):
    """Convert a boolean to a "0" or "1" string.

    .. warning:: Like most converters, a missing value (aka ``None``) is not converted.

        When you want ``None`` to be converted to ``"0"``, use::

            pipe(bool_to_str, default(u'0'))

    >>> bool_to_str(False)
    (u'0', None)
    >>> bool_to_str(True)
    (u'1', None)
    >>> bool_to_str(0)
    (u'0', None)
    >>> bool_to_str('')
    (u'0', None)
    >>> bool_to_str('any non-empty string')
    (u'1', None)
    >>> bool_to_str('0')
    (u'1', None)
    >>> bool_to_str(None)
    (None, None)
    >>> pipe(default(False), bool_to_str)(None)
    (u'0', None)
    """
    if value is None:
        return value, None
    return unicode(int(bool(value))), None


def catch_error(converter, error_value = None):
    """Make a converter that calls another converter and ignore its errors.

    >>> catch_error(noop)(42)
    (42, None)
    >>> catch_error(fail())(42)
    (None, None)
    >>> catch_error(noop, error_value = 0)(42)
    (42, None)
    >>> catch_error(fail(), error_value = 0)(42)
    (0, None)
    """
    def catch_error_converter(value, state = states.default_state):
        result, error = converter(value, state = state)
        if error is not None:
            return error_value, None
        return result, None
    return catch_error_converter


def clean_str_to_bool(value, state = states.default_state):
    """Convert a clean string to a boolean.

    .. note:: For a converter that doesn't require a clean string, see :func:`str_to_bool`.

    .. note:: For a converter that accepts special strings like "f", "off", "no", etc, see :func:`guess_bool`.

    .. warning:: Like most converters, a missing value (aka ``None``) is not converted.

        When you want ``None`` to be converted to ``False``, use::

            pipe(clean_str_to_bool, default(False))

    >>> clean_str_to_bool(u'0')
    (False, None)
    >>> clean_str_to_bool(u'1')
    (True, None)
    >>> clean_str_to_bool(None)
    (None, None)
    >>> clean_str_to_bool(u'vrai')
    (u'vrai', u'Value must be a boolean')
    >>> clean_str_to_bool(u'on')
    (u'on', u'Value must be a boolean')
    """
    if value is None:
        return value, None
    try:
        return bool(int(value)), None
    except ValueError:
        return value, state._(u'Value must be a boolean')


def clean_str_to_email(value, state = states.default_state):
    """Convert a clean string to an email address.

    .. note:: For a converter that doesn't require a clean string, see :func:`str_to_email`.

    >>> clean_str_to_email(u'john@doe.name')
    (u'john@doe.name', None)
    >>> clean_str_to_email(u'mailto:john@doe.name')
    (u'john@doe.name', None)
    >>> clean_str_to_email(u'root@localhost')
    (u'root@localhost', None)
    >>> clean_str_to_email(u'root@127.0.0.1')
    (u'root@127.0.0.1', u'Invalid domain name')
    >>> clean_str_to_email(u'root')
    (u'root', u'An email must contain exactly one "@"')
    """
    if value is None:
        return value, None
    value = value.lower()
    if value.startswith(u'mailto:'):
        value = value.replace(u'mailto:', u'')
    try:
        username, domain = value.split('@', 1)
    except ValueError:
        return value, state._(u'An email must contain exactly one "@"')
    if not username_re.match(username):
        return value, state._(u'Invalid username')
    if not domain_re.match(domain) and domain != 'localhost':
        return value, state._(u'Invalid domain name')
    return value, None


def clean_str_to_url_path_and_query(value, state = states.default_state):
    """Convert a clean string to the path and query of an URL.

    .. note:: For a converter that doesn't require a clean string, see :func:`str_to_url_path_and_query`.

    >>> clean_str_to_url_path_and_query(u'/Biryani/presentation.html#tutorial')
    (u'/Biryani/presentation.html', None)
    >>> clean_str_to_url_path_and_query(u'/Biryani/search.html?q=pipe')
    (u'/Biryani/search.html?q=pipe', None)
    >>> clean_str_to_url_path_and_query(u'http://packages.python.org/Biryani/search.html?q=pipe')
    (u'http://packages.python.org/Biryani/search.html?q=pipe', u'URL must not be complete')
    >>> clean_str_to_url_path_and_query(u'[www.nordnet.fr/grandmix/]')
    (u'[www.nordnet.fr/grandmix/]', None)
    >>> print clean_str_to_url_path_and_query(None)
    (None, None)
    >>> import urlparse
    >>> pipe(
    ...     make_clean_str_to_url(),
    ...     function(lambda value: urlparse.urlunsplit([u'', u''] + list(urlparse.urlsplit(value))[2:])),
    ...     clean_str_to_url_path_and_query,
    ...     )(u'http://packages.python.org/Biryani/search.html?q=pipe')
    (u'/Biryani/search.html?q=pipe', None)
    """
    if value is None:
        return value, None
    import urlparse
    try:
        split_url = list(urlparse.urlsplit(value))
    except ValueError:
        return value, state._(u'Invalid URL')
    if split_url[0] or split_url[1]:
        return value, state._(u'URL must not be complete')
    if split_url[4]:
        split_url[4] = ''
    return unicode(urlparse.urlunsplit(split_url)), None


def cleanup_empty(value, state = states.default_state):
    """When value is comparable to False (ie None, 0 , '', etc) replace it with None else keep it as is.

    >>> cleanup_empty(0)
    (None, None)
    >>> cleanup_empty('')
    (None, None)
    >>> cleanup_empty([])
    (None, None)
    >>> cleanup_empty({})
    (None, None)
    >>> cleanup_empty(u'hello world')
    (u'hello world', None)
    >>> cleanup_empty(u'   hello world   ')
    (u'   hello world   ', None)
    """
    return value if value else None, None


def condition(test_converter, ok_converter, error_converter = None):
    """When *test_converter* succeeds (ie no error), then apply *ok_converter*, otherwise apply *error_converter*.

    .. note:: See also :func:`first_match`.

    >>> detect_unknown_values = condition(
    ...     test_in(['?', 'x']),
    ...     set_value(False),
    ...     set_value(True),
    ...     )
    >>> detect_unknown_values(u'Hello world!')
    (True, None)
    >>> detect_unknown_values(u'?')
    (False, None)
    """
    def condition_converter(value, state = states.default_state):
        test, error = test_converter(value, state = state)
        if error is None:
            return ok_converter(value, state = state)
        elif error_converter is None:
            return value, None
        else:
            return error_converter(value, state = state)
    return condition_converter


def decode_str(encoding = 'utf-8'):
    """Return a string to unicode converter that uses given *encoding*.

    >>> decode_str()('   Hello world!   ')
    (u'   Hello world!   ', None)
    >>> decode_str()(u'   Hello world!   ')
    (u'   Hello world!   ', None)
    >>> decode_str()(42)
    (42, None)
    >>> decode_str()(None)
    (None, None)
    """
    return function(lambda value: value.decode(encoding) if isinstance(value, str) else value)


def default(constant):
    """Return a converter that replace a missing value (aka ``None``) by given one.

    >>> default(42)(None)
    (42, None)
    >>> default(42)(u'1234')
    (u'1234', None)
    >>> pipe(str_to_int, default(42))(u'1234')
    (1234, None)
    >>> pipe(str_to_int, default(42))(u'    ')
    (42, None)
    >>> pipe(str_to_int, default(42))(None)
    (42, None)
    """
    return lambda value, state = states.default_state: (constant, None) if value is None else (value, None)


def encode_str(encoding = 'utf-8'):
    """Return a unicode to string converter that uses given *encoding*.

    >>> encode_str()(u'   Hello world!   ')
    ('   Hello world!   ', None)
    >>> encode_str()('   Hello world!   ')
    ('   Hello world!   ', None)
    >>> encode_str()(42)
    (42, None)
    >>> encode_str()(None)
    (None, None)
    """
    return function(lambda value: value.encode(encoding) if isinstance(value, unicode) else value)


def fail(error = N_(u'An error occured')):
    """Return a converter that always returns an error.

    >>> fail(u'Wrong answer')(42)
    (42, u'Wrong answer')
    >>> fail()(42)
    (42, u'An error occured')
    >>> fail()(None)
    (None, u'An error occured')
    """
    def fail_converter(value, state = states.default_state):
        return value, state._(error)
    return fail_converter


def first_match(*converters):
    """Try each converter successively until one succeeds. When every converter fail, return the result of the last one.

    >>> first_match(test_equals(u'NaN'), str_to_int)(u'NaN')
    (u'NaN', None)
    >>> first_match(test_equals(u'NaN'), str_to_int)(u'42')
    (42, None)
    >>> first_match(test_equals(u'NaN'), str_to_int)(u'abc')
    (u'abc', u'Value must be an integer')
    >>> first_match(test_equals(u'NaN'), str_to_int, set_value(0))(u'Hello world!')
    (0, None)
    >>> first_match()(u'Hello world!')
    (u'Hello world!', None)
    """
    def first_match_converter(value, state = states.default_state):
        converted_value = value
        error = None
        for converter in converters:
            converted_value, error = converter(value, state = state)
            if error is None:
                return converted_value, error
        return converted_value, error
    return first_match_converter


def function(function, handle_missing_value = False, handle_state = False):
    """Return a converter that applies a function to value and returns a new value.

    .. note:: Like most converters, by default a missing value (aka ``None``) is not converted (ie function is not
       called). Set ``handle_missing_value`` to ``True`` to call function when value is ``None``.

    .. note:: When your function doesn't modify value but may generate an error, use a :func:`test` instead.

    .. note:: When your function modifies value and may generate an error, write a full converter instead of a function.

    See :doc:`how-to-create-converter` for more informations.

    >>> function(int)('42')
    (42, None)
    >>> function(sorted)([3, 2, 1])
    ([1, 2, 3], None)
    >>> function(lambda value: value + 1)(42)
    (43, None)
    >>> function(lambda value: value + 1)(None)
    (None, None)
    >>> function(lambda value: value + 1)(u'hello world')
    Traceback (most recent call last):
    TypeError:
    >>> function(lambda value: value + 1, handle_missing_value = True)(None)
    Traceback (most recent call last):
    TypeError:
    """
    def function_converter(value, state = states.default_state):
        if value is None and not handle_missing_value or function is None:
            return value, None
        if handle_state:
            return function(value, state = state), None
        return function(value), None
    return function_converter


def get(key, default = UnboundLocalError, error = None):
    """Return a converter that returns an item of a collection.

    Collection can either be a mapping (ie dict, etc) or a sequence (ie list, tuple, string, etc).

    Usage with a mapping:

    >>> get('a')(dict(a = 1, b = 2))
    (1, None)
    >>> get('c')(dict(a = 1, b = 2))
    (None, u'Unknown key: c')
    >>> get('c', default = None)(dict(a = 1, b = 2))
    (None, None)
    >>> get('c', error = u'Key Error')(dict(a = 1, b = 2))
    (None, u'Key Error')
    >>> get(u'a')(None)
    (None, None)

    Usage with a sequence:
    >>> get(0)(u'ab')
    (u'a', None)
    >>> get(-2)([u'a', u'b'])
    (u'a', None)
    >>> get(-3)(u'ab')
    (None, u'Index out of range: -3')
    >>> get(2, error = u"Index Error')([u'a', u'b'])
    (None, u"Index Error')
    >>> get(-3, default = None)(u'ab')
    (None, None)
    >>> get(0)(None)
    (None, None)
    """
    def get_converter(value, state = states.default_state):
        import collections

        if value is None:
            return value, None
        if isinstance(value, collections.Mapping):
            converted_value = value.get(key, default)
            if converted_value is UnboundLocalError:
                return None, state._(u'Unknown key: {0}').format(key) if error is None else state._(error)
            return converted_value, None
        assert isinstance(value, collections.Sequence), \
            'Value must be a mapping or a sequence. Got {0} instead.'.format(type(value))
        if 0 <= key < len(value):
            return value[key], None
        if default is UnboundLocalError:
            return None, state._(u'Index out of range: {0}').format(key) if error is None else state._(error)
        return default, None
    return get_converter


def guess_bool(value, state = states.default_state):
    """Convert the content of a string (or a number) to a boolean. Do nothing when input value is already a boolean.

    This converter accepts usual values for ``True`` and ``False``: "0", "f", "false", "n", etc.

    .. warning:: Like most converters, a missing value (aka ``None``) is not converted.

        When you want ``None`` to be converted to ``False``, use::

            pipe(guess_bool, default(False))

    >>> guess_bool(u'0')
    (False, None)
    >>> guess_bool(u'f')
    (False, None)
    >>> guess_bool(u'FALSE')
    (False, None)
    >>> guess_bool(u'false')
    (False, None)
    >>> guess_bool(u'n')
    (False, None)
    >>> guess_bool(u'no')
    (False, None)
    >>> guess_bool(u'off')
    (False, None)
    >>> guess_bool(u'  0  ')
    (False, None)
    >>> guess_bool(u'  f  ')
    (False, None)
    >>> guess_bool(False)
    (False, None)
    >>> guess_bool(0)
    (False, None)
    >>> guess_bool(u'1')
    (True, None)
    >>> guess_bool(u'on')
    (True, None)
    >>> guess_bool(u't')
    (True, None)
    >>> guess_bool(u'TRUE')
    (True, None)
    >>> guess_bool(u'true')
    (True, None)
    >>> guess_bool(u'y')
    (True, None)
    >>> guess_bool(u'yes')
    (True, None)
    >>> guess_bool(u'  1  ')
    (True, None)
    >>> guess_bool(u'  tRuE  ')
    (True, None)
    >>> guess_bool(True)
    (True, None)
    >>> guess_bool(1)
    (True, None)
    >>> guess_bool(2)
    (True, None)
    >>> guess_bool(-1)
    (True, None)
    >>> guess_bool(u'')
    (None, None)
    >>> guess_bool(u'   ')
    (None, None)
    >>> guess_bool(None)
    (None, None)
    >>> guess_bool(u'vrai')
    (u'vrai', u'Value must be a boolean')
    """
    if value is None:
        return value, None
    try:
        return bool(int(value)), None
    except ValueError:
        lower_value = value.strip().lower()
        if not lower_value:
            return None, None
        if lower_value in (u'f', u'false', u'n', u'no', u'off'):
            return False, None
        if lower_value in (u'on', u't', u'true', u'y', u'yes'):
            return True, None
        return value, state._(u'Value must be a boolean')


def item_or_sequence(converter, constructor = list, keep_missing_items = False):
    """Return a converter that accepts either an item or a sequence of items and applies a converter to them.

    >>> item_or_sequence(str_to_int)(u'42')
    (42, None)
    >>> item_or_sequence(str_to_int)([u'42'])
    (42, None)
    >>> item_or_sequence(str_to_int)([u'42', u'43'])
    ([42, 43], None)
    >>> item_or_sequence(str_to_int)([u'42', u'43', u'Hello world!'])
    ([42, 43, u'Hello world!'], {2: u'Value must be an integer'})
    >>> item_or_sequence(str_to_int)([u'42', None, u'43'])
    ([42, 43], None)
    >>> item_or_sequence(str_to_int)([None, None])
    (None, None)
    >>> item_or_sequence(str_to_int, keep_missing_items = True)([None, None])
    ([None, None], None)
    >>> item_or_sequence(str_to_int, keep_missing_items = True)([u'42', None, u'43'])
    ([42, None, 43], None)
    >>> item_or_sequence(str_to_int, keep_missing_items = True)([u'42', u'43', u'Hello world!'])
    ([42, 43, u'Hello world!'], {2: u'Value must be an integer'})
    >>> item_or_sequence(str_to_int, constructor = set)(set([u'42', u'43']))
    (set([42, 43]), None)
    """
    return condition(
        test_isinstance(constructor),
        pipe(
            uniform_sequence(converter, constructor = constructor, keep_missing_items = keep_missing_items),
            extract_when_singleton,
            ),
        converter,
        )


def make_clean_str_to_url(add_prefix = u'http://', error_if_fragment = False, error_if_path = False,
        error_if_query = False, full = False, remove_fragment = False, remove_path = False, remove_query = False,
        schemes = (u'http', u'https')):
    """Return a converter that converts a clean string to an URL.

    .. note:: For a converter that doesn't require a clean string, see :func:`make_str_to_url`.

    >>> make_clean_str_to_url()(u'http://packages.python.org/Biryani/')
    (u'http://packages.python.org/Biryani/', None)
    >>> make_clean_str_to_url(full = True)(u'packages.python.org/Biryani/')
    (u'http://packages.python.org/Biryani/', None)
    >>> make_clean_str_to_url()(u'/Biryani/presentation.html#tutorial')
    (u'/Biryani/presentation.html#tutorial', None)
    >>> make_clean_str_to_url(full = True)(u'/Biryani/presentation.html#tutorial')
    (u'/Biryani/presentation.html#tutorial', u'URL must be complete')
    >>> make_clean_str_to_url(remove_path = True)(u'http://packages.python.org/Biryani/presentation.html')
    (u'http://packages.python.org/', None)
    >>> make_clean_str_to_url(error_if_path = True)(u'http://packages.python.org/Biryani/presentation.html')
    (u'http://packages.python.org/Biryani/presentation.html', u'URL must not contain a path')
    >>> make_clean_str_to_url(remove_query = True)(u'http://packages.python.org/Biryani/presentation.html?tuto=1')
    (u'http://packages.python.org/Biryani/presentation.html', None)
    >>> make_clean_str_to_url(error_if_query = True)(u'http://packages.python.org/Biryani/presentation.html?tuto=1')
    (u'http://packages.python.org/Biryani/presentation.html?tuto=1', u'URL must not contain a query')
    >>> make_clean_str_to_url(remove_fragment = True)(u'http://packages.python.org/Biryani/presentation.html#tutorial')
    (u'http://packages.python.org/Biryani/presentation.html', None)
    >>> make_clean_str_to_url(error_if_fragment = True)(u'http://packages.python.org/Biryani/presentation.html#tuto')
    (u'http://packages.python.org/Biryani/presentation.html#tuto', u'URL must not contain a fragment')
    >>> make_clean_str_to_url(full = True)(u'[www.nordnet.fr/grandmix/]')
    (u'[www.nordnet.fr/grandmix/]', u'Invalid URL')
    >>> make_clean_str_to_url(full = True)(u'http://[www.nordnet.fr/grandmix/]')
    (u'http://[www.nordnet.fr/grandmix/]', u'Invalid URL')
    """
    def clean_str_to_url(value, state = states.default_state):
        if value is None:
            return value, None
        import urlparse
        try:
            split_url = list(urlparse.urlsplit(value))
        except ValueError:
            return value, state._(u'Invalid URL')
        if full and add_prefix and not split_url[0] and not split_url[1] and split_url[2] \
                and not split_url[2].startswith(u'/'):
            try:
                split_url = list(urlparse.urlsplit(add_prefix + value))
            except ValueError:
                return value, state._(u'Invalid URL')
        scheme = split_url[0]
        if scheme != scheme.lower():
            split_url[0] = scheme = scheme.lower()
        if full and not scheme:
            return value, state._(u'URL must be complete')
        if scheme and schemes is not None and scheme not in schemes:
            return value, state._(u'Scheme must belong to {0}').format(sorted(schemes))
        network_location = split_url[1]
        if network_location != network_location.lower():
            split_url[1] = network_location = network_location.lower()
        if split_url[2] and split_url[2] != u'/':
            if error_if_path:
                return value, state._(u'URL must not contain a path')
            if remove_path:
                split_url[2] = u'/'
        if scheme in (u'http', u'https') and not split_url[2]:
            # By convention a full HTTP URL must always have at least a "/" in its path.
            split_url[2] = u'/'
        if split_url[3]:
            if error_if_query:
                return value, state._(u'URL must not contain a query')
            if remove_query:
                split_url[3] = u''
        if split_url[4]:
            if error_if_fragment:
                return value, state._(u'URL must not contain a fragment')
            if remove_fragment:
                split_url[4] = u''
        return unicode(urlparse.urlunsplit(split_url)), None
    return clean_str_to_url


def make_item_to_singleton(constructor = list):
    """Convert an item to a singleton, but keep a sequence of items unchanged.

    >>> make_item_to_singleton()(u'Hello world!')
    ([u'Hello world!'], None)
    >>> make_item_to_singleton()([u'Hello world!'])
    ([u'Hello world!'], None)
    >>> make_item_to_singleton()([42, u'Hello world!'])
    ([42, u'Hello world!'], None)
    >>> make_item_to_singleton()([])
    ([], None)
    >>> make_item_to_singleton()(None)
    (None, None)
    >>> make_item_to_singleton(constructor = set)(u'Hello world!')
    (set([u'Hello world!']), None)
    >>> make_item_to_singleton(constructor = set)(set([u'Hello world!']))
    (set([u'Hello world!']), None)
    >>> make_item_to_singleton(constructor = set)(set([42, u'Hello world!']))
    (set([u'Hello world!', 42]), None)
    >>> make_item_to_singleton(constructor = set)([42, u'Hello world!'])
    Traceback (most recent call last):
    TypeError:
    >>> make_item_to_singleton(constructor = set)(set())
    (set([]), None)
    >>> make_item_to_singleton(constructor = set)(None)
    (None, None)
    """
    return condition(
        test_isinstance(constructor),
        noop,
        new_struct([noop], constructor = constructor),
        )


def make_str_to_normal_form(encoding = 'utf-8', separator = u' ', transform = strings.lower):
    """Return a convert that simplifies a string to normal form using compatibility decomposition and removing combining
    characters.

    .. note:: For a converter that is dedicated to a name in an URL path, see :func:`str_to_url_name`.

    .. note:: For a converter that keep only letters, digits and separator, see :func:`make_str_to_slug`
        or :func:`str_to_slug`.

    >>> make_str_to_normal_form()(u'Hello world!')
    (u'hello world!', None)
    >>> make_str_to_normal_form()('Hello world!')
    (u'hello world!', None)
    >>> make_str_to_normal_form()(u'   Hello world!   ')
    (u'hello world!', None)
    >>> make_str_to_normal_form(encoding = u'iso-8859-1')(u'Hello world!')
    (u'hello world!', None)
    >>> make_str_to_normal_form(separator = u'_')(u'Hello world!')
    (u'hello_world!', None)
    >>> from biryani import strings
    >>> make_str_to_normal_form(separator = u' ', transform = strings.upper)(u'Hello world!')
    (u'HELLO WORLD!', None)
    >>> make_str_to_normal_form()(u'')
    (None, None)
    >>> make_str_to_normal_form()(u'   ')
    (None, None)
    """
    def str_to_normal_form(value, state = states.default_state):
        if value is None:
            return value, None
        value = strings.normalize(value, encoding = encoding, separator = separator, transform = transform)
        return value or None, None
    return str_to_normal_form


def make_str_to_slug(encoding = 'utf-8', separator = u'-', transform = strings.lower):
    """Return a convert that simplifies a string to a slug.

    .. note:: For a converter that uses default parameters, see :func:`str_to_slug`.

    >>> make_str_to_slug()(u'Hello world!')
    (u'hello-world', None)
    >>> make_str_to_slug()('Hello world!')
    (u'hello-world', None)
    >>> make_str_to_slug()(u'   Hello world!   ')
    (u'hello-world', None)
    >>> make_str_to_slug(encoding = u'iso-8859-1')(u'Hello world!')
    (u'hello-world', None)
    >>> make_str_to_slug(separator = u' ')(u'Hello world!')
    (u'hello world', None)
    >>> from biryani import strings
    >>> make_str_to_slug(separator = u' ', transform = strings.upper)(u'Hello world!')
    (u'HELLO WORLD', None)
    >>> make_str_to_slug()(u'')
    (None, None)
    >>> make_str_to_slug()(u'   ')
    (None, None)
    """
    def str_to_slug(value, state = states.default_state):
        if value is None:
            return value, None
        value = strings.slugify(value, encoding = encoding, separator = separator, transform = transform)
        return unicode(value) if value else None, None
    return str_to_slug


def make_str_to_url(add_prefix = u'http://', error_if_fragment = False, error_if_path = False,
        error_if_query = False, full = False, remove_fragment = False, remove_path = False, remove_query = False,
        schemes = (u'http', u'https')):
    """Return a converter that converts an string to an URL.

    >>> make_str_to_url()(u'http://packages.python.org/Biryani/')
    (u'http://packages.python.org/Biryani/', None)
    >>> make_str_to_url(full = True)(u'packages.python.org/Biryani/')
    (u'http://packages.python.org/Biryani/', None)
    >>> make_str_to_url()(u'/Biryani/presentation.html#tutorial')
    (u'/Biryani/presentation.html#tutorial', None)
    >>> make_str_to_url(full = True)(u'/Biryani/presentation.html#tutorial')
    (u'/Biryani/presentation.html#tutorial', u'URL must be complete')
    >>> make_str_to_url(remove_path = True)(u'http://packages.python.org/Biryani/presentation.html')
    (u'http://packages.python.org/', None)
    >>> make_str_to_url(error_if_path = True)(u'http://packages.python.org/Biryani/presentation.html')
    (u'http://packages.python.org/Biryani/presentation.html', u'URL must not contain a path')
    >>> make_str_to_url(remove_query = True)(u'http://packages.python.org/Biryani/presentation.html?tuto=1')
    (u'http://packages.python.org/Biryani/presentation.html', None)
    >>> make_str_to_url(error_if_query = True)(u'http://packages.python.org/Biryani/presentation.html?tuto=1')
    (u'http://packages.python.org/Biryani/presentation.html?tuto=1', u'URL must not contain a query')
    >>> make_str_to_url(remove_fragment = True)(u'http://packages.python.org/Biryani/presentation.html#tutorial')
    (u'http://packages.python.org/Biryani/presentation.html', None)
    >>> make_str_to_url(error_if_fragment = True)(u'http://packages.python.org/Biryani/presentation.html#tutorial')
    (u'http://packages.python.org/Biryani/presentation.html#tutorial', u'URL must not contain a fragment')
    >>> make_str_to_url()(u'    http://packages.python.org/Biryani/   ')
    (u'http://packages.python.org/Biryani/', None)
    """
    return pipe(
        cleanup_line,
        make_clean_str_to_url(add_prefix = add_prefix, error_if_fragment = error_if_fragment,
            error_if_path = error_if_path, error_if_query = error_if_query, full = full,
            remove_fragment = remove_fragment, remove_path = remove_path, remove_query = remove_query,
            schemes = schemes),
        )


def new_mapping(converters, constructor = None, keep_empty = False):
    """Return a converter that constructs a mapping (ie dict, etc) from any kind of value.

    .. note:: This converter should not be used directly. Use :func:`new_struct` instead.

    .. note:: When input value has the same structure, converter :func:`struct` should be used instead.

    >>> def convert_list_to_dict(constructor = None, keep_empty = False):
    ...     return new_mapping(
    ...         dict(
    ...             name = get(0),
    ...             age = pipe(get(1), str_to_int),
    ...             email = pipe(get(2), str_to_email),
    ...             ),
    ...         constructor = constructor,
    ...         keep_empty = keep_empty,
    ...         )
    >>> convert_list_to_dict()([u'John Doe', u'72', u'john@doe.name'])
    ({'age': 72, 'email': u'john@doe.name', 'name': u'John Doe'}, None)
    >>> convert_list_to_dict()([u'John Doe', u'72'])
    ({'age': 72, 'name': u'John Doe'}, {'email': u'Index out of range: 2'})
    >>> convert_list_to_dict()([u'John Doe', u'72', None])
    ({'age': 72, 'name': u'John Doe'}, None)
    >>> convert_list_to_dict()([None, u' ', None])
    (None, None)
    >>> convert_list_to_dict(keep_empty = True)([None, u' ', None])
    ({}, None)
    >>> convert_list_to_dict()(None)
    (None, None)
    >>> import collections
    >>> new_mapping(
    ...     dict(
    ...         name = get(0),
    ...         age = pipe(get(1), str_to_int),
    ...         email = pipe(get(2), str_to_email),
    ...         ),
    ...     constructor = collections.OrderedDict,
    ...     )([u'John Doe', u'72', u'john@doe.name'])
    (OrderedDict([('age', 72), ('email', u'john@doe.name'), ('name', u'John Doe')]), None)
    >>> new_mapping(
    ...     collections.OrderedDict(
    ...         name = get(0),
    ...         age = pipe(get(1), str_to_int),
    ...         email = pipe(get(2), str_to_email),
    ...         ),
    ...     )([u'John Doe', u'72', u'john@doe.name'])
    (OrderedDict([('age', 72), ('email', u'john@doe.name'), ('name', u'John Doe')]), None)
    """
    if constructor is None:
        constructor = type(converters)
    converters = dict(
        (name, converter)
        for name, converter in (converters or {}).iteritems()
        if converter is not None
        )

    def new_mapping_converter(value, state = states.default_state):
        if value is None:
            return value, None
        errors = {}
        converted_values = {}
        for name, converter in converters.iteritems():
            converted_value, error = converter(value, state = state)
            if converted_value is not None:
                converted_values[name] = converted_value
            if error is not None:
                errors[name] = error
        if keep_empty or converted_values:
            converted_values = constructor(converted_values)
        else:
            converted_values = None
        return converted_values, errors or None
    return new_mapping_converter


def new_sequence(converters, constructor = None, keep_empty = False):
    """Return a converter that constructs a sequence (ie list, tuple, etc) from any kind of value.

    .. note:: This converter should not be used directly. Use :func:`new_struct` instead.

    .. note:: When input value has the same structure, converter :func:`struct` should be used instead.

    >>> def convert_dict_to_list(constructor = None, keep_empty = False):
    ...     return new_sequence(
    ...         [
    ...             get('name', default = None),
    ...             pipe(get('age', default = None), str_to_int),
    ...             pipe(get('email', default = None), str_to_email),
    ...             ],
    ...         constructor = constructor,
    ...         keep_empty = keep_empty,
    ...         )
    >>> convert_dict_to_list()({'age': u'72', 'email': u'john@doe.name', 'name': u'John Doe'})
    ([u'John Doe', 72, u'john@doe.name'], None)
    >>> convert_dict_to_list(constructor = tuple)({'age': u'72', 'email': u'john@doe.name', 'name': u'John Doe'})
    ((u'John Doe', 72, u'john@doe.name'), None)
    >>> convert_dict_to_list()({'email': u'john@doe.name', 'name': u'John Doe'})
    ([u'John Doe', None, u'john@doe.name'], None)
    >>> convert_dict_to_list()({})
    (None, None)
    >>> convert_dict_to_list(keep_empty = True)({})
    ([None, None, None], None)
    >>> convert_dict_to_list()(None)
    (None, None)
    >>> import collections
    >>> new_sequence(
    ...     [
    ...         get('name', default = None),
    ...         pipe(get('age', default = None), str_to_int),
    ...         pipe(get('email', default = None), str_to_email),
    ...         ],
    ...     constructor = tuple,
    ...     )({'age': u'72', 'email': u'john@doe.name', 'name': u'John Doe'})
    ((u'John Doe', 72, u'john@doe.name'), None)
    >>> new_sequence(
    ...     (
    ...         get('name', default = None),
    ...         pipe(get('age', default = None), str_to_int),
    ...         pipe(get('email', default = None), str_to_email),
    ...         ),
    ...     )({'age': u'72', 'email': u'john@doe.name', 'name': u'John Doe'})
    ((u'John Doe', 72, u'john@doe.name'), None)
    """
    if constructor is None:
        constructor = type(converters)
    converters = [
        converter
        for converter in converters or []
        if converter is not None
        ]

    def new_sequence_converter(value, state = states.default_state):
        if value is None:
            return value, None
        errors = {}
        converted_values = []
        is_empty = True
        for i, converter in enumerate(converters):
            converted_value, error = converter(value, state = state)
            if converted_value is not None:
                is_empty = False
            converted_values.append(converted_value)
            if error is not None:
                errors[i] = error
        converted_values = constructor(converted_values) if not is_empty or keep_empty else None
        return converted_values, errors or None
    return new_sequence_converter


def new_struct(converters, constructor = None, keep_empty = False):
    """Return a converter that constructs a collection (ie dict, list, set, etc) from any kind of value.

    .. note:: When input value has the same structure, converter :func:`struct` should be used instead.

    Usage to create a mapping (ie dict, etc):

    >>> def convert_list_to_dict(constructor = None, keep_empty = False):
    ...     return new_struct(
    ...         dict(
    ...             name = get(0),
    ...             age = pipe(get(1), str_to_int),
    ...             email = pipe(get(2), str_to_email),
    ...             ),
    ...         constructor = constructor,
    ...         keep_empty = keep_empty,
    ...         )
    >>> convert_list_to_dict()([u'John Doe', u'72', u'john@doe.name'])
    ({'age': 72, 'email': u'john@doe.name', 'name': u'John Doe'}, None)
    >>> convert_list_to_dict()([u'John Doe', u'72'])
    ({'age': 72, 'name': u'John Doe'}, {'email': u'Index out of range: 2'})
    >>> convert_list_to_dict()([u'John Doe', u'72', None])
    ({'age': 72, 'name': u'John Doe'}, None)
    >>> convert_list_to_dict()([None, u' ', None])
    (None, None)
    >>> convert_list_to_dict(keep_empty = True)([None, u' ', None])
    ({}, None)
    >>> convert_list_to_dict()(None)
    (None, None)
    >>> import collections
    >>> new_struct(
    ...     dict(
    ...         name = get(0),
    ...         age = pipe(get(1), str_to_int),
    ...         email = pipe(get(2), str_to_email),
    ...         ),
    ...     constructor = collections.OrderedDict,
    ...     )([u'John Doe', u'72', u'john@doe.name'])
    (OrderedDict([('age', 72), ('email', u'john@doe.name'), ('name', u'John Doe')]), None)
    >>> new_struct(
    ...     collections.OrderedDict(
    ...         name = get(0),
    ...         age = pipe(get(1), str_to_int),
    ...         email = pipe(get(2), str_to_email),
    ...         ),
    ...     )([u'John Doe', u'72', u'john@doe.name'])
    (OrderedDict([('age', 72), ('email', u'john@doe.name'), ('name', u'John Doe')]), None)

    Usage to create a sequence (ie list, tuple, etc) or a set:

    >>> def convert_dict_to_list(constructor = None, keep_empty = False):
    ...     return new_struct(
    ...         [
    ...             get('name', default = None),
    ...             pipe(get('age', default = None), str_to_int),
    ...             pipe(get('email', default = None), str_to_email),
    ...             ],
    ...         constructor = constructor,
    ...         keep_empty = keep_empty,
    ...         )
    >>> convert_dict_to_list()({'age': u'72', 'email': u'john@doe.name', 'name': u'John Doe'})
    ([u'John Doe', 72, u'john@doe.name'], None)
    >>> convert_dict_to_list(constructor = tuple)({'age': u'72', 'email': u'john@doe.name', 'name': u'John Doe'})
    ((u'John Doe', 72, u'john@doe.name'), None)
    >>> convert_dict_to_list()({'email': u'john@doe.name', 'name': u'John Doe'})
    ([u'John Doe', None, u'john@doe.name'], None)
    >>> convert_dict_to_list()({})
    (None, None)
    >>> convert_dict_to_list(keep_empty = True)({})
    ([None, None, None], None)
    >>> convert_dict_to_list()(None)
    (None, None)
    >>> import collections
    >>> new_struct(
    ...     [
    ...         get('name', default = None),
    ...         pipe(get('age', default = None), str_to_int),
    ...         pipe(get('email', default = None), str_to_email),
    ...         ],
    ...     constructor = tuple,
    ...     )({'age': u'72', 'email': u'john@doe.name', 'name': u'John Doe'})
    ((u'John Doe', 72, u'john@doe.name'), None)
    >>> new_struct(
    ...     (
    ...         get('name', default = None),
    ...         pipe(get('age', default = None), str_to_int),
    ...         pipe(get('email', default = None), str_to_email),
    ...         ),
    ...     )({'age': u'72', 'email': u'john@doe.name', 'name': u'John Doe'})
    ((u'John Doe', 72, u'john@doe.name'), None)
    """
    import collections

    if isinstance(converters, collections.Mapping):
        return new_mapping(converters, constructor = constructor, keep_empty = keep_empty)
    assert isinstance(converters, collections.Sequence), \
        'Converters must be a mapping or a sequence. Got {0} instead.'.format(type(converters))
    return new_sequence(converters, constructor = constructor, keep_empty = keep_empty)


def noop(value, state = states.default_state):
    """Return value as is.

    >>> noop(42)
    (42, None)
    >>> noop(None)
    (None, None)
    """
    return value, None


def pipe(*converters):
    """Return a compound converter that applies each of its converters till the end or an error occurs.

    >>> str_to_bool(42)
    Traceback (most recent call last):
    AttributeError:
    >>> pipe(str_to_bool)(42)
    Traceback (most recent call last):
    AttributeError:
    >>> pipe(test_isinstance(unicode), str_to_bool)(42)
    (42, u"Value is not an instance of <type 'unicode'>")
    >>> pipe(python_data_to_str, test_isinstance(unicode), str_to_bool)(42)
    (True, None)
    >>> pipe()(42)
    (42, None)
    """
    def pipe_converter(*args, **kwargs):
        if not converters:
            return noop(*args, **kwargs)
        state = kwargs.get('state', UnboundLocalError)
        for converter in converters:
            if converter is None:
                continue
            value, error = converter(*args, **kwargs)
            if error is not None:
                return value, error
            args = [value]
            kwargs = {}
            if state != UnboundLocalError:
                kwargs['state'] = state
        return value, None
    return pipe_converter


def python_data_to_float(value, state = states.default_state):
    """Convert any python data to a float.

    .. warning:: Like most converters, a missing value (aka ``None``) is not converted.

    >>> python_data_to_float(42)
    (42.0, None)
    >>> python_data_to_float('42')
    (42.0, None)
    >>> python_data_to_float(u'42')
    (42.0, None)
    >>> python_data_to_float(42.75)
    (42.75, None)
    >>> python_data_to_float(None)
    (None, None)
    """
    if value is None:
        return value, None
    try:
        return float(value), None
    except ValueError:
        return value, state._(u'Value must be a float')


def python_data_to_int(value, state = states.default_state):
    """Convert any python data to an integer.

    .. warning:: Like most converters, a missing value (aka ``None``) is not converted.

    >>> python_data_to_int(42)
    (42, None)
    >>> python_data_to_int('42')
    (42, None)
    >>> python_data_to_int(u'42')
    (42, None)
    >>> python_data_to_int(42.75)
    (42, None)
    >>> python_data_to_int(None)
    (None, None)
    """
    if value is None:
        return value, None
    try:
        return int(value), None
    except ValueError:
        return value, state._(u'Value must be an integer')


def python_data_to_str(value, state = states.default_state):
    """Convert any Python data to unicode.

    .. warning:: Like most converters, a missing value (aka ``None``) is not converted.

    >>> python_data_to_str(42)
    (u'42', None)
    >>> python_data_to_str('42')
    (u'42', None)
    >>> python_data_to_str(None)
    (None, None)
    """
    if value is None:
        return value, None
    if isinstance(value, str):
        return value.decode('utf-8'), None
    try:
        return unicode(value), None
    except UnicodeDecodeError:
        return str(value).decode('utf-8'), None


def rename_item(old_key, new_key):
    """Return a converter that renames a key in a mapping.

    >>> rename_item('a', 'c')(dict(a = 1, b = 2))
    ({'c': 1, 'b': 2}, None)
    >>> rename_item('c', 'd')(dict(a = 1, b = 2))
    ({'a': 1, 'b': 2}, None)
    >>> rename_item('c', 'd')(None)
    (None, None)
    """
    def rename_item_converter(value, state = states.default_state):
        if value is None:
            return value, None
        if old_key in value:
            value = value.copy()  # Don't modify existing mapping.
            value[new_key] = value.pop(old_key)
        return value, None
    return rename_item_converter


def set_value(constant, set_missing_value = False):
    """Return a converter that replaces any value by given one.

    >>> set_value(42)(u'Answer to the Ultimate Question of Life, the Universe, and Everything')
    (42, None)
    >>> set_value(42)(None)
    (None, None)
    >>> set_value(42, set_missing_value = True)(None)
    (42, None)
    """
    return lambda value, state = states.default_state: (constant, None) \
        if value is not None or set_missing_value \
        else (None, None)


def str_to_url_name(value, state = states.default_state):
    """Convert a string to a normalized string that can be used in an URL path or a query parameter.

    .. note:: For a converter that keep only letters, digits and separator, see :func:`make_str_to_slug`
        or :func:`str_to_slug`.

    >>> str_to_url_name(u'   Hello world!   ')
    (u'hello_world!', None)
    >>> str_to_url_name(u'   ')
    (None, None)
    >>> str_to_url_name(u'')
    (None, None)
    """
    if value is None:
        return value, None
    for character in u'\n\r/?&#':
        value = value.replace(character, u' ')
    value = strings.normalize(value, separator = u'_')
    return value or None, None


def struct(converters, constructor = None, default = None, keep_empty = False, keep_missing_values = False,
        skip_missing_items = False):
    """Return a converter that maps a collection of converters to a collection (ie dict, list, set, etc) of values.

    Usage to convert a mapping (ie dict, etc):

    >>> strict_converter = struct(dict(
    ...     name = pipe(cleanup_line, exists),
    ...     age = str_to_int,
    ...     email = str_to_email,
    ...     ))
    ...
    >>> strict_converter(dict(name = u'John Doe', age = u'72', email = u'john@doe.name'))
    ({'age': 72, 'email': u'john@doe.name', 'name': u'John Doe'}, None)
    >>> strict_converter(dict(name = u'John Doe', email = u'john@doe.name'))
    ({'email': u'john@doe.name', 'name': u'John Doe'}, None)
    >>> strict_converter(dict(name = u'John Doe', age = None, email = u'john@doe.name'))
    ({'email': u'john@doe.name', 'name': u'John Doe'}, None)
    >>> strict_converter(dict(name = u'John Doe', age = u'72', phone = u'   +33 9 12 34 56 78   '))
    ({'phone': u'   +33 9 12 34 56 78   ', 'age': 72, 'name': u'John Doe'}, {'phone': u'Unexpected item'})
    >>> non_strict_converter = struct(
    ...     dict(
    ...         name = pipe(cleanup_line, exists),
    ...         age = str_to_int,
    ...         email = str_to_email,
    ...         ),
    ...     default = cleanup_line,
    ...     )
    ...
    >>> non_strict_converter(dict(name = u'John Doe', age = u'72', email = u'john@doe.name'))
    ({'age': 72, 'email': u'john@doe.name', 'name': u'John Doe'}, None)
    >>> non_strict_converter(dict(name = u'John Doe', email = u'john@doe.name'))
    ({'email': u'john@doe.name', 'name': u'John Doe'}, None)
    >>> non_strict_converter(dict(name = u'John Doe', age = u'72', email = u'john@doe.name',
    ...     phone = u'   +33 9 12 34 56 78   '))
    ({'phone': u'+33 9 12 34 56 78', 'age': 72, 'email': u'john@doe.name', 'name': u'John Doe'}, None)
    >>> struct(
    ...     dict(
    ...         name = cleanup_line,
    ...         age = str_to_int,
    ...         email = str_to_email,
    ...         ),
    ...     default = cleanup_line,
    ...     )(dict(name = u'   ', email = None))
    (None, None)
    >>> struct(
    ...     dict(
    ...         name = cleanup_line,
    ...         age = str_to_int,
    ...         email = str_to_email,
    ...         ),
    ...     default = cleanup_line,
    ...     keep_empty = True,
    ...     )(dict(name = u'   ', email = None))
    ({}, None)
    >>> struct(
    ...     dict(
    ...         name = cleanup_line,
    ...         age = str_to_int,
    ...         email = str_to_email,
    ...         ),
    ...     default = cleanup_line,
    ...     keep_missing_values = True,
    ...     )(dict(name = u'   ', email = None))
    ({'age': None, 'email': None, 'name': None}, None)
    >>> struct(
    ...     dict(
    ...         name = cleanup_line,
    ...         age = str_to_int,
    ...         email = str_to_email,
    ...         ),
    ...     default = cleanup_line,
    ...     keep_missing_values = True,
    ...     skip_missing_items = True,
    ...     )(dict(name = u'   ', email = None))
    ({'email': None, 'name': None}, None)
    >>> import collections
    >>> struct(
    ...     dict(
    ...         name = cleanup_line,
    ...         age = str_to_int,
    ...         email = str_to_email,
    ...         ),
    ...     constructor = collections.OrderedDict,
    ...     )(dict(name = u'John Doe', age = u'72', email = u'john@doe.name'))
    (OrderedDict([('age', 72), ('email', u'john@doe.name'), ('name', u'John Doe')]), None)
    >>> struct(
    ...     collections.OrderedDict(
    ...         name = cleanup_line,
    ...         age = str_to_int,
    ...         email = str_to_email,
    ...         ),
    ...     )(dict(name = u'John Doe', age = u'72', email = u'john@doe.name'))
    (OrderedDict([('age', 72), ('email', u'john@doe.name'), ('name', u'John Doe')]), None)
    >>> struct(
    ...     dict(
    ...         name = cleanup_line,
    ...         age = str_to_int,
    ...         email = str_to_email,
    ...         ),
    ...     )(collections.OrderedDict(name = u'John Doe', age = u'72', email = u'john@doe.name'))
    ({'age': 72, 'email': u'john@doe.name', 'name': u'John Doe'}, None)

    Usage to convert a sequence (ie list, tuple, etc) or a set:

    >>> strict_converter = struct([
    ...     pipe(cleanup_line, exists),
    ...     str_to_int,
    ...     str_to_email,
    ...     ])
    ...
    >>> strict_converter([u'John Doe', u'72', u'john@doe.name'])
    ([u'John Doe', 72, u'john@doe.name'], None)
    >>> strict_converter([u'John Doe', u'john@doe.name'])
    ([u'John Doe', u'john@doe.name', None], {1: u'Value must be an integer'})
    >>> strict_converter([u'John Doe', None, u'john@doe.name'])
    ([u'John Doe', None, u'john@doe.name'], None)
    >>> strict_converter([u'John Doe', u'72', u'john@doe.name', u'   +33 9 12 34 56 78   '])
    ([u'John Doe', 72, u'john@doe.name', u'   +33 9 12 34 56 78   '], {3: u'Unexpected item'})
    >>> non_strict_converter = struct(
    ...     [
    ...         pipe(cleanup_line, exists),
    ...         str_to_int,
    ...         str_to_email,
    ...         ],
    ...     default = cleanup_line,
    ...     )
    ...
    >>> non_strict_converter([u'John Doe', u'72', u'john@doe.name'])
    ([u'John Doe', 72, u'john@doe.name'], None)
    >>> non_strict_converter([u'John Doe', u'john@doe.name'])
    ([u'John Doe', u'john@doe.name', None], {1: u'Value must be an integer'})
    >>> non_strict_converter([u'John Doe', None, u'john@doe.name'])
    ([u'John Doe', None, u'john@doe.name'], None)
    >>> non_strict_converter([u'John Doe', u'72', u'john@doe.name', u'   +33 9 12 34 56 78   '])
    ([u'John Doe', 72, u'john@doe.name', u'+33 9 12 34 56 78'], None)
    >>> import collections
    >>> struct(
    ...     [
    ...         pipe(cleanup_line, exists),
    ...         str_to_int,
    ...         str_to_email,
    ...         ],
    ...     constructor = tuple,
    ...     )([u'John Doe', u'72', u'john@doe.name'])
    ((u'John Doe', 72, u'john@doe.name'), None)
    >>> struct(
    ...     (
    ...         pipe(cleanup_line, exists),
    ...         str_to_int,
    ...         str_to_email,
    ...         ),
    ...     )([u'John Doe', u'72', u'john@doe.name'])
    ((u'John Doe', 72, u'john@doe.name'), None)
    >>> struct(
    ...     [
    ...         pipe(cleanup_line, exists),
    ...         str_to_int,
    ...         str_to_email,
    ...         ],
    ...     )((u'John Doe', u'72', u'john@doe.name'))
    ([u'John Doe', 72, u'john@doe.name'], None)
    """
    import collections

    if isinstance(converters, collections.Mapping):
        return structured_mapping(converters, constructor = constructor, default = default,
            keep_empty = keep_empty, keep_missing_values = keep_missing_values,
            skip_missing_items = skip_missing_items)
    assert isinstance(converters, collections.Sequence), \
        'Converters must be a mapping or a sequence. Got {0} instead.'.format(type(converters))
    assert not keep_missing_values, """Flag "keep_missing_values" can't be used for sequences."""
    assert not skip_missing_items, """Flag "skip_missing_items" can't be used for sequences."""
    return structured_sequence(converters, constructor = constructor, default = default,
        keep_empty = keep_empty)


def structured_mapping(converters, constructor = None, default = None, keep_empty = False, keep_missing_values = False,
        skip_missing_items = False):
    """Return a converter that maps a mapping of converters to a mapping (ie dict, etc) of values.

    .. note:: This converter should not be used directly. Use :func:`struct` instead.

    >>> strict_converter = structured_mapping(dict(
    ...     name = pipe(cleanup_line, exists),
    ...     age = str_to_int,
    ...     email = str_to_email,
    ...     ))
    ...
    >>> strict_converter(dict(name = u'John Doe', age = u'72', email = u'john@doe.name'))
    ({'age': 72, 'email': u'john@doe.name', 'name': u'John Doe'}, None)
    >>> strict_converter(dict(name = u'John Doe', email = u'john@doe.name'))
    ({'email': u'john@doe.name', 'name': u'John Doe'}, None)
    >>> strict_converter(dict(name = u'John Doe', age = None, email = u'john@doe.name'))
    ({'email': u'john@doe.name', 'name': u'John Doe'}, None)
    >>> strict_converter(dict(name = u'John Doe', age = u'72', phone = u'   +33 9 12 34 56 78   '))
    ({'phone': u'   +33 9 12 34 56 78   ', 'age': 72, 'name': u'John Doe'}, {'phone': u'Unexpected item'})
    >>> non_strict_converter = structured_mapping(
    ...     dict(
    ...         name = pipe(cleanup_line, exists),
    ...         age = str_to_int,
    ...         email = str_to_email,
    ...         ),
    ...     default = cleanup_line,
    ...     )
    ...
    >>> non_strict_converter(dict(name = u'John Doe', age = u'72', email = u'john@doe.name'))
    ({'age': 72, 'email': u'john@doe.name', 'name': u'John Doe'}, None)
    >>> non_strict_converter(dict(name = u'John Doe', email = u'john@doe.name'))
    ({'email': u'john@doe.name', 'name': u'John Doe'}, None)
    >>> non_strict_converter(dict(name = u'John Doe', age = u'72', email = u'john@doe.name',
    ...     phone = u'   +33 9 12 34 56 78   '))
    ({'phone': u'+33 9 12 34 56 78', 'age': 72, 'email': u'john@doe.name', 'name': u'John Doe'}, None)
    >>> structured_mapping(
    ...     dict(
    ...         name = cleanup_line,
    ...         age = str_to_int,
    ...         email = str_to_email,
    ...         ),
    ...     default = cleanup_line,
    ...     )(dict(name = u'   ', email = None))
    (None, None)
    >>> structured_mapping(
    ...     dict(
    ...         name = cleanup_line,
    ...         age = str_to_int,
    ...         email = str_to_email,
    ...         ),
    ...     default = cleanup_line,
    ...     keep_empty = True,
    ...     )(dict(name = u'   ', email = None))
    ({}, None)
    >>> structured_mapping(
    ...     dict(
    ...         name = cleanup_line,
    ...         age = str_to_int,
    ...         email = str_to_email,
    ...         ),
    ...     default = cleanup_line,
    ...     keep_missing_values = True,
    ...     )(dict(name = u'   ', email = None))
    ({'age': None, 'email': None, 'name': None}, None)
    >>> structured_mapping(
    ...     dict(
    ...         name = cleanup_line,
    ...         age = str_to_int,
    ...         email = str_to_email,
    ...         ),
    ...     default = cleanup_line,
    ...     keep_missing_values = True,
    ...     skip_missing_items = True,
    ...     )(dict(name = u'   ', email = None))
    ({'email': None, 'name': None}, None)
    >>> import collections
    >>> structured_mapping(
    ...     dict(
    ...         name = cleanup_line,
    ...         age = str_to_int,
    ...         email = str_to_email,
    ...         ),
    ...     constructor = collections.OrderedDict,
    ...     )(dict(name = u'John Doe', age = u'72', email = u'john@doe.name'))
    (OrderedDict([('age', 72), ('email', u'john@doe.name'), ('name', u'John Doe')]), None)
    >>> structured_mapping(
    ...     collections.OrderedDict(
    ...         name = cleanup_line,
    ...         age = str_to_int,
    ...         email = str_to_email,
    ...         ),
    ...     )(dict(name = u'John Doe', age = u'72', email = u'john@doe.name'))
    (OrderedDict([('age', 72), ('email', u'john@doe.name'), ('name', u'John Doe')]), None)
    >>> structured_mapping(
    ...     dict(
    ...         name = cleanup_line,
    ...         age = str_to_int,
    ...         email = str_to_email,
    ...         ),
    ...     )(collections.OrderedDict(name = u'John Doe', age = u'72', email = u'john@doe.name'))
    ({'age': 72, 'email': u'john@doe.name', 'name': u'John Doe'}, None)
    """
    if constructor is None:
        constructor = type(converters)
    converters = dict(
        (name, converter)
        for name, converter in (converters or {}).iteritems()
        if converter is not None
        )

    def structured_mapping_converter(values, state = states.default_state):
        if values is None:
            return values, None
        if default == 'ignore':
            values_converter = converters
        else:
            values_converter = converters.copy()
            for name in values:
                if name not in values_converter:
                    values_converter[name] = default if default is not None else fail(error = N_(u'Unexpected item'))
        errors = {}
        converted_values = {}
        for name, converter in values_converter.iteritems():
            if skip_missing_items and name not in values:
                continue
            value, error = converter(values.get(name), state = state)
            if value is not None or keep_missing_values:
                converted_values[name] = value
            if error is not None:
                errors[name] = error
        if keep_empty or converted_values:
            converted_values = constructor(converted_values)
        else:
            converted_values = None
        return converted_values, errors or None
    return structured_mapping_converter


def structured_sequence(converters, constructor = None, default = None, keep_empty = False):
    """Return a converter that map a sequence of converters to a sequence of values.

    .. note:: This converter should not be used directly. Use :func:`struct` instead.

    >>> strict_converter = structured_sequence([
    ...     pipe(cleanup_line, exists),
    ...     str_to_int,
    ...     str_to_email,
    ...     ])
    ...
    >>> strict_converter([u'John Doe', u'72', u'john@doe.name'])
    ([u'John Doe', 72, u'john@doe.name'], None)
    >>> strict_converter([u'John Doe', u'john@doe.name'])
    ([u'John Doe', u'john@doe.name', None], {1: u'Value must be an integer'})
    >>> strict_converter([u'John Doe', None, u'john@doe.name'])
    ([u'John Doe', None, u'john@doe.name'], None)
    >>> strict_converter([u'John Doe', u'72', u'john@doe.name', u'   +33 9 12 34 56 78   '])
    ([u'John Doe', 72, u'john@doe.name', u'   +33 9 12 34 56 78   '], {3: u'Unexpected item'})
    >>> non_strict_converter = structured_sequence(
    ...     [
    ...         pipe(cleanup_line, exists),
    ...         str_to_int,
    ...         str_to_email,
    ...         ],
    ...     default = cleanup_line,
    ...     )
    ...
    >>> non_strict_converter([u'John Doe', u'72', u'john@doe.name'])
    ([u'John Doe', 72, u'john@doe.name'], None)
    >>> non_strict_converter([u'John Doe', u'john@doe.name'])
    ([u'John Doe', u'john@doe.name', None], {1: u'Value must be an integer'})
    >>> non_strict_converter([u'John Doe', None, u'john@doe.name'])
    ([u'John Doe', None, u'john@doe.name'], None)
    >>> non_strict_converter([u'John Doe', u'72', u'john@doe.name', u'   +33 9 12 34 56 78   '])
    ([u'John Doe', 72, u'john@doe.name', u'+33 9 12 34 56 78'], None)
    >>> import collections
    >>> structured_sequence(
    ...     [
    ...         pipe(cleanup_line, exists),
    ...         str_to_int,
    ...         str_to_email,
    ...         ],
    ...     constructor = tuple,
    ...     )([u'John Doe', u'72', u'john@doe.name'])
    ((u'John Doe', 72, u'john@doe.name'), None)
    >>> structured_sequence(
    ...     (
    ...         pipe(cleanup_line, exists),
    ...         str_to_int,
    ...         str_to_email,
    ...         ),
    ...     )([u'John Doe', u'72', u'john@doe.name'])
    ((u'John Doe', 72, u'john@doe.name'), None)
    >>> structured_sequence(
    ...     [
    ...         pipe(cleanup_line, exists),
    ...         str_to_int,
    ...         str_to_email,
    ...         ],
    ...     )((u'John Doe', u'72', u'john@doe.name'))
    ([u'John Doe', 72, u'john@doe.name'], None)
    """
    if constructor is None:
        constructor = type(converters)
    converters = [
        converter
        for converter in converters or []
        if converter is not None
        ]

    def structured_sequence_converter(values, state = states.default_state):
        if values is None:
            return values, None
        if default == 'ignore':
            values_converter = converters
        else:
            values_converter = converters[:]
            while len(values) > len(values_converter):
                values_converter.append(default if default is not None else fail(error = N_(u'Unexpected item')))
        import itertools
        errors = {}
        converted_values = []
        is_empty = True
        for i, (converter, value) in enumerate(itertools.izip_longest(
                values_converter, itertools.islice(values, len(values_converter)))):
            value, error = converter(value, state = state)
            if value is not None:
                is_empty = False
            converted_values.append(value)
            if error is not None:
                errors[i] = error
        converted_values = constructor(converted_values) if not is_empty or keep_empty else None
        return converted_values, errors or None
    return structured_sequence_converter


def switch(key_converter, converters, default = None, handle_missing_value = False):
    """Return a converter that extracts a key from value and then converts value using the converter matching the key.

    >>> simple_type_switcher = switch(
    ...     function(lambda value: type(value)),
    ...     {
    ...         bool: set_value(u'boolean'),
    ...         int: python_data_to_str,
    ...         str: set_value(u'encoded string'),
    ...         },
    ...     handle_missing_value = True,
    ...     )
    >>> simple_type_switcher(True)
    (u'boolean', None)
    >>> simple_type_switcher(42)
    (u'42', None)
    >>> simple_type_switcher('Hello world!')
    (u'encoded string', None)
    >>> simple_type_switcher(u'Hello world!')
    (u'Hello world!', u'Expression "<type \\'unicode\\'>" doesn\\'t match any key')
    >>> simple_type_switcher(None)
    (None, u'Expression "None" doesn\\'t match any key')
    >>> type_switcher = switch(
    ...     function(lambda value: type(value)),
    ...     {
    ...         list: uniform_sequence(simple_type_switcher),
    ...         },
    ...     default = python_data_to_str,
    ...     )
    >>> type_switcher([False, 42])
    ([u'boolean', u'42'], None)
    >>> type_switcher(u'Hello world!')
    (u'Hello world!', None)
    >>> type_switcher(None)
    (None, None)
    >>> type_switcher([None])
    (None, {0: u'Expression "None" doesn\\'t match any key'})
    """
    def switch_converter(value, state = states.default_state):
        if value is None and not handle_missing_value:
            return None, None
        key, error = key_converter(value, state = state)
        if error is not None:
            return value, error
        if key not in converters:
            if default is None:
                return value, state._(u'''Expression "{}" doesn't match any key''').format(key)
            return default(value, state = state)
        return converters[key](value, state = state)
    return switch_converter


def test(function, error = N_(u'Test failed'), handle_missing_value = False, handle_state = False):
    """Return a converter that applies a test function to a value and returns an error when test fails.

    ``test`` always returns the initial value, even when test fails.

     See :doc:`how-to-create-converter` for more informations.

    >>> test(lambda value: isinstance(value, basestring))('hello')
    ('hello', None)
    >>> test(lambda value: isinstance(value, basestring))(1)
    (1, u'Test failed')
    >>> test(lambda value: isinstance(value, basestring), error = u'Value is not a string')(1)
    (1, u'Value is not a string')
    """
    def test_converter(value, state = states.default_state):
        if value is None and not handle_missing_value or function is None:
            return value, None
        ok = function(value, state = state) if handle_state else function(value)
        if ok:
            return value, None
        return value, state._(error)
    return test_converter


def test_between(min_value, max_value, error = None):
    """Return a converter that accepts only values between the two given bounds (included).

    .. warning:: Like most converters, a missing value (aka ``None``) is not compared.

    >>> test_between(0, 9)(5)
    (5, None)
    >>> test_between(0, 9)(0)
    (0, None)
    >>> test_between(0, 9)(9)
    (9, None)
    >>> test_between(0, 9)(10)
    (10, u'Value must be between 0 and 9')
    >>> test_between(0, 9, error = u'Number must be a digit')(10)
    (10, u'Number must be a digit')
    >>> test_between(0, 9)(None)
    (None, None)
    """
    return test(lambda value: min_value <= value <= max_value,
        error = error or N_(u'Value must be between {0} and {1}').format(min_value, max_value))


def test_conv(converter):
    """Return a converter that applies a applies a converter to test a value without modifying it.

    ``test_conv`` always returns the initial value, even when test fails.

    >>> test_conv(str_to_int)(u'42')
    (u'42', None)
    >>> test_conv(str_to_int)(u'Hello world!')
    (u'Hello world!', u'Value must be an integer')
    """
    def test_conv_converter(value, state = states.default_state):
        converted_value, error = converter(value, state = state)
        return value, error
    return test_conv_converter


def test_equals(constant, error = None):
    """Return a converter that accepts only values equals to given constant.

    .. warning:: Like most converters, a missing value (aka ``None``) is not compared. Furthermore, when *constant* is
       ``None``, value is never compared.

    >>> test_equals(42)(42)
    (42, None)
    >>> test_equals(dict(a = 1, b = 2))(dict(a = 1, b = 2))
    ({'a': 1, 'b': 2}, None)
    >>> test_equals(41)(42)
    (42, u'Value must be equal to 41')
    >>> test_equals(41, error = u'Value is not the answer')(42)
    (42, u'Value is not the answer')
    >>> test_equals(None)(42)
    (42, None)
    >>> test_equals(42)(None)
    (None, None)
    """
    return test(lambda value: value == constant if constant is not None else True,
        error = error or N_(u'Value must be equal to {0}').format(constant))


def test_exists(error = N_(u'Missing value')):
    """Return a converters that signals an error when value is missing (aka ``None``).

    .. note:: When error message "Missing value" can be kept, use :func:`exists` instead.

    >>> test_exists()(42)
    (42, None)
    >>> test_exists()(u'')
    (u'', None)
    >>> test_exists()(None)
    (None, u'Missing value')
    >>> test_exists(error = u'Required value')(None)
    (None, u'Required value')
    """
    def exists(value, state = states.default_state):
        if value is None:
            return value, state._(error)
        return value, None
    return exists


def test_greater_or_equal(constant, error = None):
    """Return a converter that accepts only values greater than or equal to given constant.

    .. warning:: Like most converters, a missing value (aka ``None``) is not compared.

    >>> test_greater_or_equal(0)(5)
    (5, None)
    >>> test_greater_or_equal(9)(5)
    (5, u'Value must be greater than or equal to 9')
    >>> test_greater_or_equal(9, error = u'Value must be a positive two-digits number')(5)
    (5, u'Value must be a positive two-digits number')
    >>> test_greater_or_equal(9)(None)
    (None, None)
    >>> test_greater_or_equal(None)(5)
    (5, None)
    """
    return test(lambda value: (value >= constant) if constant is not None else True,
        error = error or N_(u'Value must be greater than or equal to {0}').format(constant))


def test_in(values, error = None):
    """Return a converter that accepts only values belonging to a given set (or list or...).

    .. warning:: Like most converters, a missing value (aka ``None``) is not compared. Furthermore, when *values* is
       ``None``, value is never compared.

    >>> test_in('abcd')('a')
    ('a', None)
    >>> test_in(['a', 'b', 'c', 'd'])('a')
    ('a', None)
    >>> test_in(['a', 'b', 'c', 'd'])('z')
    ('z', u"Value must belong to ['a', 'b', 'c', 'd']")
    >>> test_in(['a', 'b', 'c', 'd'], error = u'Value must be a letter less than "e"')('z')
    ('z', u'Value must be a letter less than "e"')
    >>> test_in([])('z')
    ('z', u'Value must belong to []')
    >>> test_in(None)('z')
    ('z', None)
    >>> test_in(['a', 'b', 'c', 'd'])(None)
    (None, None)
    """
    return test(lambda value: value in values if values is not None else True,
        error = error or N_(u'Value must belong to {0}').format(values))


def test_is(constant, error = None):
    """Return a converter that accepts only values that are strictly equal to given constant.

    .. warning:: Like most converters, a missing value (aka ``None``) is not compared. Furthermore, when *constant* is
       ``None``, value is never compared.

    >>> test_is(42)(42)
    (42, None)
    >>> test_is(dict(a = 1, b = 2))(dict(a = 1, b = 2))
    ({'a': 1, 'b': 2}, u"Value must be {'a': 1, 'b': 2}")
    >>> test_is(41)(42)
    (42, u'Value must be 41')
    >>> test_is(41, error = u'Value is not the answer')(42)
    (42, u'Value is not the answer')
    >>> test_is(None)(42)
    (42, None)
    >>> test_is(42)(None)
    (None, None)
    """
    return test(lambda value: value is constant if constant is not None else True,
        error = error or N_(u'Value must be {0}').format(constant))


def test_isinstance(class_or_classes, error = None):
    """Return a converter that accepts only an instance of given class (or tuple of classes).

    >>> test_isinstance(basestring)('This is a string')
    ('This is a string', None)
    >>> test_isinstance(basestring)(42)
    (42, u"Value is not an instance of <type 'basestring'>")
    >>> test_isinstance(basestring, error = u'Value is not a string')(42)
    (42, u'Value is not a string')
    >>> test_isinstance((float, int))(42)
    (42, None)
    """
    return test(lambda value: isinstance(value, class_or_classes),
        error = error or N_(u'Value is not an instance of {0}').format(class_or_classes))


def test_less_or_equal(constant, error = None):
    """Return a converter that accepts only values less than or equal to given constant.

    .. warning:: Like most converters, a missing value (aka ``None``) is not compared.

    >>> test_less_or_equal(9)(5)
    (5, None)
    >>> test_less_or_equal(0)(5)
    (5, u'Value must be less than or equal to 0')
    >>> test_less_or_equal(0, error = u'Value must be negative')(5)
    (5, u'Value must be negative')
    >>> test_less_or_equal(9)(None)
    (None, None)
    >>> test_less_or_equal(None)(5)
    (5, None)
    """
    return test(lambda value: (value <= constant) if constant is not None else True,
        error = error or N_(u'Value must be less than or equal to {0}').format(constant))


def test_missing(error = N_(u'Unexpected value')):
    """Return a converters that signals an error when value is not missing (aka not ``None``).

    >>> test_missing()(42)
    (42, u'Unexpected value')
    >>> test_missing(error = u'No value allowed')(42)
    (42, u'No value allowed')
    >>> test_missing()(u'')
    (u'', u'Unexpected value')
    >>> test_missing()(None)
    (None, None)
    """
    def missing(value, state = states.default_state):
        if value is None:
            return value, None
        return value, state._(error)
    return missing


def test_not_in(values, error = None):
    """Return a converter that rejects only values belonging to a given set (or list or...).

    .. warning:: Like most converters, a missing value (aka ``None``) is not compared. Furthermore, when *values* is
       ``None``, value is never compared.

    >>> test_not_in('abcd')('e')
    ('e', None)
    >>> test_not_in(['a', 'b', 'c', 'd'])('e')
    ('e', None)
    >>> test_not_in('abcd')('a')
    ('a', u'Value must not belong to abcd')
    >>> test_not_in(['a', 'b', 'c', 'd'])('a')
    ('a', u"Value must not belong to ['a', 'b', 'c', 'd']")
    >>> test_not_in(['a', 'b', 'c', 'd'], error = u'Value must not be a letter less than "e"')('a')
    ('a', u'Value must not be a letter less than "e"')
    >>> test_not_in([])('z')
    ('z', None)
    >>> test_not_in(None)('z')
    ('z', None)
    >>> test_not_in(['a', 'b', 'c', 'd'])(None)
    (None, None)
    """
    return test(lambda value: value not in (values or []),
        error = error or N_(u'Value must not belong to {0}').format(values))


def translate(conversions):
    """Return a converter that converts values found in given dictionary and keep others as is.

    .. warning:: Like most converters, a missing value (aka ``None``) is not handled => It is never translated.

    >>> translate({0: u'bad', 1: u'OK'})(0)
    (u'bad', None)
    >>> translate({0: u'bad', 1: u'OK'})(1)
    (u'OK', None)
    >>> translate({0: u'bad', 1: u'OK'})(2)
    (2, None)
    >>> translate({0: u'bad', 1: u'OK'})(u'three')
    (u'three', None)
    >>> translate({None: u'problem', 0: u'bad', 1: u'OK'})(None)
    (None, None)
    >>> pipe(translate({0: u'bad', 1: u'OK'}), default(u'no problem'))(None)
    (u'no problem', None)
    """
    return function(lambda value: value
        if value is None or conversions is None or value not in conversions
        else conversions[value])


def uniform_mapping(key_converter, value_converter, constructor = dict, keep_empty = False, keep_missing_keys = False,
        keep_missing_values = False):
    """Return a converter that applies a unique converter to each key and another unique converter to each value of a
    mapping.

    >>> uniform_mapping(cleanup_line, str_to_int)({u'a': u'1', u'b': u'2'})
    ({u'a': 1, u'b': 2}, None)
    >>> uniform_mapping(cleanup_line, str_to_int)({u'   answer   ': u'42'})
    ({u'answer': 42}, None)
    >>> uniform_mapping(cleanup_line, pipe(test_isinstance(basestring), str_to_int))({u'a': u'1', u'b': u'2', 'c': 3})
    ({u'a': 1, 'c': 3, u'b': 2}, {'c': u"Value is not an instance of <type 'basestring'>"})
    >>> uniform_mapping(cleanup_line, str_to_int)({})
    (None, None)
    >>> uniform_mapping(cleanup_line, str_to_int, keep_empty = True)({})
    ({}, None)
    >>> uniform_mapping(cleanup_line, str_to_int)({None: u'42'})
    (None, None)
    >>> uniform_mapping(cleanup_line, str_to_int, keep_missing_keys = True)({None: u'42'})
    ({None: 42}, None)
    >>> uniform_mapping(cleanup_line, str_to_int)(None)
    (None, None)
    """
    def uniform_mapping_converter(values, state = states.default_state):
        if values is None:
            return values, None
        errors = {}
        converted_values = {}
        for key, value in values.iteritems():
            key, error = key_converter(key, state = state)
            if error is not None:
                errors[key] = error
            if key is None and not keep_missing_keys:
                continue
            value, error = value_converter(value, state = state)
            if value is not None or keep_missing_values:
                converted_values[key] = value
            if error is not None:
                errors[key] = error
        if keep_empty or converted_values:
            converted_values = constructor(converted_values)
        else:
            converted_values = None
        return converted_values, errors or None
    return uniform_mapping_converter


def uniform_sequence(converter, constructor = list, keep_empty = False, keep_missing_items = False):
    """Return a converter that applies the same converter to each value of a list.

    >>> uniform_sequence(str_to_int)([u'42'])
    ([42], None)
    >>> uniform_sequence(str_to_int)([u'42', u'43'])
    ([42, 43], None)
    >>> uniform_sequence(str_to_int)([u'42', u'43', u'Hello world!'])
    ([42, 43, u'Hello world!'], {2: u'Value must be an integer'})
    >>> uniform_sequence(str_to_int)([u'42', None, u'43'])
    ([42, 43], None)
    >>> uniform_sequence(str_to_int)([None, None])
    (None, None)
    >>> uniform_sequence(str_to_int, keep_empty = True)([None, None])
    ([], None)
    >>> uniform_sequence(str_to_int, keep_empty = True, keep_missing_items = True)([None, None])
    ([None, None], None)
    >>> uniform_sequence(str_to_int, keep_missing_items = True)([u'42', None, u'43'])
    ([42, None, 43], None)
    >>> uniform_sequence(str_to_int, keep_missing_items = True)([u'42', u'43', u'Hello world!'])
    ([42, 43, u'Hello world!'], {2: u'Value must be an integer'})
    >>> uniform_sequence(str_to_int, constructor = set)(set([u'42', u'43']))
    (set([42, 43]), None)
    """
    def uniform_sequence_converter(values, state = states.default_state):
        if values is None:
            return values, None
        errors = {}
        converted_values = []
        for i, value in enumerate(values):
            value, error = converter(value, state = state)
            if keep_missing_items or value is not None:
                converted_values.append(value)
            if error is not None:
                errors[i] = error
        if keep_empty or converted_values:
            converted_values = constructor(converted_values)
        else:
            converted_values = None
        return converted_values, errors or None
    return uniform_sequence_converter


# Level-2 Converters


cleanup_line = pipe(
    function(lambda value: value.strip()),
    cleanup_empty,
    )
"""Strip spaces from a string and remove it when empty.

    >>> cleanup_line(u'   Hello world!   ')
    (u'Hello world!', None)
    >>> cleanup_line('   ')
    (None, None)
    >>> cleanup_line(None)
    (None, None)
    """

cleanup_text = pipe(
    function(lambda value: value.replace(u'\r\n', u'\n').replace(u'\r', u'\n')),
    cleanup_line,
    )
"""Replaces CR + LF or CR to LF in a string, then strip spaces and remove it when empty.

    >>> cleanup_text(u'   Hello\\r\\n world!\\r   ')
    (u'Hello\\n world!', None)
    >>> cleanup_text('   ')
    (None, None)
    >>> cleanup_text(None)
    (None, None)
    """

exists = test_exists()
"""Return an error when value is missing (aka ``None``).

    .. note:: To change error message "Missing value", use :func:`test_exists` instead.

    >>> exists(42)
    (42, None)
    >>> exists(u'')
    (u'', None)
    >>> exists(None)
    (None, u'Missing value')
    """

extract_when_singleton = condition(
    test(lambda value: len(value) == 1 and not isinstance(value[0], (list, set, tuple))),
    function(lambda value: list(value)[0]),
    )
"""Extract first item of sequence when it is a singleton and it is not itself a sequence, otherwise keep it unchanged.

    >>> extract_when_singleton([42])
    (42, None)
    >>> extract_when_singleton([42, 43])
    ([42, 43], None)
    >>> extract_when_singleton([])
    ([], None)
    >>> extract_when_singleton(None)
    (None, None)
    >>> extract_when_singleton([[42]])
    ([[42]], None)
"""


# Level-3 Converters


python_data_to_bool = function(lambda value: bool(value))
"""Convert any Python data to a boolean.

    .. warning:: Like most converters, a missing value (aka ``None``) is not converted.

        When you want ``None`` to be converted to ``False``, use::

            pipe(python_data_to_bool, default(False))

    >>> python_data_to_bool(0)
    (False, None)
    >>> python_data_to_bool(-1)
    (True, None)
    >>> python_data_to_bool(u'0')
    (True, None)
    >>> python_data_to_bool(u'1')
    (True, None)
    >>> python_data_to_bool(u'true')
    (True, None)
    >>> python_data_to_bool(u'false')
    (True, None)
    >>> python_data_to_bool(u'  0  ')
    (True, None)
    >>> python_data_to_bool(u'    ')
    (True, None)
    >>> python_data_to_bool(None)
    (None, None)
    """

str_to_bool = pipe(cleanup_line, clean_str_to_bool)
"""Convert a string to a boolean.

    .. warning:: Like most converters, a missing value (aka ``None``) is not converted.

        When you want ``None`` to be converted to ``False``, use::

            pipe(str_to_bool, default(False))

    >>> str_to_bool(u'0')
    (False, None)
    >>> str_to_bool(u'   0   ')
    (False, None)
    >>> str_to_bool(u'1')
    (True, None)
    >>> str_to_bool(u'   1   ')
    (True, None)
    >>> str_to_bool(None)
    (None, None)
    >>> str_to_bool(u'vrai')
    (u'vrai', u'Value must be a boolean')
    >>> str_to_bool(u'on')
    (u'on', u'Value must be a boolean')
"""

str_to_email = pipe(cleanup_line, clean_str_to_email)
"""Convert a string to an email address.

    >>> str_to_email(u'john@doe.name')
    (u'john@doe.name', None)
    >>> str_to_email(u'mailto:john@doe.name')
    (u'john@doe.name', None)
    >>> str_to_email(u'root@localhost')
    (u'root@localhost', None)
    >>> str_to_email('root@127.0.0.1')
    ('root@127.0.0.1', u'Invalid domain name')
    >>> str_to_email(u'root')
    (u'root', u'An email must contain exactly one "@"')
    >>> str_to_email(u'    john@doe.name  ')
    (u'john@doe.name', None)
    >>> str_to_email(None)
    (None, None)
    >>> str_to_email(u'    ')
    (None, None)
    """

str_to_float = pipe(cleanup_line, python_data_to_float)
"""Convert a string to float.

    >>> str_to_float('42')
    (42.0, None)
    >>> str_to_float(u'   42.25   ')
    (42.25, None)
    >>> str_to_float(u'hello world')
    (u'hello world', u'Value must be a float')
    >>> str_to_float(None)
    (None, None)
    """

str_to_int = pipe(cleanup_line, python_data_to_int)
"""Convert a string to an integer.

    >>> str_to_int('42')
    (42, None)
    >>> str_to_int(u'   42   ')
    (42, None)
    >>> str_to_int(u'42.75')
    (u'42.75', u'Value must be an integer')
    >>> str_to_int(None)
    (None, None)
    """

str_to_slug = make_str_to_slug()
"""Convert a string to a slug.

    .. note:: For a converter that doesn't use "-" as word separators or doesn't convert characters to lower case,
        see :func:`str_to_normal_form`.

    >>> str_to_slug(u'   Hello world!   ')
    (u'hello-world', None)
    >>> str_to_slug('   Hello world!   ')
    (u'hello-world', None)
    >>> str_to_slug(u'')
    (None, None)
    >>> str_to_slug(u'   ')
    (None, None)
    """

str_to_url_path_and_query = pipe(cleanup_line, clean_str_to_url_path_and_query)
"""Convert a string to the path and query of an URL.

    >>> str_to_url_path_and_query(u'/Biryani/presentation.html#tutorial')
    (u'/Biryani/presentation.html', None)
    >>> str_to_url_path_and_query(u'/Biryani/search.html?q=pipe')
    (u'/Biryani/search.html?q=pipe', None)
    >>> str_to_url_path_and_query(u'   /Biryani/search.html?q=pipe   ')
    (u'/Biryani/search.html?q=pipe', None)
    >>> str_to_url_path_and_query(u'http://packages.python.org/Biryani/search.html?q=pipe')
    (u'http://packages.python.org/Biryani/search.html?q=pipe', u'URL must not be complete')
    >>> print str_to_url_path_and_query(None)
    (None, None)
    """


# Utility Functions


def check(converter_or_value_and_error, clear_on_error = False):
    """Check a conversion and either return its value or raise a *ValueError* exception.

    This function can be called with either a converter or the result of a conversion.

    Usage with a converter:

    >>> check(str_to_int)(u'42')
    42
    >>> check(str_to_int)(u'hello world')
    Traceback (most recent call last):
    ValueError:
    >>> check(pipe(python_data_to_str, test_isinstance(unicode), str_to_bool))(42)
    True
    >>> check(str_to_int, clear_on_error = True)(u'42')
    42
    >>> print check(str_to_int, clear_on_error = True)(u'hello world')
    None

    Usage with a conversion result :

    >>> check(str_to_int(u'42'))
    42
    >>> check(str_to_int(u'hello world'))
    Traceback (most recent call last):
    ValueError:
    >>> check(pipe(python_data_to_str, test_isinstance(unicode), str_to_bool)(42))
    True
    >>> check(str_to_int(u'42'), clear_on_error = True)
    42
    >>> print check(str_to_int(u'hello world'), clear_on_error = True)
    None
    """
    import collections

    if isinstance(converter_or_value_and_error, collections.Sequence):
        value, error = converter_or_value_and_error
        if error is not None:
            if clear_on_error:
                return None
            raise ValueError('Error: {} for: {}'.format(error, value))
        return value
    else:
        # converter_or_value_and_error is a converter.
        def check_converter(*args, **kwargs):
            value, error = converter_or_value_and_error(*args, **kwargs)
            if error is not None:
                if clear_on_error:
                    return None
                raise ValueError('Error: {} for: {}'.format(error, value))
            return value
        return check_converter
