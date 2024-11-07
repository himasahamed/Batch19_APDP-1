def best_selling_analysis(self):
        # Open the CSV file for reading
        with open('supermarket_sales2.csv', 'r') as file:
            reader = csv.reader(file)
            sales_data = list(reader)

        product_sales = {}

        for row in sales_data[1:]:
            product_id = row[2]  # Product ID
            sales_amount = float(row[7])  # Sales amount
            # Accumulate sales amount for each product
            if product_id in product_sales:
                product_sales[product_id] += sales_amount
            else:
                product_sales[product_id] = sales_amount

        # Sort products by total sales amount in descending order
        sorted_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)
        # Get the top 5 best-selling products
        top_products = [product[0] for product in sorted_products[:5]]
        print(top_products)
