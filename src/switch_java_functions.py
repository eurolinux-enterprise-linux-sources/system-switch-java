# switch_java_functions - functions for switching Java alternatives
# Copyright (C) 2007 Red Hat, Inc.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.  If not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 USA.

'''Functions for manipulating the java alternatives.'''

import gettext
import os
import os.path
import re
import sys, traceback

from switch_java_globals import PROGNAME, LOCALE_DIR
COPYRIGHT = 'Copyright (C) 2007 Red Hat, Inc.'
ssj_debug=False
none_root=False

# Internationalization.
gettext.bindtextdomain(PROGNAME, LOCALE_DIR)
gettext.textdomain(PROGNAME)
_ = gettext.gettext

TEXT_MESSAGE = _('''\
display text interface even if graphics display is available\
''')
PARSE_ERROR_MESSAGE = _('''\
An attempt to parse /var/lib/alternatives/java failed.\
''')
NO_JAVA_MESSAGE = _('''\
No supported Java packages were found.  A supported Java package is\
 one that installs a file of the form:

/usr/lib/jvm/jre-$version-$vendor/bin/java

For example, java-1.4.2-gcj-compat is a supported package because it\
 installs:

/usr/lib/jvm/jre-1.4.2-gcj/bin/java\
''')
INSTRUCTION_MESSAGE = _('Select the default Java toolset for the system.')
TITLE_MESSAGE = _('Java Toolset Configuration')
SELECTION_MESSAGE = _('Installed Java Toolsets')
ROOT_MESSAGE = _('''\
The default Java toolset can only be configured by the root user.\
''')
OK_MESSAGE = _('OK')
CLOSE_MESSAGE = _('Close')
CANCEL_MESSAGE = _('Cancel')
JAVA_PATH = '/etc/alternatives/java'

# Module-level globals

ALTERNATIVES = {}
JAVA = {}
JRE = {}
JCE = {}
JAVAC = {}
SDK = {}
PLUGIN = {}
JAVADOCDIR = {}
JAVADOCZIP = {}

class JavaOpenError(Exception):
    '''Raised if the java alternatives configuration is missing.'''
    pass
class JavaParseError(Exception):
    '''Raised if the java alternatives configuration can not be parsed.'''
    pass

def switch_java(java):
    '''Switch alternatives to the specified java.

    java is the directory suffix indicating the java name
    '''
    vendor, version, arch = get_java_split(java)
    # There are problems with the jre_ibm, jre_1.4.2, java_sdk,
    # java_sdk_1.4.2 and libjavaplugin.so alternatives in the JPackage
    # java-1.4.2-ibm and java-1.5.0-ibm packages, but not in the RHEL
    # ones.  We suppress error output from the alternatives commands
    # so that JPackage users won't be alarmed.  The only consequence
    # for them is that the seldom-used /usr/lib/jvm/jre-ibm,
    # /usr/lib/jvm/jre-1.4.2, /usr/lib/jvm/java-1.4.2 and
    # /usr/lib/jvm/java-ibm symlinks will not be updated.  In the case
    # of the plugin, JPackage and Red Hat plugin packages are
    # incompatible anyway, so failing to set an alternative will not
    # cause additional problems.
    suppress = False
    if vendor == 'ibm':
        suppress = True
    _set_alternative('java', JAVA[java])
    _set_alternative('jre_' + vendor, JRE[java], suppress)
    _set_alternative('jre_' + version, JRE[java], suppress)
    _set_alternative('jre_' + version + "_" + vendor, re.sub("/jre$", "", JRE[java].replace("java-", "jre-")), suppress)
    if JCE[java] != None:
        _set_alternative('jce_' + version + '_' + vendor + '_local_policy' + arch,
                         JCE[java])
    if JAVAC[java] != None:
        _set_alternative('javac', JAVAC[java])
        _set_alternative('java_sdk_' + vendor, SDK[java], suppress)
        _set_alternative('java_sdk_' + version, SDK[java], suppress)
        _set_alternative('java_sdk_' + version + "_" + vendor, SDK[java], suppress)
    if PLUGIN[java] != None:
        _set_alternative('libjavaplugin.so' + arch, PLUGIN[java])
    if JAVADOCDIR[java] != None:
        _set_alternative('javadocdir', JAVADOCDIR[java])
    if JAVADOCZIP[java] != None:
        _set_alternative('javadoczip', JAVADOCZIP[java])

