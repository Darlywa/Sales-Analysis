#import the required modules
import pandas as pd
import os
import matplotlib.pyplot as plt
import warnings
from itertools import combinations
from collections import Counter
import streamlit as st
import plotly.graph_objs as go

warnings.filterwarnings("ignore")

st.set_page_config(page_title="Sales Analysis Canvas", layout="wide")

text = """
Stormed through an old and insightful Data Science analysis exercise on a randomly generated sales data posted by Keith Galli. 
The author used exploratory data analysis to provide answers to pertinent questions on the dataset.
The data structure is close to those seen in the real-world, as the data is in small chunks.

The exercises in this notebook will replicate the work with more visualizations where necessary. 
The questions to answer from the data are:

* What was the best month for sales and how much was earned?
* What city sold the most product?
* What time is best for advertisement to maximize the likelihoods of buying these products?
* What products are most often sold together?
* What product sold the most and why?

A look at the questions shows that these tasks are quite interesting and match the standard of most Data Science interview questions.
"""

# Task 1: Read and merge all the monthly sales data
def merge(folder_dir: str):
    """The function will read and merge all the monthly sales data. Finally write the merged
    file to disk volume for further analysis.
    Parameters:
    ===========
    input: str

    return: None
    """
    file_paths = os.listdir(folder_dir)
    all_monthly_sales = pd.DataFrame() #define an empty dataframe to contain the monthly sales
    for file in file_paths:
        monthly_sales = pd.read_csv(folder_dir + file)
        all_monthly_sales = pd.concat([all_monthly_sales, monthly_sales], axis = 0)
    
    #write the merged data to persistent disk for further analysis
    all_monthly_sales.to_csv("./all_monthly_sales.csv", index=False)
    return None

def get_city(address):
    city = address.split(",")[1]
    state = address.split(",")[2][1:3]
    return f"{city} ({state})"

@st.cache_data
def clean(data_path: str):
    """The function cleans the data
    Parameters:
    input: str
    
    return: pd.Dataframe
    """
    all_data = pd.read_csv(data_path)

    #make a new column to contain the months
    all_data["Month"] = all_data["Order Date"].str[0:2]

    #find the row(s) that contains "Or" and exclude it from the data
    all_data = all_data[all_data["Month"] != "Or"]

    #the data contains nan: find the rows with the nan values and drop them
    nan_df = all_data[all_data.isna().any(axis=1)] #just to confirm the presence of nan

    #drop the nan
    all_data = all_data.dropna(how="all")

    #convert the month column to integer: 
    all_data["Month"] = all_data["Month"].astype("int32")

    #create a sales column
    all_data["Sales"] = pd.to_numeric(all_data["Quantity Ordered"]) * pd.to_numeric(all_data["Price Each"])

    #extract the city
    all_data["City"] = all_data["Purchase Address"].apply(lambda x: get_city(x))

    #convert the Order Date column to datetime column
    all_data["Order Date"] = pd.to_datetime(all_data["Order Date"])
    
    #create an hour column
    all_data["Hour"] = all_data["Order Date"].dt.hour

    all_data["Quantity Ordered"] = all_data["Quantity Ordered"].astype("int32")

    all_data["Price Each"] = pd.to_numeric(all_data["Price Each"])

    print("Data cleaned!")
    
    return all_data

if os.path.isfile("all_monthly_sales.csv"):
    print("The dataset has been merged.")
else:
    merge(folder_dir = "./Sales_Data/")
    print("Data merged!")

all_data = clean(data_path="all_monthly_sales.csv")

# Define sidebar elements
with st.sidebar:
    #create an empty sidebar
    st.write("")
   

#App title
st.header("Sales Analysis")
st.markdown("""
    <hr style="border: 1px solid #000;">
    """, unsafe_allow_html=True)
st.write("""This is just a canvas to represent the insights obtained from EDA questions using graph. The analysis was carried out
         on a 12 months sale's reports. The questions and the answers gotten from the dataset are quite challenging and interesting. For more details,
         kindly check the Github repository.
        Github: https://github.com/Darlywa/Sales-Analysis.git
         """)


st.subheader("Task 1: The best month for sale and how much was earned?")
#group the dataframe by month sum the sales
result = all_data.groupby(by=["Month"], as_index=False).agg({"Sales": "sum"})

#visualise the result using a bar chart
months_names = {1: "Jan", 2: "Feb", 3:"Mar", 4: "Apr", 5:"May", 6:"Jun", 7:"Jul", 8:"Aug", 9:"Sep", 10: "Oct", 11:"Nov", 12:"Dec"}
months = result["Month"].to_list()
month_labels = [months_names[month] for month in months]

#plot the bar chart
# create the traces
trace1 = go.Bar(x=month_labels, y=result["Sales"], name="Sales Amount in USD Dollars", marker=dict(color="blue"))
# set the layout
layout = go.Layout(title="Monthly Sales", xaxis=dict(title="Months", tickangle=-45), yaxis=dict(title="Sales Amount in USD Dollars", color="blue"))
# create the figure
fig = go.Figure(data=[trace1], layout=layout)
st.plotly_chart(fig)

