import glob
import json
import os
import sqlite3
import sys
import webbrowser
from pathlib import Path
import psutil
from tkinter import messagebox, Label, Button, Tk, CENTER, simpledialog, Checkbutton, BooleanVar
from tkinter.filedialog import askopenfilename
import requests
import configparser

config = configparser.ConfigParser()

version = 0.61


def check_version():
    try:
        get_version = \
            float(
                requests.get(
                    "https://api.github.com/repos/WakuWakuPadoru/WuWa_Simple_FPSUnlocker/releases/latest").json()[
                    "tag_name"][1:])
        if get_version > version:
            ask_update_dialog = messagebox.askyesno("Update Available",
                                                    f"An update is available!\nWould you like to view the latest release?\n\nCurrent Version: {version}\nLatest Version: {get_version}")
            if ask_update_dialog is True:
                webbrowser.open("https://github.com/WakuWakuPadoru/WuWa_Simple_FPSUnlocker/releases/latest")
            else:
                return
    except Exception as e:
        return


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def check_process_ok():
    if any(item in ["launcher.exe", "Wuthering Waves.exe"] for item in
           [p.name() for p in psutil.process_iter(attrs=['name'])]):
        messagebox.showerror("Error", "Please close the game before proceeding.")
        return False
    else:
        return True


def fullscreen(db_directory, path_dir_fs_cfg):
    try:
        config.read(path_dir_fs_cfg)
        fs = config.get("/Script/Engine.GameUserSettings", "FullscreenMode")
        last_fs = config.get("/Script/Engine.GameUserSettings", "LastConfirmedFullscreenMode")
        pref_fs = config.get("/Script/Engine.GameUserSettings", "PreferredFullscreenMode")
        fsm_list = [fs, last_fs, pref_fs]
        fs_status = None
        if min(fsm_list) == "0":
            fs_status = "Enabled"
        else:
            fs_status = "Disabled"
        current_x = config.get("/Script/Engine.GameUserSettings", "resolutionsizex")
        current_y = config.get("/Script/Engine.GameUserSettings", "resolutionsizey")
        fullscreen_mode_decision = messagebox.askyesno("True Fullscreen Mode",
                                                       "Would you like to enable True Fullscreen Mode? (Optional). Click on \"Yes\" to enable or \"No\" to disable.\n\nIf you enable this, you can also set your own desired Fullscreen Resolution."
                                                       f"\n\nCurrent Status: {fs_status}\nCurrent Resolution: {current_x}x{current_y}")
        if fullscreen_mode_decision is True:
            resolution = simpledialog.askstring(title="Resolution",
                                                prompt="Choose your desired Resolution (E.g. 1280x720, 1920x1080, 2560x1440, and etc:\t\t\t",
                                                initialvalue=f"{current_x}x{current_y}")
            if resolution is not None and resolution != "":
                x = resolution.split("x")[0]
                y = resolution.split("x")[1]
                while True:
                    try:
                        x = int(x)
                        y = int(y)
                        break
                    except Exception as e:
                        messagebox.showerror("Error",
                                             "Please enter a valid Resolution (E.g. 1280x720, 1920x1080, 2560x1440, and etc)")
                        resolution = simpledialog.askstring(title="Resolution",
                                                            prompt="Please enter a valid Resolution (E.g. 1280x720, 1920x1080, 2560x1440, and etc:\t\t\t",
                                                            initialvalue=f"{current_x}x{current_y}")
                        if resolution is not None and resolution != "":
                            x = resolution.split("x")[0]
                            y = resolution.split("x")[1]
                        else:
                            x = x
                            y = y
                db = sqlite3.connect(
                    Path(db_directory).joinpath("LocalStorage.db"))
                cursor = db.cursor()
                cursor.execute("SELECT * FROM LocalStorage WHERE Key = 'GameQualitySetting'")
                json_value = json.loads(cursor.fetchone()[1])
                json_value["KeyPcResolutionWidth"] = x
                json_value["KeyPcResolutionHeight"] = y
                cursor.execute("UPDATE LocalStorage SET Value = ? WHERE Key = 'GameQualitySetting'",
                               (json.dumps(json_value),))
                db.commit()
                config.set("/Script/Engine.GameUserSettings", "lastuserconfirmedresolutionsizex", str(x))
                config.set("/Script/Engine.GameUserSettings", "lastuserconfirmedresolutionsizey", str(y))
                config.set("/Script/Engine.GameUserSettings", "resolutionsizex", str(x))
                config.set("/Script/Engine.GameUserSettings", "resolutionsizey", str(y))
                messagebox.OK = messagebox.showinfo("Success",
                                                    "Resolution changed successfully!")
            else:
                messagebox.showinfo("Info", "No Resolution selected, using current Resolution settings.")
            config.set("/Script/Engine.GameUserSettings", "FullscreenMode", "0")
            config.set("/Script/Engine.GameUserSettings", "LastConfirmedFullscreenMode", "0")
            config.set("/Script/Engine.GameUserSettings", "PreferredFullscreenMode", "0")
            with open(path_dir_fs_cfg, "w") as configfile:
                config.write(configfile)
            messagebox.showinfo("Success", "True Fullscreen Mode enabled successfully!")
        elif fullscreen_mode_decision is False:
            config.set("/Script/Engine.GameUserSettings", "FullscreenMode", "1")
            config.set("/Script/Engine.GameUserSettings", "LastConfirmedFullscreenMode", "1")
            config.set("/Script/Engine.GameUserSettings", "PreferredFullscreenMode", "1")
            with open(path_dir_fs_cfg, "w") as configfile:
                config.write(configfile)
            messagebox.showinfo("Success", "True Fullscreen Mode disabled successfully!")
    except TypeError as e:
        if str(e) == "'NoneType' object is not subscriptable":
            messagebox.showerror("Error",
                                 "Your LocalStorage file is incomplete. Please run the game at least once and try again!")
        else:
            messagebox.showerror("Error",
                                 f"An error occurred. Please raise an issue or contact me on the GitHub Page with the following message: \n\n{e}")
            webbrowser.open("https://github.com/WakuWakuPadoru/WuWa_Simple_FPSUnlocker/issues")
    except Exception as e:  # This shouldn't happen as this file should be generated by the game together with the LocalStorage file which was checked earlier.
        messagebox.showerror("Error",
                             f"An error occurred. Please raise an issue or contact me on the GitHub Page with the following message: \n\n{e}")
        webbrowser.open("https://github.com/WakuWakuPadoru/WuWa_Simple_FPSUnlocker/issues")