def _set_alternative(alternative, value, suppress=False):
    '''Set the alternative to the desired value.

    Invokes /usr/sbin/alternatives --set alternative value.
    '''
    command = '/usr/sbin/alternatives --set ' + alternative + ' ' + value
    if suppress:
        command = command + ' >/dev/null 2>&1'
    _exec(command)

def _exec(commands):
    '''Execute the given string.'''
    if ssj_debug:
        print(commands)
    os.system(commands)

def version_sort_split(i):
    regex = "-+| +|\\.+"
    vendor, version, arch =  get_java_split(i)
    # group by version , vendor
    i = version + " " + vendor + " " + i
    a = re.split(regex, (i).lower())
    return a

def version_sort(i, j):
    a = version_sort_split(i)
    b = version_sort_split(j)
    la = len(a)
    lb = len(b)
    for x in range(0, min(la, lb) - 1):
        aa = a[x]
        bb = b[x]
        try:
            na = int(aa)
            nb = int(bb)
            if na < nb: return  1
            if na > nb: return -1
        except Exception:
            if aa < bb: return  1
            if aa > bb: return -1
    #return la-lb
    #its disputable how to sort jdks wit NVR and without
    return 0

def version_sort_wrapper(i, j):
    return version_sort(i[0],j[0])

def get_java_identifiers(get_alternatives_func=None):
    if get_alternatives_func is None:
        get_alternatives_func = get_alternatives
    java_identifiers = []
    # indicates whether each java_identifier is a jdk or jre
    jdks = []
    best_identifier = None
    alternatives, best = get_alternatives_func('java')
    jre_expression = re.compile('/usr/lib/jvm/jre-([^/]+)/bin/java')
    # Since Java 9, there's no separate jre dir
    jdk_expression = re.compile('/usr/lib/jvm/java-([^/]+)/(jre/)?bin/java')
    best_identifier_index = -1
    for i in range(len(alternatives)):
        alternative = alternatives[i]
        jre_search = jre_expression.search(alternative)
        jdk_search = jdk_expression.search(alternative)
        java = None
        if not jre_search == None:
            java = jre_search.group(1)
            jdks.append(False)
        elif not jdk_search == None:
            java = jdk_search.group(1)
            jdks.append(True)
        else:
            continue
        java_identifiers.append(java)
        if i == best:
            best_identifier_index = len(java_identifiers) - 1
    identifiers_and_jdks = zip(java_identifiers, jdks)
    if len(identifiers_and_jdks) > 0:
        best_identifier = identifiers_and_jdks[best_identifier_index][0]
        identifiers_and_jdks = sorted(identifiers_and_jdks, cmp=version_sort_wrapper)
        initialize_alternatives_dictionaries(identifiers_and_jdks)
        java_identifiers = sorted(java_identifiers, cmp=version_sort)
    if (ssj_debug):
        print(str(ALTERNATIVES))
        print(str(JAVA))
        print(str(JRE))
        print(str(JCE))
        print(str(JAVAC))
        print(str(SDK))
        print(str(PLUGIN))
        print(str(JAVADOCDIR))
        print(str(JAVADOCZIP))
    return java_identifiers, best_identifier

def get_plugin_alternatives(plugin_alternatives, arch):
    try:
        alternatives, best = get_alternatives('libjavaplugin.so' + arch)
        # plugin_expression = re.compile('/usr/lib/jvm/jre-([^/]*)/')
        # all fedora/rhel javas are installed into java-... dirrectory and just 
        # creates (mostly)symlinks jre-... 
        plugin_expression = re.compile('(/usr/lib/jvm/(java|jre)-([^/]*)/)|(/usr/lib.*/IcedTeaPlugin.so.*)')
        for alternative in alternatives:
            java_search = plugin_expression.search(alternative)
            if java_search == None:
                # Skip unrecognized libjavaplugin.so alternative.
                continue
            java = java_search.group(1)
            plugin_alternatives[java] = alternative
    except JavaParseError:
        # Ignore libjavaplugin.so parse errors.
        pass
    except JavaOpenError:
        # No libjavaplugin.so alternatives were found.
        pass
    return plugin_alternatives


