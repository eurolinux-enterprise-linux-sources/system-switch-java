AC_INIT([system-switch-java], [1.1.7.1], [dbhole@redhat.com], ,
        [https://fedorahosted.org/system-switch-java/])

AM_INIT_AUTOMAKE([no-dist-gzip dist-xz -Wall])

GETTEXT_PACKAGE=system-switch-java
AC_SUBST([GETTEXT_PACKAGE])
AM_GLIB_GNU_GETTEXT
IT_PROG_INTLTOOL

AM_PATH_PYTHON

AC_CONFIG_FILES([
    Makefile
    po/Makefile.in
    switch_java_globals.py
    system-switch-java
])

AC_OUTPUT
