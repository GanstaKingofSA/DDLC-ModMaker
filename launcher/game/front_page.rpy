﻿# Copyright 2004-2019 Tom Rothamel <pytom@bishoujo.us>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

define PROJECT_ADJUSTMENT = ui.adjustment()

init python:

    import os
    import subprocess

    class OpenDirectory(Action):
        """
        Opens `directory` in a file browser. `directory` is relative to
        the project root.
        """

        alt = _("Open [text] directory.")

        def __init__(self, directory, absolute=False):
            if absolute:
                self.directory = directory
            else:
                self.directory = os.path.join(project.current.path, directory)

        def get_sensitive(self):
            return os.path.exists(self.directory)

        def __call__(self):

            try:
                directory = renpy.fsencode(self.directory)

                if renpy.windows:
                    os.startfile(directory)
                elif renpy.macintosh:
                    subprocess.Popen([ "open", directory ])
                else:
                    subprocess.Popen([ "xdg-open", directory ])

            except:
                pass

    # Used for testing.
    def Relaunch():
        renpy.quit(relaunch=True)

screen front_page:
    frame:
        alt ""

        style_group "l"
        style "l_root"

        has hbox

        # Projects list section - on left.

        frame:
            style "l_projects"
            xmaximum 300
            right_margin 2

            top_padding 20
            bottom_padding 26

            side "t c b":

                window style "l_label":

                    has hbox:
                        xfill True

                    text _("Mod Projects:") style "l_label_text" size 36 yoffset 10

                    textbutton _("refresh"):
                        xalign 1.0
                        yalign 1.0
                        yoffset 5
                        style "l_small_button"
                        action project.Rescan()
                        right_margin HALF_INDENT

                side "c r":

                    viewport:
                        yadjustment PROJECT_ADJUSTMENT
                        mousewheel True
                        use front_page_project_list

                    vbar:
                        style "l_vscrollbar"
                        adjustment PROJECT_ADJUSTMENT

                vbox:
                    add HALF_SPACER
                    add SEPARATOR
                    add HALF_SPACER

                    hbox:
                        xfill True

                        textbutton _("+ Create New Project"):
                            left_margin (HALF_INDENT)
                            action Jump("new_project")

        # Project section - on right.

        if project.current is not None:
            use front_page_project

    if project.current is not None:
        if persistent.projects_directory is None:
            python:
                launch = "error"
            pass
        else:
            python:
                ver = persistent.projects_directory + '/' + project.current.name + '/renpy-version.txt'
                try:
                    with open(ver) as f:
                        if f.readline() < "7":
                            launch = False
                        else:
                            launch = True
                except IOError:
                    launch = "error"
        if launch == False:
            textbutton _("DDMMaker 6.99.12.4 Needed"):
                xalign 0.95
                yalign 0.83
                style "l_button"
                action NullAction()
                right_margin HALF_INDENT
        elif launch == True or project.current.name == "launcher":
            textbutton _("Launch Mod") action project.Launch() style "l_right_button"
            key "K_F5" action project.Launch()
        else:
            textbutton _("Cannot determine version."):
                xalign 0.95
                yalign 0.83
                style "l_button"
                action Jump('version_error')
                right_margin HALF_INDENT
        #textbutton _("Launch Project") action project.Launch() style "l_right_button"
        
# This is used by front_page to display the list of known projects on the screen.
screen front_page_project_list:

    $ projects = project.manager.projects
    $ templates = project.manager.templates

    vbox:

        if templates and persistent.show_templates:

            for p in templates:

                textbutton _("[p.name!q] (template)"):
                    action project.Select(p)
                    alt _("Select project [text].")
                    style "l_list"

            null height 12

        if projects:

            for p in projects:

                textbutton "[p.name!q]":
                    action project.Select(p)
                    alt _("Select project [text].")
                    style "l_list"

            null height 12

