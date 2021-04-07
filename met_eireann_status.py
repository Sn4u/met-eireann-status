import requests
import json
import tkinter
from tkinter import ttk
from datetime import datetime
import textwrap
from os import getcwd

# read json files with
with open(getcwd() + '\\' + "region_codes.json", "r") as file:
    REGION_CODES = json.loads(file.read())

with open(getcwd() + '\\' + "marine_codes.json", "r") as file:
    MARINE_CODES = json.loads(file.read())

dimensions = {"width": "60", "height": "10", }
style_no_warning = {"foreground": "black", "background": "green", "font": "Helvetica 11 bold"}
style_yellow = {"foreground": "Black", "background": "yellow"}
style_orange = {"foreground": "Black", "background": "orange"}
style_red = {"foreground": "Black", "background": "red"}
style_bold = {"font": "Helvetica 9 bold"}
level_to_style = {
    "Yellow": style_yellow,
    "Orange": style_orange,
    "Red": style_red,
}

warnings_objects = []  # Warnings class objects


class Warnings:
    def __init__(self, json_data=None):
        warnings_objects.append(self)
        self.frame = tkinter.Frame(root, **dimensions)
        self.frame.pack(fill='both', expand=True)

        if json_data:
            print(json_data)
            self.cap_id = json_data['capId']
            self.id = json_data['id']
            self.type = json_data['type']
            self.severity = json_data['severity']
            self.certainty = json_data['certainty']
            self.level = json_data['level']
            self.issued = json_data['issued']
            self.updated = json_data['updated']
            self.onset = json_data['onset']
            self.expiry = json_data['expiry']
            self.headline = json_data['headline']
            self.description = json_data['description']
            self.regions = json_data['regions']
            self.status = json_data['status']

            self.delta = None
            self.delta_msg = None
            self.style = level_to_style[self.level]

            if update_time() != 'expired':
                self.make()

    def make(self):

        # primary
        self.primary = tkinter.Frame(self.frame, background=self.level, **dimensions)
        self.primary.pack(fill='both', side='left')
        self.primary.bind('<Button-1>', self.display_extra)

        self.headline_label = tkinter.Label(self.primary, self.style, text=self.headline, justify='center',
                                            wraplength=500, font=('Helvetica', 11, 'bold'), width=55)
        self.headline_label.pack(side='top')

        self.primary_info_frame = tkinter.Frame(self.primary, background=self.level)
        self.certainty_frame = tkinter.Frame(self.primary_info_frame)
        self.delta_frame = tkinter.Frame(self.primary_info_frame)
        self.severity_frame = tkinter.Frame(self.primary_info_frame)
        self.primary_info_frame.pack(side='left')
        self.certainty_frame.pack(side='left')
        self.delta_frame.pack(side='left')
        self.severity_frame.pack(side='left')

        self.certainty_label = tkinter.Label(self.certainty_frame, self.style, text="Certainty: ")
        self.certainty_text = tkinter.Label(self.certainty_frame, self.style, font=('Helvetica', 9, 'bold'),
                                            text=self.certainty)
        self.certainty_label.pack(side='left')
        self.certainty_text.pack(side='left')

        self.delta_label = tkinter.Label(self.delta_frame, self.style, text=self.delta_msg)
        self.delta_text = tkinter.Label(self.delta_frame, self.style, text=self.delta,
                                        font=('Helvetica', 9, 'bold'))
        self.delta_label.pack(side='left')
        self.delta_text.pack(side='left')
        self.severity_label = tkinter.Label(self.severity_frame, text="Severity: ")
        self.severity_text = tkinter.Label(self.severity_frame, self.style, font=('Helvetica', 9, 'bold'),
                                           text=self.severity)

        self.headline_label.bind('<Button-1>', self.display_extra)

        # secondary
        self.secondary = tkinter.Frame(self.frame, **dimensions, relief=tkinter.SUNKEN, borderwidth=4)

        self.dates_frame = tkinter.Frame(self.secondary)
        self.issued_text = tkinter.Label(self.dates_frame, text='Issued: ')
        self.issued_time = tkinter.Label(self.dates_frame, text=format_time(self.issued),
                                         font=('Helvetica', 9, 'bold'))
        self.expiry_text = tkinter.Label(self.dates_frame, text='Expiry: ')
        self.expiry_time = tkinter.Label(self.dates_frame, text=format_time(self.expiry),
                                         font=('Helvetica', 9, 'bold'))

        self.dates_frame.pack(side='top')
        self.issued_text.pack(side='left')
        self.issued_time.pack(side='left')
        self.expiry_text.pack(side='left')
        self.expiry_time.pack(side='left')

        self.desclabel = tkinter.Label(self.secondary, text=self.format_description(),

                                       height=4)
        self.desclabel.pack(side='bottom')
        self.secondary.visible = False

    def delete(self=None, del_all=False):
        if del_all is True:
            # delete all Warning objects
            for obj in warnings_objects:
                for widget in obj.frame.winfo_children():
                    widget.destroy()
                obj.frame.destroy()
            warnings_objects.clear()
        else:
            # if warning's frame exists, delete frame and everything inside it
            # if not, only delete the warning
            try:
                for widget in self.frame.winfo_children():
                    widget.destroy()
                    widget.frame.destroy()
            except AttributeError:
                warnings_objects.remove(self)

    def display_extra(self, event=None):
        """toggle secondary panel visibility"""

        def forget_old():
            self.certainty_frame.pack_forget()
            self.delta_frame.pack_forget()

        if self.secondary.visible is False:
            self.secondary.pack(fill='both', side='right', expand=True)

            forget_old()
            self.certainty_frame.pack(side='top', anchor='w')
            self.delta_frame.pack(side='top', anchor='w')
        else:
            self.secondary.pack_forget()

            forget_old()
            self.certainty_frame.pack(side='left')
            self.delta_frame.pack(side='left')

        self.secondary.visible = not self.secondary.visible

    def format_description(self):
        return textwrap.TextWrapper(max_lines=3).fill(text=self.description)

    def create_non_warning(self, message):
        self.frame.configure(height=10, width=60)
        self.headline_label = tkinter.Label(self.frame, style_no_warning,
                                            text=message)
        self.headline_label.pack(fill='both', expand=True)

