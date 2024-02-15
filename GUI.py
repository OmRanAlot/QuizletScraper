import PySimpleGUI as sg
import firebase_admin
from firebase_admin import credentials, db
import settings
import methods


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
print(folder)

dropdown = sg.Combo(folder,default_value="Pick a folder", size= methods.findLongest(folder),enable_events=True,  readonly=False, key='-COMBO-')

layout = [  [sg.Text('Welcome to my Quizlet Scraper!')],
            [sg.Text('Enter the URL of the Quizlet Set you want to scrape', key='url'), sg.InputText()],
            [sg.Text('Enter the Flashcard Set Name you want', key='setName'), sg.InputText()],
            [dropdown],
            [sg.Button('Scrape','center')]
            ]

# Create the Window
window = sg.Window('Quizlet Scraper', layout,element_justification='c')
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    
    print(values)

    if event == sg.WIN_CLOSED: # if user closes window or clicks cancel
        break
    #Checks if the button "Scrape" is pressed
    if event == 'Scrape':
        print('url:', values['url'])
        print('flashcard set name ', values['setName'])

    

window.close()

