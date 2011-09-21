import psycopg2
converter = psycopg2.extensions.string_types[1015]
unicode_converter = psycopg2.extensions.string_types[1043]


def convert_tuple(datum, cursor):
    datum = datum.decode(cursor.connection.encoding)
    datum = datum.lstrip('(')
    if datum.startswith('"{"'):
        return convert_tuple_array(datum.strip('"'), cursor)

    isnull = True
    current_token = u""
    elems = []
    in_string = False
    escape = False
    datum = iter(datum)
    stop_marker = object()
    a = next(datum)
    while a != stop_marker:
        if in_string:
            if not escape:
                if a == '"':
                    in_string = False
                    elems.append(current_token)
                    isnull = True
                    a = next(datum, stop_marker)
                    current_token = u""
                else:
                    current_token += a
            elif a == '\\':
                escape = True

        elif a == '"':
            in_string = True
            isnull = False
        elif a in (',', ')'):
            elems.append(None if isnull else current_token)
            isnull = True
            current_token = u""
        else:
            isnull = False
            current_token += a
        a = next(datum, stop_marker)
    return tuple(elems)


def convert_tuple_array(data, cursor):
    """Convert an array of tuple from a pg string
    to a python array of tuple"""
    data = converter(data, cursor)
    tuples = []
    for datum in data:
        tuples.append(convert_tuple(datum, cursor))
    return tuples

TUPLE_ARRAY = psycopg2.extensions.new_type(
    (2287,), "TUPLEARRAY", convert_tuple_array)
TUPLE = psycopg2.extensions.new_type((2249,), "TUPLE", convert_tuple)
psycopg2.extensions.register_type(TUPLE_ARRAY)
psycopg2.extensions.register_type(TUPLE)
