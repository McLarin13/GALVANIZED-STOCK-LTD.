from customtkinter import * #UI Library
from PIL import Image, ImageTk  # Import ImageTk for displaying images
from bs4 import BeautifulSoup #Scraping Lib
import requests
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pytz
from datetime import datetime, time as dt_time
from tabulate import tabulate
import tkinter as tk
from tkinter import ttk
import webbrowser


def show():
    philippine_timezone = pytz.timezone('Asia/Manila')
    philippine_time = datetime.now(philippine_timezone)
    formatted_date = philippine_time.strftime("%Y-%m-%d")
    formatted_time = philippine_time.strftime("%H:%M:%S")
    print(f"Philippine Time \n{formatted_date}  {formatted_time} ")


    time = CTkLabel(master=app, text="Date", font=("Century Gothic", 12), text_color="WHITE")
    time.place(x=550, y=450)

    time = CTkLabel(master=app, text=formatted_date, font=("Century Gothic", 20), text_color="WHITE")
    time.place(x=550, y=480)

    time = CTkLabel(master=app, text=formatted_time, font=("Century Gothic", 20), text_color="WHITE")
    time.place(x=715, y=480)

    time = CTkLabel(master=app, text="Time", font=("Century Gothic", 12), text_color="WHITE")
    time.place(x=715, y=450)

    html_text = requests.get("https://finance.yahoo.com/most-active").text
    soup = BeautifulSoup(html_text, features='html.parser')

    #VALUES
    difference_change = soup.find_all("span", class_=lambda c: c in ["C($positiveColor)", "C($negativeColor)"])
    change_diff = [difference.text for difference in difference_change]
    final_change_float = [float(dif.replace("+", "")) for dif in change_diff if "%" not in dif]
    new_final_percent_float = final_change_float[6:]
    pdchange = pd.DataFrame(new_final_percent_float)

    #PERCENTAGE
    difference_percent = soup.find_all("span", class_=lambda c: c in ["C($positiveColor)", "C($negativeColor)"])
    percentage_diff = [differenceperc.text for differenceperc in difference_percent]
    final_percent_float = [float(dif.replace("+", "").replace("%", "").replace("(", "").replace(")", ""))
                           for dif in percentage_diff if "%" in dif]

    new_final_percent_float = final_percent_float[6:]

    pdpercent = pd.DataFrame(new_final_percent_float)

    values = []
    fin_streamers = soup.find_all('fin-streamer')
    for streamer in fin_streamers:
        values.append(streamer['value'])


    #PRICE AND VOLUME
    Market_Price = values[18::5]
    pdMP = pd.DataFrame(Market_Price)

    Market_Volume = values[21::5]
    pdMV = pd.DataFrame(Market_Volume)

    table_co = soup.find_all("td", class_="Va(m) Ta(start) Px(10px) Fz(s)")
    all_co = [tables.text for tables in table_co]

    #DATA FRAMING
    pdcompany = pd.DataFrame(all_co)
    combined_data1 = pd.concat([pdcompany, pdchange], axis=1)
    combined_data1.columns = ["Company Name", "Value Change"]

    combine_data2 = pd.concat([pdcompany, pdpercent], axis=1)
    combine_data2.columns = ["Args", "Percent Change"]

    combine_data3 = pd.concat([pdcompany, pdMP], axis=1)
    combine_data3.columns = ["Args", "Price(Interday)"]

    combine_data4 = pd.concat([pdcompany, pdMV], axis=1)
    combine_data4.columns = ["Args", "Buying Volume"]

    all_merge_close_2 = pd.merge(combined_data1, combine_data2, left_on="Company Name", right_on="Args").drop("Args", axis=1)
    all_merge_close_1 = pd.concat([all_merge_close_2, combine_data3], axis=1)
    ALL_MERGE_CLOSE_DEFAULT = pd.concat([all_merge_close_1, combine_data4], axis=1).drop("Args", axis=1)
    ALL_MERGE_CLOSE_DEFAULT.index = pd.RangeIndex(start=1, stop=len(table_co)+ 1, step=1)


    view = ttk.Treeview(master=frame, columns=["Company Name", "Value Change", "Percent Change", "Price(Interday)"],
                        show="headings", style="Custom.Treeview")



    #TREE VIEW TABLE
    app_style = ttk.Style()
    app_style.theme_use('clam')
    app_style.configure("Custom.Treeview", background="black", foreground="black", fieldbackground="black",
                        font=("Arial", 10))

    app_style.configure("Custom.Treeview.Heading", background="black", foreground="black", font=("Arial", 10, "bold"))

    view.configure(style='Treeview')
    style = ttk.Style()
    style.configure('Treeview', rowheight=30)

    view.heading("Company Name", text="Company Name")
    view.heading("Value Change", text="Value Change")
    view.heading("Percent Change", text="Percent Change")
    view.heading("Price(Interday)", text="Price(Interday)")
    view.place(relx=0.5, rely=0.5, relh=0.995, relw=0.995, anchor="center")

    view.tag_configure('positive', foreground='green', font=(5))
    view.tag_configure('negative', foreground='red', font=(5))

    for index in range(len(ALL_MERGE_CLOSE_DEFAULT) - 1, -1, -1):
        row = ALL_MERGE_CLOSE_DEFAULT.iloc[index]
        columna = row["Company Name"]
        columnb = row["Value Change"]
        columbc = row["Percent Change"]
        columnd = row["Price(Interday)"]

        tagb = 'positive' if float(columnb) > 0 else 'negative'
        tagbc = 'positive' if float(columbc) > 0 else 'negative'

        view.insert(parent="", values=[columna, columnb, columbc, columnd], index=0, tags=(tagb, tagbc))

    return ALL_MERGE_CLOSE_DEFAULT


