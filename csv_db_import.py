#!/usr/bin/env python
"""
Import a CSV file into a SQL database table.

This script opens a CSV file, and places the values into a freshly created
database table.  It attempts to guess as much as it can from the file
(e.g. which data types to create).

You can use the first row to name the columns (use the -c option).  You can also
use a row to explicitly specify the data type of each column (use the -t
option); otherwise it will try to make an educated guess using the first few
rows of the table (you can change the number, see options).
"""

# stdlib imports
import csv, re
from os.path import *
from datetime import date, datetime
from itertools import izip
from time import strptime
from subprocess import *

# dbapi imports
import psycopg2 as dbapi


def parse_columns(csv):
    "Figure out the column names."
    cols = None
    if opts.columns:
        cols = csv.next()

    else:
        # Create a list of columns using the length of the next line.
        idx = csv.getindex()
        colrow = csv.next()
        cols = ['col%d' % x for x in xrange(len(colrow))]
        csv.rewind(idx)

    return cols


def guess_row_type(row):
    """
    Guess the type of the row given some values in the row.
    """
    txttype = 'text'

    lens = set(len(x) for x in row)
    if len(lens) == 1:
        for x in row:
            if not re.match('(\d\d\d\d)-(\d\d)-(\d\d)', x):
                break
        else:
            return 'date'

        txttype = ('varchar', lens.pop())

    # Try integers.
    for x in row:
        try:
            int(x)
        except ValueError:
            break
    else:
        return 'integer'

    # Try floats.
    for x in row:
        try:
            float(x)
        except ValueError:
            break
    else:
        typ = 'float'

        # Try money.
        for x in row:
            if not re.match('\d+\.\d\d', x):
                break
        else:
            typ = ('numeric', '10,2')

        return typ

    return txttype

def parse_types(csv, nbcols=None):
    "Figure out the types."

    # Figure out the data types.
    types = None
    if opts.types:
        types = []
        for t in csv.next():
            mo = re.match('([a-z]+)\((.+)\)', t)
            if mo:
                t, sz = mo.group(1, 2)
                types.append((t, sz))
            else:
                types.append(t)
            if t not in typ_convert:
                raise SystemExit("Invalid type: %s" % t)
    else:
        idx = csv.getindex()

        if not opts.columns:
            # Defensively skip a forgotten column naming row to raise the
            # probability of getting the right types.  If this is the case it
            # will blow up later on insertion of the column names in the rows,
            # which is a clearer indication of the problem than guessing all
            # rows of text and having the extraneous column naming row inserted
            # with the data.  Plus any row should be as good a guess as any, so
            # this shouldn't really hurt.
            csv.next()

        guessrows = []
        for i, row in enumerate(csv):
            if opts.nbguessrows and i == opts.nbguessrows:
                break
            guessrows.append(row)
            if i%10000 == 0 :
                print 'checking %d-th row' % i 
        csv.rewind(idx)

        types = map(guess_row_type, izip(*guessrows))

        missing = nbcols - len(types)
        if missing:
            types.extend(['text'] * missing)

    return types


def create_table(name, coltypes):
    """
    Produce the schema creation statement.
    """
    decl = []
    for col, typ in coltypes:
        sz = None
        if isinstance(typ, tuple):
            typ, sz = typ
        if sz:
            typ = '%s(%s)' % (typ, sz)

        decl.append('"%s" %s' % (col, typ))

    return 'CREATE TABLE %s (\n%s\n);' % (name, ',\n'.join(decl))


class BriefCSVFile(object):
    """
    A CSV reader file abstraction that caches the results.  It also provides a
    way to automatically strip the whitespace around the entries.  It also
    automatically skips empty rows.
    """
    def __init__(self, filename, mode, strip=False):

        import csv
        self.reader = csv.reader(open(filename, mode),
                                 delimiter=opts.delimiter,
                                 skipinitialspace=1)

        self.strip = strip
        "Strip the whitespace around the entries."

        self.cached_rows = []
        self.index = 0
        "Row cache and current row index."

    def __iter__(self):
        return self

    def readrow(self):
        row = None
        while not row:
            row = self.reader.next()
        return [x.strip() for x in row]

    def next(self):
        if self.cached_rows is None:
            return self.readrow()
        else:
            try:
                newrow = self.cached_rows[self.index]
            except IndexError:
                newrow = self.readrow()
                self.cached_rows.append(newrow)
            self.index += 1
        return newrow

    def getindex(self):
        return self.index

    def rewind(self, index):
        self.index = index

    def disable_cache(self):
        self.cached_rows = None