def choose_directory():
    if check_process_ok() is True:
        directory = askopenfilename(initialdir="C:/Wuthering Waves/Wuthering Waves Game/",
                                    title="Select where \"Wuthering Waves.exe\" is located.",
                                    filetypes=[("exe files", "Wuthering Waves.exe")])
        if directory is not None and directory != "":
            path_dir_exe = Path(directory).parent.joinpath("Wuthering Waves.exe")
            path_dir_ext = Path(directory).parent.joinpath("Client", "Saved", "LocalStorage")
            path_dir_fs_cfg = Path(directory).parent.joinpath("Client", "Saved", "Config", "WindowsNoEditor",
                                                              "GameUserSettings.ini")
            if path_dir_ext.is_dir() and path_dir_exe.is_file():
                matching_files = sorted(glob.glob(str(path_dir_ext) + "/LocalStorage*.db"))
                matching_files_oos = "\n".join(matching_files)
                if len(matching_files) > 1:
                    messagebox.showerror("Error",
                                         "Multiple LocalStorage files found. This may cause compatibility issues with the FPS Unlocker."
                                         f"\n\n{matching_files_oos}"
                                         "\n\nThis is usually caused by game crashes or corruption with the original file. Please do the following before continuing:"
                                         "\n\n1) Click on OK to open the folder where the LocalStorage files are located. "
                                         "\n2) Make sure that the game and launcher isn't running and delete all files in the opened folder. (Your settings will be reset)."
                                         "\n3) Run the game at least once and close it to generate a new LocalStorage file."
                                         "\n4) Run this program again and it should work as intended.")

                    os.startfile(path_dir_ext)
                    return
                elif len(matching_files) == 0:
                    messagebox.showerror("Error",
                                         "LocalStorage file not found. Please run the game at least once and try again!")

                else:
                    messagebox.showinfo("Success", "File selected successfully!")
                    fullscreen(path_dir_ext, path_dir_fs_cfg)
                    fps_value(path_dir_ext, path_dir_fs_cfg)
            else:
                messagebox.showerror("Error",
                                     "LocalStorage file not found. Please run the game at least once and try again!")
        else:
            return