# This is used for the right side of the screen, which is where the project-specific
# buttons are.
screen front_page_project:

    $ p = project.current
    $ version = renpy.version()

    window:

        has vbox
        label _("Current Ren'Py Version: [version!q]") style "l_alternate"
        frame style "l_label":
            has hbox xfill True
            text "[p.display_name!q]" style "l_label_text"
            label _("Active Mod") style "l_alternate"

        grid 2 1:
            xfill True
            spacing HALF_INDENT

            vbox:

                label _("Open Folder") style "l_label_small"

                frame style "l_indent":
                    has vbox

                    textbutton _("game") action OpenDirectory("game")
                    textbutton _("base") action OpenDirectory(".")
                    textbutton _("images") action OpenDirectory("game/images")
                    textbutton _("audio") action OpenDirectory("game/audio")
                    textbutton _("mod_assets") action OpenDirectory("game/mod_assets")
                    textbutton _("gui") action OpenDirectory("game/gui")
                    # textbutton _("save") action None style "l_list"

            vbox:
                if persistent.show_edit_funcs:

                    label _("Edit File") style "l_label_small"

                    frame style "l_indent":
                        has vbox

                        textbutton "script.rpy" action editor.Edit("game/script.rpy", check=True)
                        textbutton "options.rpy" action editor.Edit("game/options.rpy", check=True)
                        textbutton "gui.rpy" action editor.Edit("game/gui.rpy", check=True)
                        textbutton "definitions.rpy" action editor.Edit("game/definitions.rpy", check=True)
                        textbutton "screens.rpy" action editor.Edit("game/screens.rpy", check=True)

                        if editor.CanEditProject():
                            textbutton _("Open project") action editor.EditProject()
                        else:
                            textbutton _("All script files") action editor.EditAll()

        add SPACER

        label _("Options") style "l_label_small"

        grid 2 1:
            xfill True
            spacing HALF_INDENT

            frame style "l_indent":
                has vbox

                textbutton _("Navigate Script") action Jump("navigation")
                textbutton _("Check Script for Errors") action Jump("lint")
                textbutton _("Delete Persistent") action Jump("rmpersistent")
                textbutton _("Force Recompile") action Jump("force_recompile")
                if project.current.name != "launcher":
                    textbutton _("Set Version") action Jump("set_version")

                # textbutton "Relaunch" action Relaunch

            frame style "l_indent":
                has vbox

                if ability.can_distribute:
                    textbutton _("Build Mod") action Jump("build_distributions")
                if project.current.name != "launcher":
                    textbutton _("Build Mod for Android") action Jump("android")
                    textbutton _("Generate Translations") action Jump("translate")
                    textbutton _("Extract Dialogue") action Jump("extract_dialogue")
                    textbutton _("Delete Project") action Jump("delete_folder")
                
label main_menu:
    return

label start:
    show screen bottom_info
    $ dmgcheck()

label front_page:
    call screen front_page
    jump front_page


label lint:
    python hide:

        interface.processing(_("Checking script for potential problems..."))
        lint_fn = project.current.temp_filename("lint.txt")

        project.current.launch([ 'lint', lint_fn ], wait=True)

        e = renpy.editor.editor
        e.begin(True)
        e.open(lint_fn)
        e.end()

    jump front_page

label rmpersistent:

    python hide:
        interface.processing(_("Deleting persistent data..."))
        project.current.launch([ 'rmpersistent' ], wait=True)

    jump front_page

label force_recompile:

    python hide:
        interface.processing(_("Recompiling all rpy files into rpyc files..."))
        project.current.launch([ 'compile' ], wait=True)

    jump front_page

label version_error:
    python:
        interface.info(_("This project is unavailable to launch as this is either a non-DDLC mod/game or is missing 'renpy-version.txt'"), _("Please check if 'renpy-version.txt' exists or run normal Ren'Py for non-DDLC games/mods."),)
        renpy.jump('front_page')

label set_version:
    python hide:
        ver = persistent.projects_directory + '/' + project.current.name + '/renpy-version.txt'
        try:
            with open(ver) as f:
                if f.readline() < "7":
                    delete_response = interface.input(
                        _("Warning"),
                        _("This mod is set to Ren'Py 6 Mode. If you change this, it may result in a improperly packaged mod. Are you sure you want to proceed? Type either Yes or No."),
                        filename=False,
                        cancel=Jump("front_page"))

                    delete_response = delete_response.strip()

                    if not delete_response:
                        interface.error(_("The operation has been cancelled."))

                    response = delete_response

                    if response == "No" or response == "no":
                        interface.error(_("The operation has been cancelled."))
                    elif response == "Yes" or response == "yes":
                        f = open(ver,'w+')
                        f.write("7")
                        interface.info(_("Set the Ren'Py mode version to Ren'Py 7."))
                    else:
                        interface.error(_("Invalid Input. Please try again."))
                elif f.readline() == "7":
                    interface.error(_("The Ren'Py mode version is already set to Ren'Py 7."))
                else:
                    f = open(ver,'w+')
                    f.write("7")
                    interface.info(_("Set the Ren'Py mode version to Ren'Py 7."))
        except IOError:
            f = open(ver,'w+')
            f.write("7") 
            interface.info(_('A file named `renpy-version.txt` has been created in the base directory.'), _("Do not delete this file as it is needed to determine which version of Ren'Py it uses for building your mod."))
    return