import requests
import tkinter as tk
from tkinter import ttk


# Function to fetch data from the Hypixel API
def fetch_bazaar_data():
	url = "https://api.hypixel.net/skyblock/bazaar"
	try:
		response = requests.get(url)
		response.raise_for_status()
		data = response.json()
		return data['products']
	except requests.RequestException as e:
		print(f"Error fetching data: {e}")
		return {}


# Function to process data and calculate profits
def calculate_profits(data, user_money):
	profits = []
	for item, details in data.items():
		if 'buy_summary' in details and 'sell_summary' in details and details['buy_summary'] and details[
			'sell_summary']:
			highest_buy_order = max(detail['pricePerUnit'] for detail in details['sell_summary'])
			lowest_sell_offer = min(detail['pricePerUnit'] for detail in details['buy_summary'])

			buy_price = highest_buy_order + 0.1
			sell_price = lowest_sell_offer - 0.1

			# Prevent unrealistic orders
			if sell_price > buy_price and sell_price <= 10 * buy_price:
				profit_per_item = sell_price - buy_price
				quantity = int(user_money / buy_price)
				total_profit = quantity * profit_per_item

				if total_profit > 0:
					total_profit_per_item = total_profit / quantity if quantity else 0
					profits.append((item, buy_price.__round__(2), sell_price.__round__(2),
									profit_per_item.__round__(2), quantity,
									total_profit, total_profit_per_item.__round__(2)))

	profits.sort(key=lambda x: x[5], reverse=True)
	return profits[:50]


# Function to update the Treeview with new data
def update_treeview(tree, data):
	for i in tree.get_children():
		tree.delete(i)
	for item in data:
		tree.insert('', 'end', values=item)


# Function to refresh data
def refresh_data(tree, money_entry):
	try:
		user_money = float(money_entry.get())
	except ValueError:
		print("Invalid money amount")
		return

	data = fetch_bazaar_data()
	profits = calculate_profits(data, user_money)
	update_treeview(tree, profits)


# Function to create the GUI
def create_gui():
	root = tk.Tk()
	root.title("Skyblock Bazaar Flipping Calculator")

	money_label = tk.Label(root, text="Enter Your Money:")
	money_label.pack(pady=5)

	money_entry = tk.Entry(root)
	money_entry.pack(pady=5)

	refresh_button = tk.Button(root, text="Calculate Profits", command=lambda: refresh_data(tree, money_entry))
	refresh_button.pack(pady=10)

	tree = ttk.Treeview(root, columns=(
		"Item Name", "Buy Order at", "Sell Offer at", "Profit per Item",
		"Quantity", "Total Profit", "Total Profit per Item"), show='headings')
	for col in tree["columns"]:
		tree.heading(col, text=col)

	tree.pack(expand=True, fill='both')

	return root


def main():
	root = create_gui()
	root.mainloop()


if __name__ == "__main__":
	main()