comments = """The best month of sales was december, probably because of Christmas season."""
st.write(comments)

#draw horizontal line
st.markdown("""
    <hr style="border: 1px solid #000;">
    """, unsafe_allow_html=True)

st.subheader("Task 2: What city had the highest number of sales")
#groupby the city and sum the sales
result = all_data.groupby("City", as_index=False)["Sales"].sum()

#visualise the result
# create the traces
trace1 = go.Bar(x=result["City"], y=result["Sales"], name="Sales Amount in USD Dollars", marker=dict(color="blue"))
# set the layout
layout = go.Layout(title="City Sales", xaxis=dict(title="City Names", tickangle=-45), yaxis=dict(title="Sales Amount in USD Dollars", color="blue"))
# create the figure
fig = go.Figure(data=[trace1], layout=layout)
st.plotly_chart(fig)
comments = "The city with the highest sales is San Francisco (CA)."
st.write(comments)

#draw horizontal line
st.markdown("""
    <hr style="border: 1px solid #000;">
    """, unsafe_allow_html=True)

st.subheader("Task 3: What time is best for advertisement to maximize the likelihoods of buying these products?")
result = all_data.groupby("Hour", as_index=False)["Order ID"].count()

#visualise the result
# create the traces
trace1 = go.Scatter(x=result["Hour"], y=result["Order ID"], name="Order Counts", mode="lines+markers")
# set the layout
layout = go.Layout(title="Order Count Progression in Hours", xaxis=dict(title="Hours"), yaxis=dict(title="Order Counts"))
# create the figure
fig = go.Figure(data=[trace1], layout=layout)
st.plotly_chart(fig)

comments = """From the graph, the highest number of orders were made around 11am to 12 Noon and 7pm (19). 
Thus, the maximum likelihood time to place an advert should be around 10 to 11 am or around 5:00pm to 6:00pm 
to maximise the peak periods seen in order count.
"""
st.write(comments)

#draw horizontal line
st.markdown("""
    <hr style="border: 1px solid #000;">
    """, unsafe_allow_html=True)

st.subheader("Task 4: What products are most often sold together?")
#Products sold together have the same order id: filter all the transactions with duplicates id
df = all_data[all_data["Order ID"].duplicated(keep=False)] #the keep arguments to keep either the first or second duplicate. When set to false, it keeps all the duplicates

#group the products in a column named grouped
df["Grouped"] = df.groupby("Order ID")["Product"].transform(lambda x: ",".join(x))

#filter the Order id and the grouped column and drop the duplicates
df = df[["Order ID", "Grouped"]].drop_duplicates()

count = Counter()
for row in df["Grouped"]:
    row_list = row.split(",") #split the row into 2
    # Convert combinations to tuples (hashable) before using in Counter
    count.update(Counter(tuple(comb) for comb in combinations(row_list, 2)))

products, frequency= [], []
for key, value in count.most_common(10):
    products.append(key)
    frequency.append(value)

products = [f"({product1}, {product2})" for product1, product2 in products]
# create the traces
trace1 = go.Bar(x=products, y=frequency, name="Frequency (Count)", marker=dict(color="blue"))
# set the layout
layout = go.Layout(title="10 Most Product's Sold Together", xaxis=dict(title="Products", tickangle=-45), yaxis=dict(title="Frequency (Count)", color="blue"), height=500)
# create the figure
fig = go.Figure(data=[trace1], layout=layout)
st.plotly_chart(fig)
comments = """The most frequent products ordered together were 'iPhone' and 'Lightning Charging Cable."""
st.write(comments)

#draw horizontal line
st.markdown("""
    <hr style="border: 1px solid #000;">
    """, unsafe_allow_html=True)

st.subheader("Task 5: What product sold the most and why?")

#To find out why? lets overlay the price of the products on the graph
#groupby product and sum the quantity ordered
quantity_ordered = all_data.groupby("Product")["Quantity Ordered"].sum()

#visualise the quantity ordered
products = [product for product, df in all_data.groupby("Product")]

#get the average price of the products
prices = all_data.groupby("Product")["Price Each"].mean()

# create the traces
trace1 = go.Bar(x=products, y=quantity_ordered, name="Quantity Ordered", marker=dict(color="blue"))
trace2 = go.Scatter(x=products, y=prices, name="Prices", yaxis="y2", mode="lines+markers", line=dict(color="red"))

# set the layout
layout = go.Layout(title="Price Overlayed on Quantity Ordered", xaxis=dict(title="Products", tickangle=-45), yaxis=dict(title="Quantity Ordered", color="blue"), yaxis2=dict(title="Prices", color="red", overlaying="y", side="right"))

# create the figure
fig = go.Figure(data=[trace1, trace2], layout=layout)
st.plotly_chart(fig)
comments = """The most sold product was AAA-Batteries(4-pack) and it might be because of price. When compared with other products
the price seem relatively low. """
st.write(comments)

st.write("Reference: Keith Galli: Reference: https://www.youtube.com/watch?v=eMOA1pPVUc4")
