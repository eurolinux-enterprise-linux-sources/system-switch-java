Name: system-switch-java
Version: 1.1.5
Release: 11%{?dist}
Summary: A tool for changing the default Java toolset

%define baseurl https://fedorahosted.org

Group: Applications/System
License: GPLv2+ and BSD
URL: %{baseurl}/%{name}
Source0: %{baseurl}/releases/s/y/system-switch-java/%{name}-%{version}.tar.gz
# Patch is upstream but not in a release https://fedorahosted.org/system-switch-java/changeset/80
Patch0: new-jdk-paths.patch
Patch1: jre-java.patch
Patch2: disabledUnderline.patch
Patch3: tuiWidth.patch
Patch4: version-fix.patch
Patch5: fix-arch-detection.patch

BuildArch: noarch

BuildRequires: desktop-file-utils
BuildRequires: gettext
BuildRequires: intltool
BuildRequires: python-devel

Requires: chkconfig
Requires: libglade2
Requires: newt-python
Requires: pygtk2
Requires: pygtk2-libglade
Requires: python
Requires: usermode
Requires: usermode-gtk

%description
The system-switch-java package provides an easy-to-use tool to select
the default Java toolset for the system.

%prep
%setup -q
#%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1

%build
%configure
make %{?_smp_mflags}

%install
make DESTDIR=%{buildroot} install
%find_lang %{name}
desktop-file-install \
  --dir %{buildroot}%{_datadir}/applications \
  %{buildroot}%{_datadir}/applications/%{name}.desktop


%files -f %{name}.lang
%defattr(-,root,root)
%doc AUTHORS README COPYING COPYING.icon
%{_bindir}/%{name}
%{_sbindir}/%{name}
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/switch_java_functions.py*
%{_datadir}/%{name}/switch_java_gui.py*
%{_datadir}/%{name}/switch_java_tui.py*
%{_datadir}/applications/%{name}.desktop
%{_datadir}/pixmaps/%{name}.png
%{_datadir}/%{name}/system-switch-java.glade
%config(noreplace) /etc/pam.d/%{name}
%config(noreplace) /etc/security/console.apps/%{name}

%changelog
* Thu Mar 27 2014 Omair Majid <omajid@redhat.com> - 1.1.5-11
- Detect arch for newer-style directory names correctly
- Resolves: rhbz#1078313

* Tue Mar 11 2014 Jiri Vanek <jvanek@redhat.com> - 1.1.5-10
- Renamed (to baseurl) url macro to prevent shadowing
- Added BSD license to list of Licenses
 - (COPYING.icon says it's a 2-clause BSD license)
- removed buildroot definition and manual removing of it
- Resolves: rhbz#1070976

* Tue Mar 04 2014 Omair Majid <omajid@redhat.com> - 1.1.5-9
- Remove libuser-python dependency
- Update to work with newer alternatives
 - added new-jdk-paths.patch
 - this patch is disabled, untill more work is done in upstream
- Resolves: rhbz#1070976

* Tue Oct 25 2011 Deepak Bhole <dbhole@redhat.com> 1.1.5-5
- Resolves: rhbz# 745457
- Added new patch (3/version-fix.patch) to fix version

* Wed Aug 17 2011 Jiri Vanek <jvanek@redhat.com> - 1.1.5-4
- added jre-java patch to work corectly with java directories and not
  just with  jre  symlinks
  backward compatibility preserved
- added correct recognition of icedtea-web plugin
- added disabledUnderline patch
- added tuiWidth patch
- Resolves: rhbz#731039
- Resolves: rhbz#725718


* Tue Feb 01 2011 Deepak Bhole <dbhole@redhat.com> - 1.1.5-2
- Renamed url macro to prevent shadowing

* Wed Jan 05 2011 Deepak Bhole <dbhole@redhat.com> - 1.1.5-1
- Resolves: rhbz#663322
- Sync with F14:
  - Update to 1.1.5 which fixes rhbz 493898 and adds more translations

* Fri Apr 18 2008 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.1.2-2
- Fix handling of broken primary java symlink.
- Resolves: rhbz#404331

* Mon Apr 14 2008 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.1.2-1
- Import system-switch-java 1.1.2.
- Remove patches.
- Resolves: rhbz#442399
- Resolves: rhbz#404331

* Tue Jul 24 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.1.0-2
- Tolerate trailing newlines in alternatives file.
- Handle Sun plugin alternative.
- Do not use desktop-file-install.
- Resolves: rhbz#195649

* Tue Jun 27 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.1.0-1
- Import system-switch-java 1.1.0.
- Merge gui subpackage into base package.
- Resolves: rhbz#195649

* Tue Jan 23 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.0.0-1
- Initial release.