def _get_javadocs_alternatives(key, suffix):
    javadocdir_alternatives = {}
    try:
        alternatives, best = get_alternatives(key)
        javadocdir_expression = re.compile('/usr/share/javadoc/java-([^/]*)'+suffix)
        for alternative in alternatives:
            java_search = javadocdir_expression.search(alternative)
            if java_search == None:
                # Skip unrecognized javadocdir alternative.
                continue
            java = java_search.group(1)
            javadocdir_alternatives[java] = alternative
    except JavaParseError:
        # Ignore javadocdir parse errors.
        pass
    except JavaOpenError:
        # No javadocdir alternatives were found.
        pass
    return javadocdir_alternatives

def get_javadocdir_alternatives():
    return _get_javadocs_alternatives('javadocdir', '/api')


def get_javadoczip_alternatives():
    return _get_javadocs_alternatives('javadoczip', '\.zip')

def get_alternatives(master, open_func=open, exists=os.path.exists):
    """Parse all alternatives for `master`.

    Return a tuple (alternatives, index_of_best_alternative).

    open_func is the function invoked to open the file. Defaults to
    the builtin open().

    exists is the function invoked to check that the file
    exists. Defaults to os.path.exists.

    Raise JavaOpenError if alternative file is
    not found. Raise JavaParseError if it can not be parsed.
    """
    try:
        alternative_file = open_func('/var/lib/alternatives/' + master, 'r')
    except IOError:
        raise JavaOpenError

    with alternative_file:
        return _get_alternatives(alternative_file, exists)

def _get_alternatives(alternative_file, exists):
    """Return a tuple (alternatives, index_of_best_alternative)."""
    alternatives = []
    highest_priority = -1
    best = -1
    slave_line_count = 0
    # Skip mode and master symlink lines.
    first_slave_index = 2
    index = first_slave_index
    try:
        lines = alternative_file.readlines()
        # index points to first slave line.
        line = lines[index]
        # Count number of slave lines to ignore.
        while line != '\n':
            index = index + 1
            line = lines[index]
        # index points to blank line separating slaves from target.
        slave_line_count = (index - first_slave_index) / 2
        index = index + 1
        # index points to target.
        while index < len(lines):
            line = lines[index]
            # Accept trailing blank lines at the end of the file.
            # Debian's update-alternatives requires this.
            if line == '\n':
                break
            # Remove newline.
            alternative = line[:-1]
            # Exclude alternative targets read from
            # /var/lib/alternatives/$master that do not exist in the
            # filesystem.  This inconsistent state can be the result
            # of an rpm post script failing.
            append = False
            if exists(alternative):
                append = True
                alternatives.append(alternative)
                if (ssj_debug):
                    print("found: "+str(alternative))
            index = index + 1
            # index points to priority.
            line = lines[index]
            if append:
                ss = line[:-1];
                # alternatives with --family swithch are saved as @family@priority
                if ("@" in ss):
                    splitted = ss.split("@");
                    priority = int(splitted[len(splitted)-1])
                else:
                    priority = int(ss)
                if priority > highest_priority:
                    highest_priority = priority
                    best = len(alternatives) - 1
            index = index + 1
            # index points to first slave.
            index = index + slave_line_count
            # index points to next target or end-of-file.
    except:
        if (ssj_debug):
            traceback.print_exc(file=sys.stdout)    
        raise JavaParseError
    return alternatives, best

