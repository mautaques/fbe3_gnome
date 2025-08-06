# main.py
#
# Copyright 2024 Cabral
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import gi
import os

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw
from .window import FbeWindow
cur_path = os.path.realpath(__file__)
base_path = os.path.dirname(os.path.dirname(cur_path))
sys.path.insert(1, base_path)


class FbeApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id='com.lapas.Fbe',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about_action, ['<Ctrl>m'])
        self.set_accels_for_action('win.new-project', ['<Ctrl>n'])
        self.set_accels_for_action('win.open-project', ['<Ctrl>o'])
        self.set_accels_for_action('win.rename-project', ['<Ctrl>r'])
        self.set_accels_for_action('win.close-project', ['<Ctrl>d'])
        self.set_accels_for_action('win.new-app', ['<Ctrl><Shift>n'])
        self.set_accels_for_action('win.rename-app', ['F2'])
        self.set_accels_for_action('win.delete-app', ['F3'])
        self.set_accels_for_action('win.show-help-overlay', ['<Ctrl><Shift>question'])
        self.set_accels_for_action('win.system-information', ['<Ctrl>g'])
        self.set_accels_for_action('win.system-configuration', ['<Ctrl>h'])
        self.set_accels_for_action('win.apps-swipe-left', ['<Ctrl>p'])
        self.set_accels_for_action('win.apps-swipe-right', ['<Ctrl>a'])
        self.set_accels_for_action('win.save-project', ['<Ctrl>s'])
        self.set_accels_for_action('win.add-type', ['<Ctrl><Alt>n'])
        self.set_accels_for_action('win.last-page', ['<Ctrl>b'])
        self.set_accels_for_action('win.export-project', ['<Ctrl>e'])

    def do_activate(self):
        """
        Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.props.active_window
        if not win:
            win = FbeWindow(application=self)
        win.present()

    def on_about_action(self, widget, _):
        """Callback for the app.about action."""
        about = Adw.AboutWindow(
            transient_for=self.props.active_window,
            application_name='Function Block Environment 3',
            application_icon='fbe',
            developer_name='Claudinei Cabral, Mauricio Martins Taques Filho',
            version='0.2.0',
            comments="An application for modelling function blocks based on IEC 61499",
            license_type=Gtk.License.GPL_3_0,
            developers=['Cabral, Mauricio'],
            copyright='© 2024 GASR'
        )
        about.present()

    def create_action(self, name, callback, shortcuts=None):
        """
        Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
            activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version):
    """The application's entry point."""
    app = FbeApplication()
    return app.run(sys.argv)