def maxperc():
    ALL_MERGE_CLOSE_DEFAULT = show()  # Assuming show() is a function that returns the dataframe
    top_5_percent = ALL_MERGE_CLOSE_DEFAULT.sort_values(by="Percent Change", ascending=False).head(5).drop(
        ["Value Change", "Price(Interday)", "Buying Volume"], axis=1)

    positive_values = top_5_percent[top_5_percent['Percent Change'] >= 0]
    negative_values = top_5_percent[top_5_percent['Percent Change'] < 0]

    plt.figure()

    positive_bars = plt.bar(positive_values['Company Name'], positive_values['Percent Change'], color='g',
                            label='Positive')
    negative_bars = plt.bar(negative_values['Company Name'], negative_values['Percent Change'], color='r',
                            label='Negative')
    # GPAPH SPECS
    plt.xlabel('Company Name')
    plt.ylabel('Percent Change')
    plt.title('Top 5 Percent Change (Positive and Negative)')
    plt.legend()
    plt.xticks(rotation=30)

    # BAR VAL
    for bar in positive_bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 2), va='bottom')

    for bar in negative_bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 2), va='bottom')


    plt.show()
    return plt.gcf()


def minperc():
    ALL_MERGE_CLOSE_DEFAULT = show()  # Assuming show() is a function that returns the dataframe
    min_5_percent = ALL_MERGE_CLOSE_DEFAULT.sort_values(by="Percent Change", ascending=True).head(5).drop(
        ["Value Change", "Price(Interday)", "Buying Volume"], axis=1)

    positive_values = min_5_percent[min_5_percent['Percent Change'] >= 0]
    negative_values = min_5_percent[min_5_percent['Percent Change'] < 0]


    plt.figure()

    positive_bars = plt.bar(positive_values['Company Name'], positive_values['Percent Change'], color='g',
                            label='Positive')
    negative_bars = plt.bar(negative_values['Company Name'], negative_values['Percent Change'], color='r',
                            label='Negative')

    plt.xlabel('Company Name')
    plt.ylabel('Percent Change')
    plt.title('Bottom 5 Percent Change (Positive and Negative)')
    plt.legend()
    plt.xticks(rotation=30)


    for bar in positive_bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 2), va='bottom')

    for bar in negative_bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 2), va='bottom')


    plt.show()
    return plt.gcf()


def maxval():
    ALL_MERGE_CLOSE_DEFAULT = show()  # Assuming show() is a function that returns the dataframe
    top_5_values = ALL_MERGE_CLOSE_DEFAULT.sort_values(by="Value Change", ascending=False).head(5).drop(
        ["Percent Change", "Price(Interday)", "Buying Volume"], axis=1)

    positive_values = top_5_values[top_5_values['Value Change'] >= 0]
    negative_values = top_5_values[top_5_values['Value Change'] < 0]


    plt.figure()

    positive_bars = plt.bar(positive_values['Company Name'], positive_values['Value Change'], color='g',
                            label='Positive')
    negative_bars = plt.bar(negative_values['Company Name'], negative_values['Value Change'], color='r',
                            label='Negative')


    plt.xlabel('Company Name')
    plt.ylabel('Value Change')
    plt.title('Top 5 Value Changes (Positive and Negative)')
    plt.legend()
    plt.xticks(rotation=30)


    for bar in positive_bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 2), va='bottom')

    for bar in negative_bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 2), va='bottom')


    plt.show()
    return plt.gcf()