def download_json(selected_region):
    if selected_region == "Demo":
        with open(getcwd() + '\\' + "demo_weather_warning.json", "r") as file:
            response = json.loads(file.read())
    else:
        if selected_region in REGION_CODES:
            areacode = REGION_CODES[selected_region]
        else:
            areacode = MARINE_CODES[selected_region]
        met_url = "https://www.met.ie/Open_Data/json/warning_" + areacode + ".json"

        response = requests.get(met_url).json()  # downloads latest json from api with given region
    return response


def format_time(date_input):
    """format time to be displayed on warning card
    Example: 2021-02-21T14:45:06-00:00 -> Feb 21 At 14:45"""
    date_object = datetime.strptime(date_input, '%Y-%m-%dT%H:%M:%S%z')
    return date_object.strftime('%b %d At %H:%M')


def update_time():
    """For every warning object, compare current time to expiration time to check if warning is expired.
    If expired, return 'expired' and delete the warning card. Otherwise check if warning is in place or not in place yet
    and assign time delta and correct label to the object attribute"""
    t_format = '%Y-%m-%dT%H:%M:%S'
    current_time = datetime.now()

    for obj in warnings_objects:
        onset_time = datetime.strptime(obj.onset[:-6], t_format)
        expiry_time = datetime.strptime(obj.expiry[:-6], t_format)

        if current_time > onset_time and current_time > expiry_time:
            # we are past both the onset and the expiration
            # destroy tkinter warning widgets and remove Warnings object.

            obj.delete()
            return "expired"

        elif current_time > onset_time:
            # warning is in place but not expired
            # display time until expiration
            obj.delta = ':'.join(str(expiry_time - current_time).split(':')[:2])
            obj.delta_msg = 'Time until expiration: '

        else:
            # warning is not in place yet
            # display time until warning onset
            obj.delta = ':'.join(str(onset_time - current_time).split(':')[:2])
            obj.delta_msg = 'Time until onset: '


def flash_red():
    """Make the headline of warning card flash red and white"""
    for obj in warnings_objects:
        try:
            if obj.level == "Red":
                if obj.headline_label["background"] != 'white':
                    obj.headline_label.configure(backgroun='white')
                else:
                    obj.headline_label.configure(background='red')
        except AttributeError:
            pass


def refresh(event=None):
    Warnings.delete(del_all=True)

    selected_region = combox.get()  # gets the selected region from combo box
    response = download_json(selected_region)

    # if there are no warnings, display it as a message
    if len(response) == 0:
        Warnings().create_non_warning(message="There are no warnings for the selected region")
    # root.geometry('350x200')
    else:
        create_object(response, selected_region)

def error_no_internet():
    # todo
    pass


def create_object(response, selected_region):
    # creates a class object for all warnings that match location
    # todo is this needed?
    for dict_entry in response:
        if selected_region == 'Demo' or selected_region == "All counties":
            Warnings(dict_entry)
        elif REGION_CODES[selected_region] in dict_entry['regions']:
            print(REGION_CODES[selected_region])
            Warnings(dict_entry)


def update_combox_val():
    sea_val = sea_box_val.get()
    if sea_val == 1:
        combox.configure(values=[i for i in MARINE_CODES.keys()])
        location_label.configure(text="Select Marine Zone: ")
    else:
        combox.configure(values=[i for i in REGION_CODES.keys()])
        location_label.configure(text="Select County: ")


# GUI
root = tkinter.Tk()
root.resizable(False, False)
root.title("Met Eireann Status")
root.iconbitmap("Assets/MetEireann logo-02.ico")
root["bg"] = "gray"  # todo this doesn't work. Why?

options_frame = tkinter.LabelFrame(root, relief=tkinter.RAISED, borderwidth=5, bg='white')
options_frame.pack(fill='x')

location_label = tkinter.Label(options_frame, text="Select County:", width=14)
location_label.grid(column=0, row=0, padx=5, pady=4)

combox = tkinter.ttk.Combobox(options_frame, values=[i for i in REGION_CODES.keys()], state="readonly")
combox.current(27)  # sets default for the combo box
combox.grid(column=1, row=0, padx=5, pady=4)

refresh_button = tkinter.Button(options_frame, text='Refresh', command=refresh)
refresh_button.grid(column=3, row=0, padx=4, pady=5)
root.bind('<Return>', refresh)

sea_box_val = tkinter.IntVar()
sea_check_box = tkinter.Checkbutton(options_frame, variable=sea_box_val, text="Search Marine Warnings",
                                    command=update_combox_val)
sea_check_box.grid(column=4, row=0)


def tick():
    root.after(1000, tick)
    flash_red()


tick()
root.mainloop()

# todo add all information to be displayed
# todo prevent duplicate warnings
# todo auto launch at startup and check for warnings in background process
# todo implement timer to prevent spamming requests
# todo display time and date on options bar
# todo create a new tab showing what warning information means
# todo place icons for warning type
# todo create a new tab showing a map
# todo make background light gray
# todo "warning: cannot connect to internet"
# todo give credit to met eireann
# todo give region by province instead of county