def fps_value(db_directory, path_dir_fs_cfg):
    try:
        fps = simpledialog.askinteger(title="", prompt="Choose your desired FPS Value:\t\t\t", initialvalue=90,
                                      minvalue=60, maxvalue=120)
        if fps is not None:
            db = sqlite3.connect(
                Path(db_directory).joinpath("LocalStorage.db"))
            cursor = db.cursor()
            cursor.execute("SELECT * FROM LocalStorage WHERE Key = 'GameQualitySetting'")
            json_value = json.loads(cursor.fetchone()[1])
            json_value["KeyCustomFrameRate"] = fps
            cursor.execute("UPDATE LocalStorage SET Value = ? WHERE Key = 'GameQualitySetting'",
                           (json.dumps(json_value),))
            messagebox.OK = messagebox.showinfo("Success",
                                                "FPS Value changed successfully! You can now close this program and enjoy the game!")
            db.commit()
            config.set("/Script/Engine.GameUserSettings", "frameratelimit", str(fps))
            with open(path_dir_fs_cfg, "w") as configfile:
                config.write(configfile)
    except TypeError as e:
        if str(e) == "'NoneType' object is not subscriptable":
            messagebox.showerror("Error",
                                 "Your LocalStorage file is incomplete. Please run the game at least once and try again!")
        else:
            messagebox.showerror("Error",
                                 f"An error occurred. Please raise an issue or contact me on the GitHub Page with the following message: \n\n{e}")
            webbrowser.open("https://github.com/WakuWakuPadoru/WuWa_Simple_FPSUnlocker/issues")
    except Exception as e:
        messagebox.showerror("Error",
                             f"An error occurred. Please raise an issue or contact me on the GitHub Page with the following message: \n\n{e}")
        webbrowser.open("https://github.com/WakuWakuPadoru/WuWa_Simple_FPSUnlocker/issues")


root_window = Tk()
root_window.title(f"Wuthering Waves FPS Unlocker v{version}")
root_window.geometry("600x600")
root_window.iconbitmap(default=resource_path("./icon.ico"))
root_window.withdraw()
check_version()
root_window.deiconify()
label = Label(root_window, text=f"Welcome to Wuthering Waves FPS Unlocker v{version}!"
                                "\n\n To get started...\nStep 1) Run the game at least once before using this tool. This generates the needed configuration files.\nStep 2) Click on \"Browse\" to locate the \"Wuthering Waves.exe\" file.\nStep 3) You will be asked if you would like to enable/disable \"True Fullscreen Mode\". This is optional.\nStep 4) If you enable \"True Fullscreen Mode\", you can also set your own desired Fullscreen Resolution.\n\nMake sure that the game isn't running!"
                                "\n\n1) You may need to run this program again when you change graphical settings or when there's a new patch.\n2) This doesn't change the game files in any way, only your saved \"settings\"."
                                "\n3) \"True Fullscreen Mode\" might marginally improve performance over the default Fullscreen Setting. This allows Windows to better manage the game's resources.\n",
              font=("Bahnschrift", 14), wraplength=590, justify=CENTER)
label.pack()
button = Button(root_window, text="Browse", command=choose_directory, font=("Bahnschrift", 14))
button.pack(pady=(20, 10))
root_window.mainloop()
