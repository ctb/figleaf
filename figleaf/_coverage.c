/* Coverage collection module */

/*
This module collects coverage information for python programs.  The C
implementation is 3 times faster than the standard python implementations of
coverage collection.  Additional algorithm improvements have increased the
speed further.

Module interface:
Collector(exclude_prefix=None, include_prefix=None):

exclude_prefix may be set to a prefix of files to not include in coverage.
include_prefix may be set to a prefix to limit coverage to - files not starting with this prefix will not be covered.  exclude_prefix
and include_prefix are exclusive.

Collector.enable: begins coverage collection.
Collector.disable: ends coverage collection.
Collector.getlines: returns an {filename : [lineno, lineno] } array including each covered file and line.
Collector.clear: removes all coverage data from this object.

*/
#include <Python.h>
#include <frameobject.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <pythread.h>

/*
DEFAULT_FILE_SIZE: File size that most python files are smaller than
(counting line numbers).  We assert that most python code occurs on line #s
less than the D_F_S, and optimize our behavior for such lines, and fall back to
slower behavior for larger files.  Lowering this number decreases the memory
usage of coverage at the cost of slowing down coverage for lines greater than
this number.
*/

static int DEFAULT_FILE_SIZE = 5000;

/* Per file name + array storage - a pointer to one of these objects is
   stored as the "latest" cache, so that both latest filename and line_array
   can be updated atomically.  */

int cache_hit = 0;
int total_lines = 0;
int total_exclude = 0;
int exclude_hit = 0;
typedef struct {
    int * line_array;
    PyObject * filename;
} FileCoverage;

/* cleanup method for FileCoverage CObjects */
void dealloc_file_coverage(void * f) {
    FileCoverage * file_coverage;
    file_coverage = (FileCoverage *)f;
    free(file_coverage->line_array);
    free(file_coverage);
}

typedef struct {
    PyObject_HEAD
    PyObject * files;           /* {file : FileCoverage() } dict 
                                   for lines < DEFAULT_FILE_SIZE } */
    FileCoverage * latest_file; /* pointer to name, lines for last-used file */
    PyObject * latest_exclude;  /* pointer to last excluded file for 
                                   quick check */
    PyObject * large_files;     /* {(file, lineno) : None} dict
                                   for lines >= DEFAULT_FILE_SIZE */
    char * exclude_prefix;      /* ignore files starting with this prefix */
    char * include_prefix;      /* ignore files not starting with this prefix */
    PyObject * lock;            /* Used to avoid threading 
                                   contention when adding files */
} CollectorObject;

staticforward PyTypeObject PyCollector_Type;

/*
slow_add_file:
Standard way of adding file - add (filename, lineno) to python dict.
This is slow but always works - used for lineno > DEFAULT_FILE_SIZE
*/
int slow_add_file(CollectorObject * co, PyObject * filename, long lineno) {
    PyObject * t = NULL;
    t = PyTuple_New(2);
    if(t == NULL)
        goto error;
    Py_INCREF(filename);
    if(0 != PyTuple_SetItem(t, 0, filename))
        goto error;
    if(0 != PyTuple_SetItem(t, 1, PyInt_FromLong(lineno)))
        goto error;
    Py_INCREF(Py_None);
    if(0 != PyDict_SetItem(co->large_files, t, Py_None))
        goto error;
    Py_DECREF(t);
    return 0;
error:
    Py_XDECREF(t);
    return -1;
}

/* add_new_file: adds FileCoverage object for filename to collector dict
   in a (hopefully) thread-safe manner.
*/
static FileCoverage * add_new_file(CollectorObject * co, PyObject * filename) {
    FileCoverage * file_coverage;
    PyObject * file_coverage_obj;
    PyThread_acquire_lock(co->lock, 1);
    /* thread safe check to ensure someone didn't add the file while
       we were waiting for the lock */
    file_coverage_obj = PyDict_GetItem(co->files, filename);
    if(file_coverage_obj != NULL) {
        PyThread_release_lock(co->lock);
        file_coverage = (FileCoverage *)PyCObject_AsVoidPtr(file_coverage_obj);
        return file_coverage;
    }
    file_coverage = malloc(sizeof(FileCoverage));
    file_coverage->line_array = calloc(DEFAULT_FILE_SIZE, sizeof(int));
    if(file_coverage == NULL) {
       PyErr_SetFromErrno(PyExc_OSError);
       goto error;
    }
    file_coverage_obj = PyCObject_FromVoidPtr((void *)file_coverage, 
                                              dealloc_file_coverage);
    if(file_coverage_obj == NULL) {
        goto error;
    }
    if(0 != PyDict_SetItem(co->files, filename, file_coverage_obj))
        goto error;
    Py_INCREF(filename);
    file_coverage->filename = filename;
    PyThread_release_lock(co->lock);
    return file_coverage;
error:
    if(file_coverage)
        free(file_coverage->line_array);
        free(file_coverage);
    PyThread_release_lock(co->lock);
    return NULL;
}

