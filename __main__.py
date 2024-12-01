from tkinter import *
import tkinter as tk
#Import finance module
import yfinance as yf
#Import maths modules
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk 
import pandas as pd
#Import word processing modules
import nltk
from nltk import pos_tag, RegexpParser
from nltk.tokenize import word_tokenize

#Define Stock Class
class Stock:
    def __init__(self, ticker):
        self.ticker = ticker
        self.data = yf.Ticker(ticker)
        self.price_data = self.data.history(period="1y", interval="1d")
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
        #Initialise Plot and set outer plot to black
        graph_figure = Figure(figsize=(10,10), dpi=80)
        graph = graph_figure.add_subplot(111)
        graph_figure.set_facecolor('#000000')
        #Define graph appearance
        bullish = self.price_data[self.price_data.Close >= self.price_data.Open]
        bearish = self.price_data[self.price_data.Close < self.price_data.Open]
        bullish_colour = "green"
        bearish_colour = "red"
        candle_width = 0.9
        wick_width = candle_width*0.15
        #Plot bullish periods on chart
        #candle - top wick - bottom wick
        graph.bar(bullish.index, bullish.Close-bullish.Open, candle_width, bottom=bullish.Open, color=bullish_colour)
        graph.bar(bullish.index, bullish.High-bullish.Close, wick_width, bottom=bullish.Close, color=bullish_colour)
        graph.bar(bullish.index, bullish.Open-bullish.Low, wick_width, bottom=bullish.Low, color=bullish_colour)
        #Plot bearish periods on chart
        #candle - top wick - bottom wick
        graph.bar(bearish.index, bearish.Open-bearish.Close, candle_width, bottom=bearish.Close, color=bearish_colour)
        graph.bar(bearish.index, bearish.High-bearish.Open, wick_width, bottom=bearish.Open, color=bearish_colour)
        graph.bar(bearish.index, bearish.Close-bearish.Low, wick_width, bottom=bearish.Low, color=bearish_colour)
        graph.tick_params(axis='x', colors = '#FFFFFF', rotation = 30, labelsize = 12)
        graph.tick_params(axis='y', colors = '#FFFFFF', labelsize = 15)        #BG colour set to dark blue - Title - Grid
        graph.set_facecolor("#233D4D")
        graph.set_title(f"{self.name} price history (1Y period)", color= '#FFFFFF')
        graph.grid(True, color = "#9DA39A")
        #Creating Tkinter Canvas which contains chart
        canvas = FigureCanvasTkAgg(graph_figure, master = tk_window)
        canvas.draw()
        canvas.get_tk_widget().grid(row=2,column=0)
        #canvas.get_tk_widget().pack(side = tk.BOTTOM, fill=tk.BOTH, expand=True)
        #Creating matplotlib toolbar
        toolbar = NavigationToolbar2Tk(canvas, tk_window)
        toolbar.update()
        canvas.get_tk_widget().pack()
#Function checks whether ticker exists
def tickerExists(ticker):
    if ticker == "":
        return False
    else:
        ticker_test = yf.Ticker(ticker).history(period='5d', interval='1d')
        if len(ticker_test) > 1:
            return True
        else:
            return False
#Window processing here
default_font = ('calibre',10,'bold')
return_label = None
#Function to return failed results to the user
def tickerHandling(ticker, tk_window):
    global return_label
    if return_label is not None:
        return_label.destroy()
    if tickerExists(ticker):
        stock = Stock(ticker)
        stock.candle_chart(tk_window)
    else:   
        if ticker == "":
            return_text = "Please input a ticker before searching."
        else:
            return_text = f"Error: ticker {ticker.upper()} does not exist."
    return_label= tk.Label(tk_window, text=return_text, font=default_font, fg="red")
    return_label.grid(row=1,column=0)

#Initialise Stock object 
#while True:
#    ticker_name = input("Ticker Search: ").upper()
#    if tickerExists(ticker_name):
#        stock = Stock(ticker_name)
#        break
#stock = Stock('GOOG')

#Create the window
window = Tk()
window.title('Stock Graph in Tkinter')
window.geometry('500x500')
#Create search box and variable to store results
stock_name = tk.StringVar()
search_label = tk.Label(window, text = "Stock: ", font=default_font)
search_box = tk.Entry(window, textvariable=stock_name, font=default_font)
search_button = Button(master = window,
                     command = lambda: tickerHandling(stock_name.get(), window),
                     height = 2,
                     width = 10,
                     text = "Search")
#Organising window elements using grid
search_label.grid(row=0,column=0)
search_box.grid(row=0,column=1)
search_button.grid(row=0,column=2)
window.mainloop()