def initdb(opts, table, table_stmt):
    """
    Make sure that the database exists and return a valid connection to the
    database.
    """
    # Try to create the database.
    cmd = ['createdb', opts.database]
    if opts.user:
        cmd.append('--user="%s"' % opts.user)
    if opts.password:
        cmd.append('--password="%s"' % opts.password)
    call(cmd, stdout=PIPE, stderr=PIPE)
    
    # Connect to the database.
    params = dict(x for x in dict(database=opts.database,
                                  user=opts.user,
                                  password=opts.password,
                                  port=opts.port,
                                  host=opts.host).items() if x[1] is not None)
    conn = dbapi.connect(**params)

    # Try to drop the table.
    cursor = conn.cursor()
    try:
        cursor.execute('DROP TABLE %s;' % table)
    except dbapi.ProgrammingError:
        conn.rollback()
    else:
        conn.commit()

    # Create the table.
    cursor.execute(table_stmt)
    conn.commit()
    
    return conn


def str2date(s):
    s = s.replace('?', '1')
    return date(*strptime(s, "%Y-%m-%d")[0:3])

def str2datetime(s):
    return datetime(*strptime(x, "%Y-%m-%dT%H:%M:%S")[0:6])

def str2uni(s):
    return s.decode(opts.encoding)

typ_convert = {'integer': int,
               'float': float,
               'numeric': float,
               'decimal': float,
               'text': str2uni,
               'char': str2uni,
               'varchar': str2uni,
               'date': str2date,
               'datetime': str2datetime}

def process_contents(conn, csv, table, cols, types):
    """
    Insert the contents of the CSV file.
    """

    # Process all the rows, convert into the appropriate data types and insert.
    nbcols = len(cols)
    insert_stmt = """
      INSERT INTO %s (%s) VALUES (%s)
      """ % (table, ','.join('"%s"' % x for x in cols), ','.join(['%s']*nbcols))

    def getconv(x):
        if isinstance(x, tuple):
            x = x[0]
        return typ_convert[x]
        
    converters = map(getconv, types)
    cursor = conn.cursor()
    i = 0
    for row in csv:
        values = [conv(val) for conv, val in izip(converters, row)]
        values.extend( [None] * (nbcols - len(values)) )

        cursor.execute(insert_stmt, values)
        i += 1
        if i % 100 == 0:
            print '%d rows inserted' %  i
            conn.commit()
            cursor = conn.cursor()
    conn.commit()


def main():
    import optparse
    parser = optparse.OptionParser(__doc__.strip())

    parser.add_option('-c', '--columns', action='store_true',
                      help="Assume that the file contains a line dedicated to "
                      "naming the columns.")

    parser.add_option('-t', '--types', action='store_true',
                      help="Assume that the file contains a line dedicated to "
                      "specifying the column types, normally after the column "
                      "names if there is such a line.")

    parser.add_option('-d', '--delimiter', action='store',
                      default=',',
                      help="Delimiter character to use.")

    parser.add_option('-n', '--table', '--table-name', action='store',
                      default=None,
                      help="Set the table name (default will be the basename "
                      "of the file.")

    parser.add_option('-s', '--schema', action='store',
                     default=None,
                     help="Schema name (default create table at top level)")

    parser.add_option('-x', '--nodata', action='store_true',
                     default=None,
                     help="Create the table based on the csv header but do not insert any rows")

    parser.add_option('-e', '--encoding', action='store',
                      default='iso-8859-1',
                      help="Encoding of the CSV file.")

    parser.add_option('-r', '--guessrows', dest='nbguessrows',
                      action='store', type='int', default=16,
                      help="Number of guess rows to use. Use 0 to specify all.")

    group = optparse.OptionGroup(parser, "Options for connecting to a database")

    group.add_option('-D', '--database', action='store',
                     default='csvimport',
                     help="Database name (default is 'csvimport')")

    group.add_option('-U', '--user', action='store',
                     default=None,
                     help="Database user")

    group.add_option('-p', '--password', action='store',
                     default=None,
                     help="Database password")

    group.add_option('-V', '--port', action='store', type='int',
                     default=None,
                     help="Database port")

    group.add_option('-H', '--host', action='store',
                     default='localhost',
                     help="Database hostname")

    parser.add_option_group(group)

    global opts; opts, args = parser.parse_args()

    if not args:
        parser.error("You must specify a single CSV filename.")
    csvfn, = args

    table = opts.table
    if not table:
        table = splitext(basename(csvfn))[0]

    schema = opts.schema
    if schema:
        table = schema + '.' + table

    # Open up the CSV file.
    csv = BriefCSVFile(csvfn, 'rb', strip=True)

    # Obtain the list of column names and associated data types.
    cols = parse_columns(csv)
    types = parse_types(csv, len(cols))
    if len(cols) != len(types):
        raise SystemExit("Error: invalid number of column names and types.")
    if not opts.types:
        print 'Guessing types for data:', types

    # Insure/create a database and an appropriate table for the data.
    conn = initdb(opts, table, create_table(table, zip(cols, types)))
    assert conn

    if not opts.nodata:
        print "Data will be stored in: %s/%s" % (opts.database, table)
        process_contents(conn, csv, table, cols, types)

    conn.close()

    
if __name__ == '__main__':
    main()

