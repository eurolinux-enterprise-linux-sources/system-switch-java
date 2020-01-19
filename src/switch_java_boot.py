# switch_java_boot - the Java toolset switcher frontend
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

import os
import os.path
import sys
from optparse import OptionParser

from switch_java_globals import VERSION
import switch_java_functions
from switch_java_functions import *

def main():
    parser = OptionParser(version=VERSION)
    parser.add_option('-t', '--text', action='store_true',
                      dest='force_text', default=False, help=TEXT_MESSAGE)
    parser.add_option('-d', '--debug', action='store_true',
                      dest='force_debug', default=False, help="")
    parser.add_option('-r', '--non-root', action='store_true',
                      dest='none_root', default=False, help="")
    options, args = parser.parse_args()
    show_gui = False
    if options.force_debug:
        switch_java_functions.ssj_debug=True
    if options.none_root:
        switch_java_functions.none_root = True
    if not options.force_text:
        try:
            if os.environ['DISPLAY'] != '':
                show_gui = True
        except KeyError:
            pass
    if os.getuid() != 0 and not switch_java_functions.none_root:
        show_dialog(show_gui, ROOT_MESSAGE)
        sys.exit(1)
    java_identifiers = []
    best_identifier = ''
    # Get list of identifiers for installed Java environments.
    try:
        java_identifiers, best_identifier = get_java_identifiers()
    except JavaParseError:
        show_dialog(show_gui, PARSE_ERROR_MESSAGE)
        sys.exit(1)
    except JavaOpenError:
        pass
    if len(java_identifiers) == 0:
        show_dialog(show_gui, NO_JAVA_MESSAGE)
        sys.exit(1)
    # Get default Java alternative.  Default to best alternative if no
    # recognized default is currently set.  That is, if
    # /etc/alternatives/java does not point to a recognized Java
    # alternative, point it to the best alternative.  This will
    # override a deliberate custom setting of /etc/alternatives/java
    # but that's probably the right thing to do for an easy-to-use GUI
    # tool.  In almost all cases /etc/alternatives/java pointing to
    # something unrecognized will represent an error condition that
    # should be fixed, rather than a custom setting.
    default_java_command = get_default_java_command()
    if default_java_command not in JAVA.values():
        default_java_command = JAVA[best_identifier]
    default_java = ALTERNATIVES[default_java_command]
    pretty_names = get_pretty_names(java_identifiers)
    if show_gui:
        from switch_java_gui import mainDialog
    else:
        from switch_java_tui import mainDialog
    mainDialog().main(java_identifiers, default_java, pretty_names)

def show_dialog(show_gui, message):
    if show_gui:
        from switch_java_gui import mainDialog
    else:
        from switch_java_tui import mainDialog
    mainDialog().show_dialog(message)
