# Copyright 2024 Liquid Glass
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import filedialog
import os
import subprocess

# Custom libraries
import directory_movements
import utils.truncate
import utils.clean as sanitize

# App version
app_version = "v1.0.1 (Catalyst)"

# Backend stuff (e.g. refresh GUI to show current path, etc)
path_history = []

# This array is used in update_contents()
button_ids = []

# A variable to show files being hidden
show_hidden_files = False

# Make a class for custom colors based off hex values
class Colors:
    dark_grey = "#333333"

# Create instance of custom colors
custom_colors = Colors()

def home_path() -> str:
    try:
        with open("config/home-path.txt", "r") as path_file:
            original_home_path = path_file.read()
            new_home_path = original_home_path.replace("\\", "/")
            clean_home_path = sanitize.clean_newline(new_home_path)
            return clean_home_path
    except FileNotFoundError:
        return fallback_home_path()

def fallback_home_path() -> str:
    shortened_downloads_path = "~/Downloads"
    downloads_home_path = os.path.expanduser(shortened_downloads_path)
    return downloads_home_path

def open_path(path):
    if os.path.isdir(path):
        current_path.set(path)
        update_contents()
    else:
        # Checks the type of file and display the necessary apps
        file_type = directory_movements.file_sort_type(path)
        if file_type == "part-file":
            application_options(file_type, path)
        if file_type == "laser-file":
            application_options(file_type, path)

# Delete buttons on canvas
def delete_buttons_canvas():
    for button_id in button_ids:
        canvas.delete(button_id)

# Get the values for the centre of the canvas
def centre_of_canvas():
    canvas.update()
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    centre_x = canvas_width // 2
    centre_y = canvas_height //2
    return centre_x, centre_y, canvas_width, canvas_height