/* get_or_add_file: return file coverage object for filename, creating it
   if necessary */
static FileCoverage * get_or_add_file(CollectorObject * co, PyObject * filename) {
    FileCoverage * file_coverage;
    PyObject * file_coverage_obj = NULL;

    file_coverage_obj = PyDict_GetItem(co->files, filename);
    if (file_coverage_obj == NULL)
        file_coverage = add_new_file(co, filename);
    else
        file_coverage = (FileCoverage *)PyCObject_AsVoidPtr(file_coverage_obj);
    if(PyErr_Occurred())
        goto error;
    return file_coverage;
error:
    return NULL;

}

/* mark_line: adds filename + lineno combination to coverage data */
static void mark_line(CollectorObject * co, PyObject * filename, long lineno,
                     FileCoverage * file_coverage) {
    if (lineno >= DEFAULT_FILE_SIZE) {
        slow_add_file(co, filename, lineno);
    }
    else {
        file_coverage->line_array[lineno] = 1;
    }
}

static int should_exclude_file(CollectorObject * co, PyFrameObject * frame) {
    PyObject * filename;
    if (co->exclude_prefix) {
        filename = PyDict_GetItemString(frame->f_globals, "__file__");
        /* NOTE - next section is mimicing some behavior
           in figleaf that I'm not sure I quite understand.
           For the exclude prefix, we always translate 
           the path to an absolute path, but for include 
           prefix, we'll use the relative path that's kept
           in frame->f_lineno.
        */
        if (filename == NULL)
            filename = frame->f_code->co_filename;
        if (0 == strncmp(co->exclude_prefix, \
                         PyString_AS_STRING(filename),
                         strlen(co->exclude_prefix))) {
            /* match exclude prefix */
           return 1;
        }
    }
    if (co->include_prefix \
        && (0 != strncmp(co->include_prefix, \
                         PyString_AS_STRING(frame->f_code->co_filename),
                         strlen(co->include_prefix)))) {
        /* do not match exclude prefix */
        return 1;
    }
    return 0;
}


/* collector_callback: CPython's callback interface for tracing.
   adds line coverage information.  */
int collector_callback(PyObject *self, PyFrameObject *frame, int what,
		   PyObject *arg) {
    CollectorObject *co = (CollectorObject *) self;
    PyObject * filename;

    switch (what) {
    case PyTrace_LINE:
        filename = frame->f_code->co_filename;
        if (!co->latest_file \
            || (co->latest_file->filename != filename && \
                strcmp(PyString_AS_STRING(co->latest_file->filename), 
                      PyString_AS_STRING(filename)))) {
            /* Cache miss - we've switched files and need to perform
               the slow actions of checking to make sure we should
               record this file */
            if (co->latest_exclude == filename) {
                total_exclude++;
                exclude_hit++;
                break;
            }
            else if(should_exclude_file(co, frame)) {
                total_exclude++;
                Py_INCREF(filename);
                Py_XDECREF(co->latest_exclude);
                co->latest_exclude = filename;
                break;
            }
            co->latest_file = get_or_add_file(co, filename);
            if(co->latest_file == NULL)
                goto error;
        }
        else {
            cache_hit++;
        }
        total_lines++;
        mark_line(co, filename, frame->f_lineno, 
                  co->latest_file);
	break;
    default:
        frame->f_trace = NULL;
	break;
    }
    return 0;
error:
    frame->f_trace = NULL;
    return 0;
}

/* collector methods */
PyDoc_STRVAR(getlines_doc,
	     "getlines() -> dictionary of executed (file, lineno) tuples");
static PyObject*
collector_getlines(CollectorObject *self, PyObject *args, PyObject *kw)
{
    PyObject *filename, *file_coverage_obj, *line_list_obj;
    Py_ssize_t pos = 0;
    int i;
    PyObject * results;
    printf("Cache hit: %d/%d: %0.2f\n", cache_hit, total_lines, 
            cache_hit / (total_lines * 1.0));
    printf("Exclude hit: %d/%d: %0.2f\n", exclude_hit, total_exclude, 
            exclude_hit / (total_exclude * 1.0));

    results = PyDict_New();
    FileCoverage * file_coverage;
    int * line_array;
    int idx = 0;

    while (PyDict_Next(self->files, &pos, &filename, &file_coverage_obj)) {
        file_coverage = (FileCoverage *)PyCObject_AsVoidPtr(file_coverage_obj);
        line_array = file_coverage->line_array;

        idx = 0;
        for(i=0; i < DEFAULT_FILE_SIZE; i++) {
            if(line_array[i]) {
                idx++;
            }
        }
        line_list_obj = PyList_New(idx);
        idx = 0;
        for(i=0; i < DEFAULT_FILE_SIZE; i++) {
            if(line_array[i]) {
                PyList_SET_ITEM(line_list_obj, idx, PyInt_FromLong(i));
                idx++;
            }
        }
        PyDict_SetItem(results, filename, line_list_obj);
   }
   return results;
}

