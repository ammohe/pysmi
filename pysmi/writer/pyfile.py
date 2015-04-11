import os
import sys
import time
import imp
import py_compile
from pysmi.writer.base import AbstractWriter
from pysmi import debug
from pysmi import error

class PyFileWriter(AbstractWriter):
    suffixes = {}
    for sfx, mode, typ in imp.get_suffixes():
        if typ not in suffixes:
            suffixes[typ] = []
        suffixes[typ].append((sfx, mode))

    def __init__(self, path):
        self._path = os.path.normpath(path)

    def __str__(self): return '%s{"%s"}' % (self.__class__.__name__, self._path)

    def putData(self, mibname, data, dryRun=False):
        if dryRun:
            debug.logger & debug.flagWriter and debug.logger('dry run mode')
            return
        if not os.path.exists(self._path):
            try:
                os.makedirs(self._path)
            except OSError:
                raise error.PySmiError('failure creating destination directory %s: %s' % (self._path, sys.exc_info()[1]))

        pyfile = os.path.join(self._path, mibname.upper()) + self.suffixes[imp.PY_SOURCE][0][0]
        try:
            f = open(pyfile, 'w')
            f.write(data.encode('utf-8'))
            f.close()
        except (IOError, UnicodeEncodeError):
            try:
                os.unlink(pyfile)
            except:
                pass
            raise error.PySmiError('failure writing file %s: %s' % (pyfile, sys.exc_info()[1]))

        debug.logger & debug.flagWriter and debug.logger('file %s created' % pyfile)

        try:
            py_compile.compile(pyfile, doraise=True)
        except (SyntaxError, py_compile.PyCompileError):
            pass  # XXX
        except:
            try:
                os.unlink(pyfile)
            except:
                pass
            raise error.PySmiError('failure compiling %s: %s' % (pyfile, sys.exc_info()[1]))

        debug.logger & debug.flagWriter and debug.logger('compiled %s' % pyfile)

if __name__ == '__main__':
    from pysmi import debug

    debug.setLogger(debug.Debug('all'))

    f = PyFileWriter('/tmp/x')

    f.getTimestamp('X')

    f.putData('X', 'print(123)')