# Define scrolling step on canvas
def canvas_scrolling(event):
    if canvas.bbox("all")[3] > canvas.winfo_height():
        canvas.yview_scroll(-1 * (event.delta // 120), "units")

# Update scroll region
def update_scroll_region(event=None):
    # Forcing canvas to update to see any pending events
    canvas.update_idletasks()
    # Set max scrolling based on items on canvas
    canvas.configure(scrollregion=canvas.bbox("all"))
    # Update scrollbar scaling
    scrollbar.config(command=canvas.yview)

# Check if the file has been opened and copied to .complete folder
def opened_file_status(path, item) -> bool:
    for root, dirs, copied_files in os.walk(path + "/" + ".complete"):
        if item in copied_files:
            return True

"""
Check if the filename extension has a format that is whitelisted
in config files
"""
def format_whitelisted(item) -> bool:
    # Set initial whitelisted status for a format
    no_whitelisted_format = True

    with open("config/part-file-formats.txt", "r") as part_file_whitelists:
        part_file_formats = part_file_whitelists.read()
        clean_part_file_formats = sanitize.clean_newline(part_file_formats)
        part_formats_array = clean_part_file_formats.split(",")
        for this_part_format in part_formats_array:
            if item.endswith(this_part_format):
                no_whitelisted_format = False
        
    with open("config/laser-file-formats.txt", "r") as laser_file_whitelists:
        laser_file_formats = laser_file_whitelists.read()
        clean_laser_file_formats = sanitize.clean_newline(laser_file_formats)
        laser_formats_array = clean_laser_file_formats.split(",")
        for this_laser_format in laser_formats_array:
            if item.endswith(this_laser_format):
                no_whitelisted_format = False

    return no_whitelisted_format

# Checks if an item has a notation that makes it special)
def check_special_notations(item) -> bool:
    if item.startswith("."):
        return True
    elif item.endswith("~"):
        return True
    else:
        return False

def update_contents():
    # Clear current content
    delete_buttons_canvas()

    # Get current path and items from the path
    try:
        path = current_path.get()
        paths = os.listdir(path)
    except FileNotFoundError:
        # If path cannot be found, use Downloads folder as a fallback
        path = fallback_home_path()
        paths = os.listdir(path)

    # Create buttons for each item in path
    button_position = 0
    for item in paths:
        complete_status = opened_file_status(path, item)
        if complete_status == True and show_hidden_files == False:
            continue

        special_item = check_special_notations(item)
        if special_item == True and show_hidden_files == False:
            continue

        item_path = os.path.join(path, item)
        no_whitelist_format = format_whitelisted(item)
        if os.path.isdir(item_path) == False:
            if no_whitelist_format == True and show_hidden_files == False:
                continue
        
        item_name = utils.truncate.truncate_text(item)
        button = tk.Button(canvas, text=item_name,
                           command=lambda path=item_path: open_path(path))
        centre_x, centre_y, canvas_width, canvas_height = centre_of_canvas()
        button_ids.append(canvas.create_window(centre_x, button_position*30,
                                               window=button, anchor="center"))
        button_position += 1

    # Bind canvas resizing to update scrollbar and scroll region
    canvas.bind("<Configure>", update_scroll_region)
    update_scroll_region()

# Executes app based on user choice
def run_application(current_frame, exe_name, path):
    subprocess.Popen([exe_name, path], shell=True)
    directory_movements.copy_to_complete(path)
    update_contents()
    current_frame.destroy()

# Open File Manager (e.g. Explorer, Nautilus, etc)
def open_file_manager():
    with open("config/file-manager-command.txt","r") as file_manager_command:
        open_command = file_manager_command.read()
        clean_open_manager_command = sanitize.clean_newline(open_command)
    file_manager_path = current_path.get()
    os.system(clean_open_manager_command + " " + file_manager_path)

def list_hidden_files():
    global show_hidden_files
    hidden_status = show_hidden_files
    if hidden_status == False:
        show_hidden_files = True
    elif hidden_status == True:
        show_hidden_files = False
    update_contents()

# Deletes entry from URL bar
def clear_url_bar():
    url_entry.delete(0, tk.END)

# Settings
def config_home_path():
    new_dir_path = filedialog.askdirectory()
    if new_dir_path:
        with open("config/home-path.txt", "w") as home_path_config:
            home_path_config.write(new_dir_path)

    open_settings_menu()

def save_part_formats_config(old_part_formats):
    new_part_formats = text_part_formats_config.get("1.0", "end-1c")
    if old_part_formats != new_part_formats:
        if new_part_formats != "":
            with open("config/part-file-formats.txt",
                      "w") as edit_part_formats:
                edit_part_formats.write(new_part_formats)
            
    part_formats_config.destroy()
    open_settings_menu()

def config_part_file_formats():
    settings_option.destroy()

    global part_formats_config
    part_formats_config = tk.Toplevel(root)
    part_formats_config.title("Edit Part File Formats")
    part_formats_config.resizable(False, False)

    part_formats_guide = tk.Label(part_formats_config,
                                  text="Format:\n<format 1>,<format 2>,<format n>\n\nExample:\n.3mf,.stl",
                                  anchor="w",
                                  justify="left")
    part_formats_guide.pack(side=tk.TOP, fill=tk.BOTH, pady=15)

    global text_part_formats_config
    text_part_formats_config = tk.Text(part_formats_config)
    text_part_formats_config.pack(fill=tk.BOTH, expand=True)

    with open("config/part-file-formats.txt", "r") as saved_part_formats:
        current_part_formats = saved_part_formats.read()
        clean_current_part_formats =\
            sanitize.clean_newline(current_part_formats)
        text_part_formats_config.insert("1.0", clean_current_part_formats)

    save_part_formats = tk.Button(part_formats_config,
                                  text="Save Format(s)",
                                  command=
                                  lambda
                                  old_part_formats=clean_current_part_formats:
                                  save_part_formats_config(old_part_formats))
    
    save_part_formats.pack(pady=10)

    text_part_formats_config.bind("<Control-s>", lambda old_part_formats=
                                  clean_current_part_formats:
                                  save_part_formats_config(old_part_formats))
    
def save_laser_formats_config(old_laser_formats):
    new_laser_formats = text_laser_formats_config.get("1.0", "end-1c")
    if old_laser_formats != new_laser_formats:
        if new_laser_formats != "":
            with open("config/laser-file-formats.txt",
                      "w") as edit_laser_formats:
                edit_laser_formats.write(new_laser_formats)
            
    laser_formats_config.destroy()
    open_settings_menu()
    
def config_laser_file_formats():
    settings_option.destroy()

    global laser_formats_config
    laser_formats_config = tk.Toplevel(root)
    laser_formats_config.title("Edit Laser File Formats")
    laser_formats_config.resizable(False, False)

    laser_formats_guide = tk.Label(laser_formats_config,
                                   text="Format:\n<format 1>,<format 2>,<format n>\n\nExample:\n.xcs,.svg",
                                   anchor="w",
                                   justify="left")
    laser_formats_guide.pack(side=tk.TOP, fill=tk.BOTH, pady=15)

    global text_laser_formats_config
    text_laser_formats_config = tk.Text(laser_formats_config)
    text_laser_formats_config.pack(fill=tk.BOTH, expand=True)

    with open("config/laser-file-formats.txt", "r") as saved_laser_formats:
        current_laser_formats = saved_laser_formats.read()
        clean_current_laser_formats =\
            sanitize.clean_newline(current_laser_formats)
        text_laser_formats_config.insert("1.0", clean_current_laser_formats)

    save_laser_formats = tk.Button(laser_formats_config,
                                   text="Save Format(s)",
                                   command=
                                   lambda
                                   old_laser_formats=
                                   clean_current_laser_formats:
                                   save_laser_formats_config(old_laser_formats))
    
    save_laser_formats.pack(pady=10)

    text_laser_formats_config.bind("<Control-s>", lambda old_laser_formats=
                                   clean_current_laser_formats:
                                   save_laser_formats_config(old_laser_formats))

def save_app_list_config(old_app_list):
    new_app_list = text_app_list_config.get("1.0", "end-1c")
    if old_app_list != new_app_list:
        if new_app_list != "":
            with open("config/application-lists.txt",
                      "w") as edit_app_list:
                edit_app_list.write(new_app_list)
            
    app_list_config.destroy()
    open_settings_menu()

def config_apps_list():
    settings_option.destroy()

    global app_list_config
    app_list_config = tk.Toplevel(root)
    app_list_config.title("Edit Applications")
    app_list_config.resizable(False, False)

    app_list_guide = tk.Label(app_list_config,
                              text="Format:\n<type of file>,<app name>,<app executable name or path>\n\nNote that <type of file> can only have 2 types: 'part-file' for 3D models or 'laser-file' for laser services",
                              anchor="w",
                              justify="left")
    app_list_guide.pack(side=tk.TOP, fill=tk.BOTH, pady=15)
    
    global text_app_list_config
    text_app_list_config = tk.Text(app_list_config)
    text_app_list_config.pack(fill=tk.BOTH, expand=True)

    with open("config/application-lists.txt", "r") as saved_app_list:
        current_app_list = saved_app_list.read()
        clean_current_app_list =\
            sanitize.clean_newline(current_app_list)
        text_app_list_config.insert("1.0", clean_current_app_list)

    save_app_list = tk.Button(app_list_config,
                              text="Save Configuration",
                              command=
                              lambda
                              old_app_list=clean_current_app_list:
                              save_app_list_config(old_app_list))
    
    save_app_list.pack(pady=10)

    text_app_list_config.bind("<Control-s>", lambda old_app_list=
                              clean_current_app_list:
                              save_app_list_config(old_app_list))

# Frontend, GUI stuff (e.g. buttons, etc)
def go_home():
    current_path.set(os.path.expanduser(home_path()))
    update_contents()

def go_back():
    current_path.set(os.path.dirname(current_path.get()))
    path_history.append(current_path.get())
    update_contents()

def go_forward():
    # Fetch previous directory from history list and update current path
    if len(path_history) > 1:
        current_path.set(path_history[-2])
        path_history.pop()
        update_contents()
    elif len(path_history) == 1:
        current_path.set(path_history[-1])
        path_history.pop()
        update_contents()

def search_path(event=None):
    path = url_entry.get()
    clear_url_bar()
    open_path(path)

def clear_placeholder(event):
    if url_entry.get() == "Input file path":
        url_entry.delete(0, tk.END)
        url_entry.config(fg='black')

def restore_placeholder(event):
    if not url_entry.get():
        url_entry.insert(0, "Input file path")
        url_entry.config(fg='grey')

def more_options_menu():
    more_options.post(more_button.winfo_rootx(), more_button.winfo_rooty()
                      + more_button.winfo_height())

# Allow user to choose an app when a file is clicked on
def application_options(file_type, path):
    available_apps = []
    with open("config/application-lists.txt", "r") as app_lists:
        file_line = app_lists.read()
        line_list = file_line.split("\n")
        for app_list in line_list:
            clean_app_list = sanitize.clean_newline(app_list)
            if file_type in clean_app_list:
                available_apps.append(clean_app_list)

    # Generate buttons on a new frame
    # Allow user to select applications
    app_options = tk.Toplevel(root)
    app_options.title("Choose Application")
    app_options.resizable(False, False)

    for current_iteration in available_apps:
        current_list_app = current_iteration.split(",")
        app_name = current_list_app[1]
        exe_name = current_list_app[2]
        app_choice_button = tk.Button(app_options, text=app_name,
                                      command=lambda current_frame=app_options,
                                      run_exe_name=exe_name,
                                      source_path=path:
                                      run_application(current_frame,
                                                      run_exe_name,
                                                      source_path))
        app_choice_button.pack(padx=100, pady=5)

def open_settings_menu():
    # tkinter's default text font
    default_tk_font = font.nametofont("TkDefaultFont")
    default_tk_font.actual()
    
    x_axis_settings_button = 100
    y_axis_settings_button = 5

    global settings_option
    
    settings_option = tk.Toplevel(root)
    settings_option.title("Settings")
    settings_option.resizable(False, False)

    # Change home path
    settings_home_path = tk.Button(settings_option, text="Set home path",
                                   command=config_home_path)
    settings_home_path.pack(padx=10, pady=0, anchor="w")
    
    current_home_path = home_path()
    home_path_subtitles = tk.Label(settings_option,
                                   text=fr"Current: {current_home_path}",
                                   font=(default_tk_font, 8),
                                   fg=custom_colors.dark_grey)
    home_path_subtitles.pack(padx=10, pady=0, anchor="w")

    # Edit part file formats to track
    settings_part_formats = tk.Button(settings_option,
                                      text="Edit part file formats to track",
                                      command=config_part_file_formats)
    settings_part_formats.pack(padx=10, pady=10, anchor="w")

    # Edit laser file formats to track
    settings_laser_formats = tk.Button(settings_option,
                                       text="Edit laser file formats to track",
                                       command=config_laser_file_formats)
    settings_laser_formats.pack(padx=10, pady=5, anchor="w")

    # Manage apps to include
    settings_apps = tk.Button(settings_option,
                              text="Manage the list of apps to open with",
                              command=config_apps_list)
    settings_apps.pack(padx=10, pady=5, anchor="w")

# Create GUI instance
root = tk.Tk()
root.title("Print Queue Manager {}".format(app_version))
# Disable window resize
root.resizable(False, False)

# Create frame for URL search bar and buttons
url_frame = tk.Frame(root)
url_frame.pack(padx=35, pady=10)

# Create home button
home_button = tk.Button(url_frame, text="Home", compound=tk.LEFT,
                        command=go_home)
home_button.pack(side=tk.LEFT, padx=5)

# Create back button
back_button = tk.Button(url_frame, text="Back", compound=tk.LEFT,
                        command=go_back)
back_button.pack(side=tk.LEFT, padx=5)

# Create forward button
forward_button = tk.Button(url_frame, text="Forward", compound=tk.LEFT,
                           command=go_forward)
forward_button.pack(side=tk.LEFT, padx=5)

# Create text to aid user on URL search bar
url_entry = tk.Entry(url_frame, width=50, fg='grey')
url_entry.insert(0, "Input file path")
url_entry.bind("<FocusIn>", clear_placeholder)
url_entry.bind("<FocusOut>", restore_placeholder)
url_entry.pack(side=tk.LEFT, padx=5)

# Bind the enter button to the URL search bar
# Shortcut for search_button
url_entry.bind("<Return>", search_path)

# Create search button
search_button = tk.Button(url_frame, text="Go", command=search_path)
search_button.pack(side=tk.LEFT, padx=5)

# More option button
more_button = tk.Button(url_frame, text="...", command=more_options_menu)
more_button.pack(side=tk.LEFT, padx=5)

more_options = tk.Menu(url_frame, tearoff=0)

more_options.add_command(label="Settings",
                         command=open_settings_menu)

hidden_file_toggle = tk.IntVar()
more_options.add_checkbutton(label="Show Hidden Items",
                             variable=hidden_file_toggle,
                             onvalue=1,
                             offvalue=0,
                             command=list_hidden_files)

more_options.add_command(label="Open File Manager",
                         command=open_file_manager)

#Canvas widget in centre
canvas = tk.Canvas(root)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Add a scrollbar
scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Configure canvas to scroll with scrollbar
canvas.configure(yscrollcommand=scrollbar.set)

# Bind mouse wheel scrolling to canvas
canvas.bind_all("<MouseWheel>", canvas_scrolling)

current_path = tk.StringVar()
current_path.set(home_path())

update_contents()

root.mainloop()
