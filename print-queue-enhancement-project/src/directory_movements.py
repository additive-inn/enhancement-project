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

import os
import shutil

# Custom libraries
import utils.clean as sanitize

# Older method of opening files
def file_sort(path):
        with open("./config/formats-to-track.txt", "r") as file_formats:
                valid_formats = file_formats.read()
                clean_valid_formats = sanitize.clean_newline(valid_formats)
        formats_to_sort = clean_valid_formats.split(",")
        for current_format in formats_to_sort:
                if current_format in path:
                        move_to_complete(path)

# Newer method of opening files
# Differentiates between part files and laser cutting files
def file_sort_type(path):
        with open("./config/part-file-formats.txt", "r") as part_file_formats:
                valid_part_formats = part_file_formats.read()
                clean_part_formats = sanitize.clean_newline(valid_part_formats)
                part_formats = clean_part_formats.split(",")
                for current_format in part_formats:
                        if current_format in path:
                                return "part-file"
        with open("./config/laser-file-formats.txt", "r") as laser_file_formats:
                valid_laser_formats = laser_file_formats.read()
                clean_laser_formats = sanitize.clean_newline(valid_laser_formats)
                laser_formats = clean_laser_formats.split(",")
                for current_format in laser_formats:
                        if current_format in path:
                                return "laser-file"

# Copied file to .complete folder
def copy_to_complete(path):
        parent_path = os.path.dirname(path)
        complete_folder = os.path.join(parent_path ,".complete")
        folder_existance = os.path.exists(complete_folder)
        if folder_existance == False:
                os.mkdir(complete_folder)
        current_file = path
        destination_folder = complete_folder
        shutil.copy2(current_file, destination_folder)
