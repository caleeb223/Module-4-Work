# %% [markdown]
# ## Part 1: Explore the Data
# 
# Import the data and use Pandas to learn more about the dataset.

# %%
import pandas as pd

df = pd.read_csv('Resources/client_dataset.csv')
df.head()

# %%
# View the column names in the data
print("Column Names:")
print(df.columns.tolist())

# %%
# Use the describe function to gather some basic statistics
print("\nBasic Statistics:")
print(df.describe(include='all'))

# %%
# Use this space to do any additional research
# and familiarize yourself with the data.
print("\nData Information:")
print(df.info())

# %%
# What three item categories had the most entries?
top_item_categories = df['category'].value_counts().head(3)
print("\nTop 3 Item Categories with the Most Entries:")
print(top_item_categories)


# %%
# For the category with the most entries, which subcategory had the most entries?
most_common_category = df['category'].value_counts().idxmax()
subcategory_with_most_entries = df[df['category'] == most_common_category]['subcategory'].value_counts().idxmax()
print(f"\nThe subcategory with the most entries in the most common category ({most_common_category}): {subcategory_with_most_entries}")


# %%
# Which five clients had the most entries in the data?
top_clients = df['client_id'].value_counts().head(5)
print("\nTop 5 Clients with the Most Entries:")
print(top_clients)

# %%
# Store the client ids of those top 5 clients in a list.
top_clients_list = top_clients.index.tolist()
print("\nTop 5 Client IDs:")
print(top_clients_list)

# %%
# How many total units (the qty column) did the client with the most entries order order?
client_with_most_entries = df['client_id'].value_counts().idxmax()
total_units_by_top_client = df[df['client_id'] == client_with_most_entries]['qty'].sum()
print(f"\nTotal units ordered by the client with the most entries ({client_with_most_entries}): {total_units_by_top_client}")


# %% [markdown]
# ## Part 2: Transform the Data
# Do we know that this client spent the more money than client 66037? If not, how would we find out? Transform the data using the steps below to prepare it for analysis.

# %%
# Create a column that calculates the subtotal for each line using the unit_price and the qty
df['subtotal'] = df['unit_price'] * df['qty']
print("\nAdded 'subtotal' column to the dataset.")


# %%
# Create a column for shipping price.
# Assume a shipping price of $7 per pound for orders over 50 pounds and $10 per pound for items 50 pounds or under.
df['shipping_price'] = df['unit_weight'].apply(
    lambda x: 7 * x if x > 50 else 10 * x
)
print("\nAdded 'shipping_price' column to the dataset.")



# %%
# Create a column for the total price using the subtotal and the shipping price along with a sales tax of 9.25%
df['total_price'] = df['subtotal'] + df['shipping_price']
df['total_price'] *= 1.0925  # Applying 9.25% sales tax
print("\nAdded 'total_price' column to the dataset, including sales tax.")

# %%
# Create a column for the cost of each line using unit cost, qty, and
# shipping price (assume the shipping cost is exactly what is charged to the client).
df['line_cost'] = (df['unit_cost'] * df['qty']) + df['shipping_price']
print("\nAdded 'line_cost' column to the dataset.")



# %%
# Create a column for the profit of each line using line cost and line price
df['line_profit'] = df['total_price'] - df['line_cost']
print("\nAdded 'line_profit' column to the dataset.")


# Confirm your work: Validate calculations for the given Order IDs and their expected total prices

# Define the order IDs and their expected total prices
expected_totals = {
    2742071: 152811.89,
    2173913: 162388.71,
    6128929: 923441.25
}

# Calculate the total prices for the given order IDs
calculated_totals = df[df['order_id'].isin(expected_totals.keys())].groupby('order_id')['total_price'].sum()

# Compare the calculated totals with the expected totals
print("\nValidation Results for Order Totals:")
for order_id, expected_total in expected_totals.items():
    calculated_total = calculated_totals.get(order_id, 0)  # Get calculated total or default to 0
    match = abs(calculated_total - expected_total) < 0.01  # Allow small margin for rounding
    print(f"Order ID {order_id}:")
    print(f"  Calculated Total: ${calculated_total:,.2f}")
    print(f"  Expected Total:   ${expected_total:,.2f}")
    print(f"  Match:            {'Yes' if match else 'No'}")
# %%
# Check your work using the totals above
print("\nChecking totals for validation:")
print("Total revenue:", df['total_price'].sum())
print("Total cost:", df['line_cost'].sum())
print("Total profit:", df['line_profit'].sum())

# %% [markdown]
# ## Part 4: Summarize and Analyze
# Use the new columns with confirmed values to find the following information.

# %%
# How much did each of the top 5 clients by quantity spend? Check your work from Part 1 for client ids.
top_5_clients_spending = df[df['client_id'].isin(top_clients_list)].groupby('client_id')['total_price'].sum()
print("\nTop 5 Clients by Total Spending:")
print(top_5_clients_spending)


# %%
# Create a summary DataFrame showing the totals for the for the top 5 clients with the following information:
# total units purchased, total shipping price, total revenue, and total profit. 
summary_df = df[df['client_id'].isin(top_clients_list)].groupby('client_id').agg(
    total_units_purchased=('qty', 'sum'),
    total_shipping_price=('shipping_price', 'sum'),
    total_revenue=('total_price', 'sum'),
    total_profit=('line_profit', 'sum')
).reset_index()

# %%
# Format the data and rename the columns to names suitable for presentation
summary_df.rename(columns={
    'client_id': 'Client ID',
    'total_units_purchased': 'Total Units Purchased',
    'total_shipping_price': 'Total Shipping Price',
    'total_revenue': 'Total Revenue',
    'total_profit': 'Total Profit'
}, inplace=True)

# Define the money columns
money_columns = ['Total Shipping Price', 'Total Revenue', 'Total Profit']

# Define a function that converts a dollar amount to millions
def currency_format_millions(value):
    return round(value / 1_000_000, 2)

# Apply the currency_format_millions function to only the money columns
for col in money_columns:
    summary_df[col] = summary_df[col].apply(currency_format_millions)

# Rename the columns to reflect the change in the money format
summary_df.rename(columns={
    'Total Shipping Price': 'Total Shipping Price (millions)',
    'Total Revenue': 'Total Revenue (millions)',
    'Total Profit': 'Total Profit (millions)'
}, inplace=True)




# %%
# Sort the updated data by "Total Profit (millions)" form highest to lowest and assign the sort to a new DatFrame.
sorted_summary_df = summary_df.sort_values(by='Total Profit (millions)', ascending=False)


# %%
print("\nSorted Summary DataFrame (Top 5 Clients):")
print(sorted_summary_df)