def initialize_alternatives_dictionaries(java_identifiers_and_jdks, path_exists=None):
    if path_exists is None:
        path_exists = os.path.exists
    plugin_alternatives = get_plugin_alternatives({}, '')
    javadocdir_alternatives = get_javadocdir_alternatives()
    javadoczip_alternatives = get_javadoczip_alternatives()
    arch_found = False
    for (java, is_jdk) in java_identifiers_and_jdks:
        vendor, version, arch = get_java_split(java)
        if is_jdk:
            # since Java 9, there's no separate jre subdir
            candidate = '/usr/lib/jvm/java-' + java + '/jre/bin/java'
            if path_exists(candidate):
                JAVA[java] = candidate
            else:
                JAVA[java] = '/usr/lib/jvm/java-' + java + '/bin/java'
        else:
            JAVA[java] = '/usr/lib/jvm/jre-' + java + '/bin/java'
        # Command-to-alternative-name map to set default alternative.
        ALTERNATIVES[JAVA[java]] = java
        if is_jdk:
            # since Java 9, there's no separate jre subdir
            candidate = '/usr/lib/jvm/java-' + java + '/jre'
            if path_exists(candidate):
                JRE[java] = candidate
            else:
                JRE[java] = '/usr/lib/jvm/java-' + java
        else:
            JRE[java] = '/usr/lib/jvm/jre-' + java
        jce = '/usr/lib/jvm-private/java-' + java\
              + '/jce/vanilla/local_policy.jar'
        if path_exists(jce):
            JCE[java] = jce
        else:
            JCE[java] = None
        javac = '/usr/lib/jvm/java-' + java + '/bin/javac'
        if os.path.exists(javac):
            JAVAC[java] = javac
            SDK[java] = '/usr/lib/jvm/java-' + java
        else:
            JAVAC[java] = None
            SDK[java] = None
        if arch != '' and not arch_found:
            plugin_alternatives = get_plugin_alternatives(plugin_alternatives,
                                                          arch)
            arch_found = True
        PLUGIN[java] = None
        if java in plugin_alternatives:
            PLUGIN[java] = plugin_alternatives[java]
        for v in plugin_alternatives:
            if (str(plugin_alternatives[v]).find('IcedTeaPlugin.so')>=0 and str(java).find('openjdk')>=0):
                 PLUGIN[java]=plugin_alternatives[v]
            else:
                if (plugin_alternatives[v].find(java.split('/')[0])>=0):
                    PLUGIN[java] = plugin_alternatives[v]
        # javadoc is noarch
        archlesjava=java.replace(arch,"")
        JAVADOCDIR[java] = None
        if archlesjava in javadocdir_alternatives:
            JAVADOCDIR[java] = javadocdir_alternatives[archlesjava]
        JAVADOCZIP[java] = None
        if archlesjava in javadoczip_alternatives:
            JAVADOCZIP[java] = javadoczip_alternatives[archlesjava]

def get_default_java_command(path=JAVA_PATH):
    '''Return the default java command (default is '/etc/alternatives/java')'''
    if os.path.exists(path) and os.path.islink(path):
        return os.readlink(path)
    else:
        return None

def get_pretty_names(alternative_names):
    '''Return a dictionary that maps each item in the input list to the pretty string representation.

    See get_pretty_name for more information'''
    pretty_names = {}
    for java in alternative_names:
        pretty_names[java] = get_pretty_name(java)
    return pretty_names

def get_pretty_name(java):
    '''Return a pretty name of the form "formatted-name version optional-arch"'''
    debugPackage = False;
    if ("-debug" in java):
        debugPackage = True;
    java = java.replace("-debug", "")
    vendor, version, arch = get_java_split(java)
    if vendor in ['sun', 'blackdown', 'oracle']:
        pretty_name = vendor.capitalize() + ' ' + version
    elif vendor == 'icedtea':
        pretty_name = 'IcedTea' + ' ' + version
    elif vendor == 'openjdk':
        pretty_name = 'OpenJDK' + ' ' + version
    else:
        pretty_name = vendor.upper() + ' ' + version
    versionsplit = java.split('-')

    #handling of  legacy '1.7.0-openjdk' or '1.5.0-sun.x86_64'
    if "." not in versionsplit[len(versionsplit)-1]:
        return pretty_name
    nvr = ''
    if len(versionsplit) > 2:
        nvr = nvr + versionsplit[2]
    if len(versionsplit) > 3:
        nvr = nvr + '-' + versionsplit[3]
    if nvr == '' and len(arch) > 1:
        if arch.startswith("."):
            nvr = arch[1:]
        else:
            nvr = arch
    if (debugPackage):
        pretty_name = pretty_name + ' (' + nvr + " DEBUG"+')'
    else:
        pretty_name = pretty_name + ' (' + nvr + ')'

    return pretty_name

def get_java_split(java):
    '''Return the tuple (version, vendor, arch) for a directory suffix (1.5.0-gcj.x86_64)
    arch is empty if the directory suffix does not contain arch.'''
    if ("-debug" in java):
        java=java.replace("-debug","")
    vendor_arch = java.split('-')
    if "." not in vendor_arch[len(vendor_arch)-1]:
        return vendor_arch[1], vendor_arch[0], ''
    vendor_arch = java.split('-')[1].split('.')
    vendor = vendor_arch[0]
    arch = ''
    #path can be full of dots - as in jdk>6 full version is included
    vendor_version_arch = java.split('.')
    if len(vendor_version_arch) > 1:
        arch = '.' + vendor_version_arch[len(vendor_version_arch)-1]
    version = java.split('-')[0]
    return vendor, version, arch
