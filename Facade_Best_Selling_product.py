import os
import pandas as pd
import plotly.graph_objects as go

# Data Injuction
class DataInjuctor:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self):
        # Load data from CSV file into a pandas DataFrame
        if os.path.exists(self.file_path):
            df = pd.read_csv(self.file_path)
            return df
        else:
            raise FileNotFoundError(f"The file {self.file_path} does not exist.")

# Subsystem 2: Analyzer
class ProductAnalyzer:
    def __init__(self, df):
        self.df = df

    def get_best_selling_products(self):
        # Get best-selling products (sorted by units sold)
        sorted_df = self.df.sort_values(by="units_sold", ascending=False)
        return sorted_df

# Subsystem 3: Plotter
class ChartPlotter:
    def __init__(self, df):
        self.df = df

    def plot_best_selling_products(self):
        # Create a bar chart using Plotly
        fig = go.Figure([go.Bar(x=self.df["product"], y=self.df["units_sold"])])
        fig.update_layout(
            title="Best-Selling Products",
            xaxis_title="Product",
            yaxis_title="Units Sold"
        )
        fig.show()

# Facade: Product Analysis System
class ProductAnalysisFacade:
    def __init__(self, file_path):
        self.data_loader = DataInjuctor(file_path)
        self.df = self.data_loader.load_data()
        self.analyzer = ProductAnalyzer(self.df)
        self.plotter = ChartPlotter(self.df)

    def analyze_and_plot_best_selling_products(self):
        best_selling_products = self.analyzer.get_best_selling_products()
        self.plotter.plot_best_selling_products()

# Usage
if __name__ == "__main__":
   
    file_path = input("Please enter the path to the sales data CSV file: ")
    file_path = os.path.abspath(file_path)

    try:
        analysis_system = ProductAnalysisFacade(file_path)
        analysis_system.analyze_and_plot_best_selling_products()
    except FileNotFoundError as e:
        print(e)
