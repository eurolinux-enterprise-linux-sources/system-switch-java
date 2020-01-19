SUBDIRS = po

dist_sbin_SCRIPTS = system-switch-java

nobase_dist_sysconf_DATA = pam.d/$(PACKAGE) security/console.apps/$(PACKAGE)
nobase_dist_data_DATA = pixmaps/$(PACKAGE).png
desktopdir = $(datadir)/applications
nodist_desktop_DATA = $(PACKAGE).desktop

pythondir = $(datadir)/$(PACKAGE)
python_PYTHON = switch_java_functions.py switch_java_gui.py switch_java_tui.py
dist_python_DATA = $(PACKAGE).glade

$(PACKAGE).desktop: $(PACKAGE).desktop.in
	@INTLTOOL_MERGE@ --desktop-style $(srcdir)/po $< $@

EXTRA_DIST = switch_java_functions.py.in $(PACKAGE).desktop.in COPYING.icon

DISTCLEANFILES = \
	$(PACKAGE).desktop

install-exec-local:
	$(mkinstalldirs) $(DESTDIR)$(bindir)
	ln -sf consolehelper $(DESTDIR)$(bindir)/$(PACKAGE)
