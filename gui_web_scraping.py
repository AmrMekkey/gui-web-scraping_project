from ttkbootstrap import *
import requests
from bs4 import BeautifulSoup
import csv
from ttkbootstrap.dialogs import Messagebox
from tkinter import filedialog
from threading import Thread
import os

root = Window(themename='vapor')
root.title('Match Center')
root.geometry('1200x700+300+100')

matches_details = []

welcome_label = Label(root, text='Welcome to Match Center', font=('helvetica', 18, 'bold'), bootstyle='secondary, inverse')
welcome_label.pack(pady=10, fill=X)

def clear_tree_view():
    for item in tree.get_children():
        tree.delete(item)
    matches_details.clear()


def running():
    selected_date = date_chooser.entry.get()
    if selected_date:
        time_label.config(text=f'Getting the matches for {selected_date}')
        clear_tree_view()
        Thread(target=get_main_page).start()
    else:
        Messagebox.show_error('Please select a valid date','Error')




def get_main_page():
    try:
        page= requests.get(f'https://www.yallakora.com/match-center/%D9%85%D8%B1%D9%83%D8%B2-%D8%A7%D9%84%D9%85%D8%A8%D8%A7%D8%B1%D9%8A%D8%A7%D8%AA?date={date_chooser.entry.get()}')
        src = page.content
        soup = BeautifulSoup(src , 'lxml')
        championships = soup.find_all('div', {'class':'matchCard'})
        for championship in championships:
            get_main_info(championship)
        time_label.config(text=f'Here are matches of {date_chooser.entry.get()}')
        root.after(0,ask_to_save)


    except Exception as e:
        mb = Messagebox.ok(f'Unexpected error happened :( \n{e}','Error')
        
        

def get_main_info(championship):
    
    tournament = championship.find('h2').text.strip()
    matches = championship.find_all('div',{'class':'liItem'})
    for match in matches:
        channel = match.find('div',{'class':'channel'}).text.strip() if match.find('div',{'class':'channel'}) else 'Not found'

        team_A_name = match.find('div',{'class':'teams teamA'}).text.strip()
        team_B_name = match.find('div',{'class':'teams teamB'}).text.strip()
        time = match.find('span',{'class':'time'}).text.strip()
        score = match.find_all('span',{'class':'score'})
        match_result = f'{score[0].text.strip()} - {score[1].text.strip()}'
        tree.insert('',END,values=(tournament,team_A_name,team_B_name,time,channel,match_result))
        matches_details.append({'Tournament':tournament,'First team':team_A_name,'Second team': team_B_name, 'Time': time,'Channel':channel, 'Score': match_result})



def ask_to_save():
    save_csv_mb = Messagebox.yesno('Save results as a csv file ?','Save CSV')
    if save_csv_mb == 'Yes':
        keys = matches_details[0].keys()
        path = filedialog.askdirectory()
        if not path:
            Messagebox.show_error('Please choose a valid directory to save file ','Error')
        else:
            old_save_date = date_chooser.entry.get()
            new_save_date = old_save_date.replace('/','-')
            filepath = os.path.join(path,f'mathches_of_{new_save_date}.csv')
            with open(filepath,'w') as output_file:
                dict_writer = csv.DictWriter(output_file, keys)
                dict_writer.writeheader()
                dict_writer.writerows(matches_details)
            Messagebox.ok('Saved successfully :)','Done')

        


date_chooser = DateEntry(root, firstweekday=5)
date_chooser.pack(pady=10)


button_style = Style()
button_style.configure('my.Outline.TButton', font=('helvetica', 13))


action_button = Button(root, text='Get Matches', style='my.Outline.TButton', width=13,command=running)
action_button.pack(pady=10)



time_label = Label(root, text=f'', font=('helvetica', 14))
time_label.pack(pady=20)

# Create a frame for the Treeview to control its size and position
tree_frame = Frame(root)
tree_frame.pack(pady=20, padx=20, fill=BOTH, expand=True)

tree = Treeview(tree_frame, columns=('Tournament', 'First_team', 'Second_team', 'Time', 'Channel', 'Score'), show='headings')
tree.pack(fill=BOTH, expand=True)

tree.heading('Tournament', text='Tournament')
tree.heading('First_team', text='First team')
tree.heading('Second_team', text='Second team')
tree.heading('Time', text='Time')
tree.heading('Channel', text='Channel')
tree.heading('Score', text='Score')




root.mainloop()
