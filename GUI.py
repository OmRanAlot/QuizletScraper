import PySimpleGUI as sg
import firebase_admin
from firebase_admin import credentials, db
import settings
import methods
from scraper import *

cred = credentials.Certificate('cred.json')
firebase_admin.initialize_app(cred, {'databaseURL': settings.db_url})

sg.theme('DarkGrey11')   # Add a touch of color
# All the stuff inside your window.
folder = []

ref = db.reference('/')
# Function to recursively get all references and add them to a list
for key in ref.get().keys():
    folder.append(key)

folder.append('Create new Folder')

dropdown = sg.Combo(folder,default_value="Pick a folder", size= methods.findLongest(folder),enable_events=True,  readonly=False, key='-COMBO-')

layout = [  [sg.Text('Welcome to my Quizlet Scraper!')],
            [sg.Text('Enter the URL of the Quizlet Set you want to scrape', key='url'), sg.InputText()],
            [sg.Text('Enter the Flashcard Set Name you want', key='setName'), sg.InputText()],
            [dropdown],
            [sg.Button('Scrape', key="-Scrape-")],
            [sg.Text('Enter the name for the new folder:', visible=False, key="-toggleText-"), sg.InputText(key='-Input-',visible=False)],
            [sg.Button('Create Folder',visible=False, key="-toggleButton-")]
            ]

# Create the Window
window = sg.Window('Quizlet Scraper', layout,element_justification='c')
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    
    print(event)

    if values['-COMBO-'] == "Create new Folder":
        window["-toggleText-"].update(visible=True)
        window["-Input-"].update(visible=True)
        window["-toggleButton-"].update(visible=True)

    
    match event:
        case sg.WIN_CLOSED:
            break
        case '-Scrape-':
            if values["-COMBO-"] == "Pick a Folder":
                sg.popup("You need to select a folder! If you don't have one, then you can create one.")
            else:
                print('url:', values[0])
                print('flashcard set name ', values[1])
                print(values["-COMBO-"])
                # scrap = Scraper(url=values[0],
                #                 flashcardSetName=values[1],
                #                 usr=settings.email,
                #                 pwd=settings.pwd)

        case "-toggleButton-":
            if values["-Input-"] == "":
               sg.popup("You need to enter something!")
            else:
                fo = values["-Input-"]
                db.reference(fo).push("temp1")

                folder.insert(0,fo)
                window["-toggleText-"].update(visible=False)
                window["-Input-"].update(visible=False)
                window["-toggleButton-"].update(visible=False)
                window["-COMBO-"].update(value= folder[0])
        

    # if event == sg.WIN_CLOSED: # if user closes window or clicks cancel
    #     break
    # #Checks if the button "Scrape" is pressed
    # elif event == 'Scrape':
    #     print('url:', values[0])
    #     print('flashcard set name ', values[1])
    # elif event =="Create Folder":
    #     if values["-Input-"] == "":
    #         sg.popup("You need to enter something!")
    #     else:
    #         print(values["-Input-"])
    #         window["-toggleText-"].update(visible=False)
    #         window["-Input-"].update(visible=False)
    #         window["-toggleButton-"].update(visible=False)

window.close()


