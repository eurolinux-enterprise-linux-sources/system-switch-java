# switch_java_gui - the Java toolset switcher GUI
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

import gtk
import gtk.glade
from switch_java_functions import *

class mainDialog:
    def __init__(self):
        pass

    def main(self, java_identifiers, default_java, pretty_names):
        # Initialize UI.
        xml = gtk.glade.XML('/usr/share/system-switch-java/'
                            + 'system-switch-java.glade',
                            None, domain=PROGNAME)
        self.dialog = xml.get_widget('dialog')
        self.dialog.set_title(TITLE_MESSAGE)
        radio_vbox = xml.get_widget('radio-vbox')
        xml.get_widget('instruction-label').set_text(INSTRUCTION_MESSAGE)
        xml.get_widget('selection-label').set_markup('<b>'
                                                     + SELECTION_MESSAGE
                                                     + '</b>')
        ok_button = xml.get_widget('ok-button')
        # Initialize alternatives list.
        self.radio_buttons = {}
        self.alternatives = {}
        for java in java_identifiers:
            if len(self.radio_buttons) == 0:
                self.radio_buttons[java] = gtk.RadioButton(None,
                                                           pretty_names[java])
                group_button = self.radio_buttons[java]
            else:
                self.radio_buttons[java] = gtk.RadioButton(group_button,
                                                           pretty_names[java])
            radio_vbox.pack_start(self.radio_buttons[java], False, False, 0)
            self.radio_buttons[java].show()
            self.radio_buttons[java].connect("toggled", lambda *x:
                                             ok_button.set_sensitive(True))
            self.alternatives[self.radio_buttons[java]] = java
        # Show default alternative as currently selected and give it
        # keyboard focus.
        self.radio_buttons[default_java].set_active(True)
        self.radio_buttons[default_java].grab_focus()
        ok_button.connect('clicked', self.ok_button_clicked)
        ok_button.set_sensitive(False)
        xml.get_widget('cancel-button').connect('clicked',
                                                self.cancel_button_clicked)
        self.dialog.connect('delete-event', self.dialog_delete_event)
        self.dialog.connect('hide', gtk.main_quit)
        self.dialog.set_icon_from_file('/usr/share/pixmaps/'
                                       + 'system-switch-java.png')
        self.dialog.show()
        gtk.main()

    def dialog_delete_event(self, *args):
        gtk.main_quit()

    def ok_button_clicked(self, button):
        for radio_button in self.radio_buttons.values():
            if radio_button.get_active():
                switch_java(self.alternatives[radio_button])
                break
        self.dialog.hide()
        gtk.main_quit()

    def cancel_button_clicked(self, button):
        self.dialog.hide()
        gtk.main_quit()

    def show_dialog(self, message):
        dialog = gtk.MessageDialog(None,
                                   gtk.DIALOG_MODAL
                                   | gtk.DIALOG_DESTROY_WITH_PARENT,
                                   gtk.MESSAGE_INFO,
                                   gtk.BUTTONS_OK,
                                   message)
        dialog.set_title(TITLE_MESSAGE)
        dialog.set_icon_from_file('/usr/share/pixmaps/system-switch-java.png')
        dialog.run()
        dialog.destroy()