def minval():
    ALL_MERGE_CLOSE_DEFAULT = show()  # Assuming show() is a function that returns the dataframe
    min_5_values = ALL_MERGE_CLOSE_DEFAULT.sort_values(by="Value Change", ascending=True).head(5).drop(
        ["Percent Change", "Price(Interday)", "Buying Volume"], axis=1)

    positive_values = min_5_values[min_5_values['Value Change'] >= 0]
    negative_values = min_5_values[min_5_values['Value Change'] < 0]


    plt.figure()

    positive_bars = plt.bar(positive_values['Company Name'], positive_values['Value Change'], color='g',
                            label='Positive')
    negative_bars = plt.bar(negative_values['Company Name'], negative_values['Value Change'], color='r',
                            label='Negative')


    plt.xlabel('Company Name')
    plt.ylabel('Value Change')
    plt.title('Bottom 5 Value Changes (Positive and Negative)')
    plt.legend()
    plt.xticks(rotation=30)


    for bar in positive_bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 2), va='bottom')

    for bar in negative_bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 2), va='bottom')


    plt.show()
    return plt.gcf()



def open_link():
    url = "https://finance.yahoo.com/most-active"
    webbrowser.open(url)

def open_link1():
    url = "https://www.youtube.com/watch?v=p7HKvqRI_Bo"
    webbrowser.open(url)

def open_link2():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    webbrowser.open(url)


def open_link3():
    url = "https://finance.yahoo.com/"
    webbrowser.open(url)

app = CTk()
app.geometry("1200x700")
app.minsize(width=1200, height=700)
app.maxsize(width=1200,height=700)
app.title("GALVANIZED STOCKS")
set_appearance_mode("dark")


bg_image = Image.open("Galavanized Stocks Background.png")
bg_photo = ImageTk.PhotoImage(bg_image)


# BG
bg_label = CTkLabel(master=app, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)


#FRAME
frame = CTkFrame(app, width=730, height=400, fg_color="navy", border_width = 1, border_color= "white")
frame.place(x=450, y=30)


# COLLECT
btn = CTkButton(master=app, height=40, width=360, text="COLECT", corner_radius=67, fg_color="#0056b3",
                hover_color="#80aaff", border_color="#0056b3", border_width=2, command=show, text_color="white")
btn.place(x=50, y=380, )

# PHERIPHERAL BUTTONS
btnurl = CTkButton(master=app, height=40, width=150, text="Yahoo! Stocks", corner_radius=67, fg_color="#410093",
                   hover_color="#A98CC7", border_color="#410093", border_width=0, command=open_link, text_color="white")
btnurl.place(x=1095, y=480, anchor="center")

btnurllearn = CTkButton(master=app, height=40, width=150, text="Learn Trading", corner_radius=67, fg_color="#FF0000",
                   hover_color="#A98CC7", border_color="#410093", border_width=0, command=open_link1, text_color="white")
btnurllearn.place(x=1095, y=550, anchor="center")

btnurlscam = CTkButton(master=app, height=40, width=150, text="Free MONEY!", corner_radius=67, fg_color="#FF0000",
                   hover_color="#A98CC7", border_color="#410093", border_width=0, command=open_link2, text_color="white")
btnurlscam.place(x=1095, y=600, anchor="center")

btnurlnews = CTkButton(master=app, height=40, width=150, text="FINANCE NEWS", corner_radius=67, fg_color="navy",
                   hover_color="#A98CC7", border_color="#410093", border_width=0, command=open_link3, text_color="white")
btnurlnews.place(x=920, y=480, anchor="center")


#LABELS
textpmax = CTkLabel(master=app, text="PERCENTAGE", font=("Arial Black", 25), text_color="orange")
textpmax.place(x=50, y=100)

textVmax = CTkLabel(master=app, text="VALUE", font=("Arial Black", 25), text_color="cyan")
textVmax.place(x=50, y=230)


# Button for maximum percentage
btnmax = CTkButton(master=app, height=40, width=150, text="BEST", corner_radius=67, fg_color="#007700",
                   hover_color="#4CAF50", border_color="#007700", border_width=2, command=maxperc, text_color="white",font=("Helvetica", 20))
btnmax.place(x=130, y=170, anchor="center")

# Button for minimum percentage
btnmin = CTkButton(master=app, height=40, width=150, text="BOTTOM", corner_radius=67, fg_color="#990000",
                   hover_color="#FF5733", border_color="#990000", border_width=2, command=minperc, text_color="white", font=("Helvetica", 20))
btnmin.place(x=330, y=170, anchor="center")

# Button for maximum value
btnmaxv = CTkButton(master=app, height=40, width=150, text="BEST", corner_radius=67, fg_color="#007700",
                    hover_color="#4CAF50", border_color="#007700", border_width=2, command=maxval, text_color="white",font=("Helvetica", 20))
btnmaxv.place(x=130, y=300, anchor="center")

# Button for minimum value
btnminv = CTkButton(master=app, height=40, width=150, text="BOTTOM", corner_radius=67, fg_color="#990000",
                    hover_color="#FF5733", border_color="#990000", border_width=2, command=minval, font=("Helvetica", 20),
                    text_color="white")
btnminv.place(x=330, y=300, anchor="center")


app.mainloop()

