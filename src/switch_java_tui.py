# switch_java_tui - the Java toolset switcher TUI
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

'''The text UI for switching the java toolet'''

from snack import *
from switch_java_functions import *

class mainDialog:
    def __init__(self):
        pass

    def main(self, java_identifiers, default_java, pretty_names):
        # Initialize UI.
        screen = SnackScreen()
        text = TextboxReflowed(60, INSTRUCTION_MESSAGE)
        java_list = Listbox(5, width=60, scroll=1, returnExit=1)
        label = Label(SELECTION_MESSAGE)
        # Initialize alternatives list.
        for java in java_identifiers:
            java_list.append(pretty_names[java], java)
        # Show default alternative as currently selected and give it
        # keyboard focus.
        java_list.setCurrent(default_java)
        buttons = (CLOSE_MESSAGE, CANCEL_MESSAGE)
        buttonbar = ButtonBar(screen,buttons)
        grid = GridForm(screen, TITLE_MESSAGE, 1, 5)
        grid.add(text, 0, 0)
        grid.add(label, 0, 1, (0, 1, 0, 0))
        grid.add(java_list, 0, 2, (0, 1, 0, 0))
        grid.add(buttonbar, 0, 3, (0, 1, 0, 0))
        result = grid.runOnce()
        screen.finish()
        bbp = buttonbar.buttonPressed(result)
        if ssj_debug:
            print("  bbpr    " + str(bbp))
            print("  message " + CANCEL_MESSAGE)
            print("  result  " + str(result))
        if bbp == "cancel":
            print("Not saving!")
        else:
            switch_java(java_list.current())

    def show_dialog(self, message):
        screen = SnackScreen()
        button = Button(OK_MESSAGE)
        text = TextboxReflowed(40, message + '\n\n')
        grid = GridFormHelp(screen, TITLE_MESSAGE, None, 1, 2)
        grid.add(text, 0, 0)
        grid.add(button, 0, 1)
        result = grid.runOnce()
        screen.finish()