PyDoc_STRVAR(enable_doc, "enable() -> enable the coverage collector");
static PyObject*
collector_enable(CollectorObject *self, PyObject *args, PyObject *kw)
{
    PyEval_SetTrace(collector_callback, (PyObject*)self);
    Py_INCREF(Py_None);
    return Py_None;
}

PyDoc_STRVAR(disable_doc, "diable() -> disable the coverage collector");
static PyObject*
collector_disable(CollectorObject *self, PyObject *args, PyObject *kw)
{
    Py_INCREF(Py_None);
    PyEval_SetTrace(NULL, NULL);
    return Py_None;
}

PyDoc_STRVAR(clear_doc, "clear() -> clear the coverage collector");
static PyObject*
collector_clear(CollectorObject *self, PyObject *args, PyObject *kw)
{
    PyDict_Clear(self->files);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef collector_methods[] = {
    { "getlines", (PyCFunction)collector_getlines, METH_NOARGS, getlines_doc },
    { "enable", (PyCFunction)collector_enable, METH_NOARGS, enable_doc },
    { "disable", (PyCFunction)collector_disable, METH_NOARGS, disable_doc },
    { "clear", (PyCFunction)collector_clear, METH_NOARGS, clear_doc },
    { NULL, NULL}
};

/* type implementation */
static void
collector_dealloc(CollectorObject *co)
{
    Py_XDECREF(co->files);
    Py_XDECREF(co->latest_exclude);
    co->ob_type->tp_free(co);
    if (co->exclude_prefix != NULL) {
        free(co->exclude_prefix);
    }
    if (co->include_prefix != NULL) {
        free(co->include_prefix);
    }
    co->latest_file = NULL;
    PyThread_free_lock(co->lock);
}

static int
collector_init(CollectorObject *co, PyObject *args, PyObject *kw)
{
    co->files = PyDict_New();
    co->large_files = PyDict_New();
    co->lock = PyThread_allocate_lock();
    PyObject *excludePrefix, *includePrefix;
    excludePrefix = includePrefix = Py_None;
    PyArg_ParseTuple(args, "|OO", &excludePrefix, &includePrefix);
    if(excludePrefix != Py_None) {
        co->exclude_prefix = strndup(PyString_AS_STRING(excludePrefix), 4096);
    }
    else {
        co->exclude_prefix = NULL;
    }
    if(includePrefix != Py_None) {
        co->include_prefix = strndup(PyString_AS_STRING(includePrefix), 4096);
    }
    else {
        co->include_prefix = NULL;
    }
    co->latest_file = NULL;
    co->latest_exclude = NULL;
    return 0;
}

PyDoc_STRVAR(collector_doc, "A coverage collector");
statichere PyTypeObject PyCollector_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                      /* ob_size */
    "_coverage.Collector",                  /* tp_name */
    sizeof(CollectorObject),                /* tp_basicsize */
    0,                                      /* tp_itemsize */
    (destructor)collector_dealloc,          /* tp_dealloc */
    0,                                      /* tp_print */
    0,                                      /* tp_getattr */
    0,                                      /* tp_setattr */
    0,                                      /* tp_compare */
    0,                                      /* tp_repr */
    0,                                      /* tp_as_number */
    0,                                      /* tp_as_sequence */
    0,                                      /* tp_as_mapping */
    0,                                      /* tp_hash */
    0,                                      /* tp_call */
    0,                                      /* tp_str */
    0,                                      /* tp_getattro */
    0,                                      /* tp_setattro */
    0,                                      /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    collector_doc,                          /* tp_doc */
    0,                                      /* tp_traverse */
    0,                                      /* tp_clear */
    0,                                      /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    0,                                      /* tp_iter */
    0,                                      /* tp_iternext */
    collector_methods,                      /* tp_methods */
    0,                                      /* tp_members */
    0,                                      /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    0,                                      /* tp_descr_get */
    0,                                      /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)collector_init,               /* tp_init */
    PyType_GenericAlloc,                    /* tp_alloc */
    PyType_GenericNew,                      /* tp_new */
    PyObject_Del,                           /* tp_free */
};

static PyMethodDef modmethods[] = {
    { NULL, NULL }
};

PyMODINIT_FUNC
init_coverage(void)
{
    PyObject *module, *d;
    module = Py_InitModule3("_coverage", modmethods, "coverage collector");
    if (module == NULL)
	return;
    d = PyModule_GetDict(module);
    if (PyType_Ready(&PyCollector_Type) < 0)
	return;
    PyDict_SetItemString(d, "Collector", (PyObject *)&PyCollector_Type);
}
