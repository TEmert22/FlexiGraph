#import GUI
import tkinter as tk
#Import finance module
import yfinance as yf
#Import graph processing modules
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pyautogui
#Import word processing modules
import nltk
from nltk import pos_tag, RegexpParser
from nltk.tokenize import word_tokenize

#Define Stock Class
class Stock:
    def __init__(self, ticker):
        self.ticker = ticker
        self.data = yf.Ticker(ticker)
        self.price_data = self.data.history(period='1y', interval='1d')
        self.summary = self.data.info['longBusinessSummary']
        #Discovering name from description
        pos_tagged_summary = pos_tag(word_tokenize(self.summary))
        noun_parser = RegexpParser('NS: {<NNP|NNPS>+}')
        parsed_summary = noun_parser.parse(pos_tagged_summary)
        #Assign first match as the name
        for subtree in parsed_summary:
            if isinstance(subtree, nltk.Tree) and subtree.label() == 'NS':
                self.name = ' '.join([word for word, pos in subtree.leaves()])
                break
            
    def __str__(self):
        return self.summary

    #Plot candle chart
    def candle_chart(self, tk_window):
        #Reset canvas to display new graph
        global canvas
        try:
            canvas.get_tk_widget().destroy()
        except:
            canvas.destroy()
        #Define plot resolution
        #Screen_size = (width, height)
        screen_size = pyautogui.size()
        dpi = 120
        #Initialise Plot and set outer plot to black
        graph_figure = Figure(figsize=(screen_size[0]/dpi, screen_size[1]/dpi), dpi=dpi)
        graph = graph_figure.add_subplot(111)
        graph_figure.set_facecolor(col_black)
        #Define graph appearance
        bullish = self.price_data[self.price_data.Close >= self.price_data.Open]
        bearish = self.price_data[self.price_data.Close < self.price_data.Open]
        candle_width = 0.8
        wick_width = candle_width*0.15
        #Plot bullish periods on chart
        #candle - top wick - bottom wick
        graph.bar(bullish.index, bullish.Close-bullish.Open, candle_width, bottom=bullish.Open, color=col_green)
        graph.bar(bullish.index, bullish.High-bullish.Close, wick_width, bottom=bullish.Close, color=col_green)
        graph.bar(bullish.index, bullish.Open-bullish.Low, wick_width, bottom=bullish.Low, color=col_green)
        #Plot bearish periods on chart
        #candle - top wick - bottom wick
        graph.bar(bearish.index, bearish.Open-bearish.Close, candle_width, bottom=bearish.Close, color=col_red)
        graph.bar(bearish.index, bearish.High-bearish.Open, wick_width, bottom=bearish.Open, color=col_red)
        graph.bar(bearish.index, bearish.Close-bearish.Low, wick_width, bottom=bearish.Low, color=col_red)
        graph.tick_params(axis='x', colors = col_white, rotation = 30, labelsize = 9)
        graph.tick_params(axis='y', colors = col_white, labelsize = 9)
        #BG colour set to dark blue - Title - Grid
        graph.set_facecolor(col_darkblue)
        graph.set_title(f'{self.name} price history (1Y period)', color= col_white)
        graph.grid(True, color = col_grey, alpha=0.3)
        canvas = FigureCanvasTkAgg(graph_figure, master = tk_window)
        canvas.draw()
        canvas.get_tk_widget().pack(side = tk.BOTTOM, fill=tk.BOTH, expand=True)

#Function checks whether ticker exists
def tickerExists(ticker):
    if ticker == '':
        return False
    else:
        ticker_test = yf.Ticker(ticker).history(period='5d', interval='1d')
        if len(ticker_test) > 1:
            return True
        else:
            return False
        

#Function to return failed results to the user
def tickerHandling(*args):
    ticker = stock_name.get()
    if returnframe.winfo_viewable():
        returnframe.grid_remove()
    if tickerExists(ticker):
        stock = Stock(ticker)
        stock.candle_chart(graphframe)
    else:
        if ticker == '':
            return_label.configure(text='Error: Please input a ticker before searching.')
        else:
            return_label.configure(text=f'Error: ticker {ticker.upper()} is not available or does not exist.')
        returnframe.grid(column=0, row=1, sticky='EW')
        returnframe.grid_columnconfigure(0, weight=1)
        delete_return_frame()

#Function to stop scheduled deletion of error message frame, letting it be updated instead
delete_frame_id = ''
def delete_return_frame(*args):
    global delete_frame_id
    if delete_frame_id != '':
        root.after_cancel(delete_frame_id)
    delete_frame_id = root.after(5000, returnframe.grid_remove)           

#WINDOW CREATION SECTION
#Window Styling
default_font = ('calibre', 10, 'bold')
error_font = ('calibre', 15, 'bold')
col_white = '#FFFFFF'
col_grey = '#9DA39A'
col_black = '#000000'
col_darkblue = '#233D4D'
col_red = '#FF495C'
col_green = '#5AFF15'

#Create the window
root = tk.Tk()
root.title('FlexiGraph')
root.geometry('500x500')
root.configure(bg=col_black)
icon = tk.PhotoImage(file='icon.png')
root.iconphoto(True, icon)

#Create the main frames
searchframe = tk.Frame(root, bg=col_darkblue)
searchframe_elements = tk.Frame(searchframe, bg = col_darkblue)
returnframe = tk.Frame(root, bg=col_darkblue)
graphframe = tk.Frame(root, bg=col_black)
#Frame Layout
searchframe.grid(column=0, row=0, sticky = 'EW')
searchframe_elements.grid(column=1, row=0)
searchframe.grid_columnconfigure(0, weight=1)
searchframe.grid_columnconfigure(1, weight=0)
searchframe.grid_columnconfigure(2, weight=1)
graphframe.grid(column=0, row=2)
root.grid_rowconfigure(2,weight=1)
root.grid_columnconfigure(0, weight=1)

#Create search frame elements (search box, etc.) and variable to store results,
search_label = tk.Label(searchframe_elements, text='Stock Ticker:', font=default_font, fg=col_white, bg=col_darkblue)
stock_name = tk.StringVar()
search_box = tk.Entry(searchframe_elements, textvariable=stock_name, font=default_font)
search_button = tk.Button(master = searchframe_elements, command = tickerHandling, height=1, width=8, text='Search', bd=2, bg=col_grey, fg=col_white, activebackground=col_white, activeforeground=col_black)
search_label.grid(row=0,column=0, pady=10, padx=(10,5))
search_box.grid(row=0,column=1, pady=10)
search_button.grid(row=0,column=2,pady=10, padx=18)

#Create return frame elements
return_label = tk.Label(returnframe, text = '', font=error_font, fg=col_red, bg=col_darkblue)
return_label.grid(sticky='EW')

#Create graph frame elements
canvas = tk.Canvas(graphframe, width=0, height=0)

#Initialise GUI loop
search_box.focus()
root.mainloop()
