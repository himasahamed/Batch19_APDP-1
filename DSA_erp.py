import pandas as pd
from abc import ABC, abstractmethod
import dash
from dash import html
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


# Interface for data ingestion
class DataIngestionStrategy(ABC):
    @abstractmethod
    def ingest_data(self, file_path):
        pass

# Concrete class for CSV data ingestion
class CSVDataIngestion(DataIngestionStrategy):
    def ingest_data(self, file_path):
        return pd.read_csv(file_path)


# Context class for data ingestion
class DataIngestionContext:
    def __init__(self, strategy: DataIngestionStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: DataIngestionStrategy):
        self._strategy = strategy

    def ingest(self, file_path):
        return self._strategy.ingest_data(file_path)


class DataProcess(ABC):
    @abstractmethod
    def process_data(self, data):
        pass


class SalesTrendsOverTime(DataProcess):
    def process_data(self, data):
        # Ensure 'Date' is in datetime format
        data['Date'] = pd.to_datetime(data['Date'])

        # Group by year and month, then sum the sales
        grouped = data.groupby([data['Date'].dt.year.rename('Year'), data['Date'].dt.month.rename('Month')])[
            'Sales'].sum().reset_index(name='TotalSales')

        # Reconstructing the 'Date' column for ease of plotting
        grouped['Date'] = pd.to_datetime(grouped.assign(DAY=1)[['Year', 'Month', 'DAY']])

        # Ensure 'Date' is the first column if needed
        cols = ['Date'] + [col for col in grouped.columns if col != 'Date']
        return grouped[cols]


class ProfitAnalysisByCountry(DataProcess):
    def process_data(self, data):
        return data.groupby('Country')['Profit'].sum().reset_index()

class ProductPerformance(DataProcess):
    def process_data(self, data):
        return data.groupby('Product')[['Sales', 'Profit']].sum().reset_index()

class DiscountImpactOnSales(DataProcess):
    def process_data(self, data):
        return data[['Discount Band', 'Sales', 'Profit']]

class MonthlySalesDistribution(DataProcess):
    def process_data(self, data):
        data['Date'] = pd.to_datetime(data['Date'])
        return data.groupby(data['Date'].dt.month)['Sales'].sum().reset_index(name='MonthlySales')


class CountryWiseSalesDistribution(DataProcess):
    def process_data(self, data):
        return data.groupby('Country')['Sales'].sum().reset_index()


class CorrelationAnalysis(DataProcess):
    def process_data(self, data):
        # Updated function to handle non-convertible strings
        def convert_currency(val):
            try:
                # Removing currency symbols and commas
                val = val.replace(',', '').replace('$', '')
                # Converting to float or returning NaN for non-convertible values
                return float(val) if val.strip() != '' and val.strip() != '-' else np.nan
            except Exception as e:
                return np.nan  # Return NaN for any other conversion errors

        # Apply conversion on all specified columns
        for col in ['Units Sold', 'Manufacturing Price', 'Sale Price', 'Gross Sales', 'Discounts', 'Sales', 'Profit']:
            data[col] = data[col].apply(convert_currency)

        return data[['Units Sold', 'Manufacturing Price', 'Sale Price', 'Gross Sales', 'Discounts', 'Sales', 'Profit']].corr()



class DataProcessingContext:
    def __init__(self, strategy: DataProcess):
        self._strategy = strategy

    def set_strategy(self, strategy: DataProcess):
        self._strategy = strategy

    def process(self, data):
        return self._strategy.process_data(data)



# Load and process data
data_ingestion_context = DataIngestionContext(CSVDataIngestion())
sales_data = data_ingestion_context.ingest('Financials.csv')

data_processing_context = DataProcessingContext(SalesTrendsOverTime())
sales_trends_data = data_processing_context.process(sales_data)

data_processing_context.set_strategy(ProfitAnalysisByCountry())
profit_by_country_data = data_processing_context.process(sales_data)

data_processing_context = DataProcessingContext(ProductPerformance())
product_performance_data = data_processing_context.process(sales_data)

data_processing_context = DataProcessingContext(DiscountImpactOnSales())
discount_impact_data = data_processing_context.process(sales_data)

data_processing_context.set_strategy(CountryWiseSalesDistribution())
country_wise_sales_data = data_processing_context.process(sales_data)

data_processing_context.set_strategy(CorrelationAnalysis())
correlation_analysis_data = data_processing_context.process(sales_data)


# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div(children=[
    html.H1(children='ERP System Reporting tool for Sales Data'),

    # Column selector
    html.H3('Select Columns to Display:'),
    dcc.Checklist(
        id='column-selector',
        options=[{'label': col, 'value': col} for col in sales_data.columns],
        value=sales_data.columns.tolist(),  # Default to all columns
        inline=True,
    ),

    html.Button('Uncheck All', id='uncheck-all-button', n_clicks=0),

    # Data Table
    html.H2("ERP System's Data Table"),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in sales_data.columns],  # Columns to be updated in the callback
        data=sales_data.to_dict('records'),
        filter_action='native',  # Enable filtering
        sort_action='native',  # Enable sorting
        sort_mode='multi',  # Allow multi-column sorting
        page_action='native',  # Enable pagination
        page_size=10,  # Number of rows per page
    ),

    # Dynamic Chart
    dcc.Graph(id='dynamic-chart'),

    # Dropdown for selecting charts
    html.H3('Select a Chart to Display:'),
    dcc.Dropdown(
        id='chart-selector',
        options=[
            {'label': 'Sales Trends Over Time', 'value': 'sales-trends'},
            {'label': 'Profit Analysis by Country', 'value': 'profit-by-country'},
            {'label': 'Product Performance', 'value': 'product-performance'},
            {'label': 'Country-wise Sales Distribution', 'value': 'country-wise-sales'},
            {'label': 'Discount Impact on Sales', 'value': 'discount-impact'},
            {'label': 'Correlation Analysis', 'value': 'correlation-analysis'},
        ],
        value='sales-trends',  # Default value
    ),

    # Container for the selected chart
    html.Div(id='selected-chart-container'),

])

# Define callback to update table columns
@app.callback(
    Output('table', 'columns'),
    [Input('column-selector', 'value')]
)
def update_table_columns(selected_columns):
    return [{"name": i, "id": i} for i in selected_columns]

# Callback to uncheck all checklist options
@app.callback(
    Output('column-selector', 'value'),
    [Input('uncheck-all-button', 'n_clicks')],
    prevent_initial_call=True
)
def uncheck_all_columns(n_clicks):
    if n_clicks > 0:
        return []
    raise dash.exceptions.PreventUpdate

# Callback to update the dynamic chart based on the table's data and selected columns
@app.callback(
    Output('dynamic-chart', 'figure'),
    [Input('table', 'derived_virtual_data'),
     Input('column-selector', 'value')]
)
def update_dynamic_chart(rows, selected_columns):
    if rows is None:
        return {'data': []}

    dff = pd.DataFrame(rows)

    if selected_columns is None or not selected_columns:
        return {'data': []}

    data = []
    for column in selected_columns:
        if dff[column].dtype in ['float64', 'int64']:
            data.append({
                'x': dff.index,
                'y': dff[column],
                'type': 'line',
                'name': column
            })

    return {
        'data': data,
        'layout': {
            'title': 'Dynamic Data Chart',
            'xaxis': {'title': 'Index'},
            'yaxis': {'title': 'Value'}
        }
    }


@app.callback(
    Output('selected-chart-container', 'children'),
    Input('chart-selector', 'value')
)
def display_selected_chart(chart_value):
    if chart_value == 'sales-trends':
        return dcc.Graph(
            figure={
                'data': [{'x': sales_trends_data['Date'], 'y': sales_trends_data['TotalSales'], 'type': 'line'}],
                'layout': {'title': 'Sales Trends Over Time'}
            }
        )
    elif chart_value == 'profit-by-country':
        return dcc.Graph(
            figure={
                'data': [{'x': profit_by_country_data['Country'], 'y': profit_by_country_data['Profit'], 'type': 'bar'}],
                'layout': {'title': 'Profit Analysis by Country'}
            }
        )
    elif chart_value == 'product-performance':
        return dcc.Graph(
            figure={
                'data': [
                    {'x': product_performance_data['Product'], 'y': product_performance_data['Sales'], 'type': 'bar', 'name': 'Sales'},
                    {'x': product_performance_data['Product'], 'y': product_performance_data['Profit'], 'type': 'bar', 'name': 'Profit'},
                ],
                'layout': {
                    'title': 'Product Performance',
                    'barmode': 'stack'
                }
            }
        )
    elif chart_value == 'country-wise-sales':
        return dcc.Graph(
            figure={
                'data': [
                    {'x': country_wise_sales_data['Country'], 'y': country_wise_sales_data['Sales'], 'type': 'bar', 'name': 'Sales by Country'},
                ],
                'layout': {
                    'title': 'Country-wise Sales Distribution',
                    'xaxis': {'title': 'Country'},
                    'yaxis': {'title': 'Total Sales'}
                }
            }
        )
    elif chart_value == 'discount-impact':
        return dcc.Graph(
        figure={
            'data': [
                {'x': discount_impact_data['Discount Band'], 'y': discount_impact_data['Sales'], 'mode': 'markers', 'type': 'scatter', 'name': 'Discount Impact on Sales'},
            ],
            'layout': {
                'title': 'Discount Impact on Sales'
            }
        }
    )
    elif chart_value == 'correlation-analysis':
        return dcc.Graph(
            figure={
                'data': [
                    {
                        'z': correlation_analysis_data.values,
                        'x': correlation_analysis_data.columns,
                        'y': correlation_analysis_data.index,
                        'type': 'heatmap',
                        'colorscale': 'Viridis',
                    }
                ],
                'layout': {
                    'title': 'Correlation Analysis',
                    'xaxis': {'title': 'Variables'},
                    'yaxis': {'title': 'Variables'},
                }
            }
        )
    # Add more elif blocks for other chart values...
    else:
        return "Please select a chart."

if __name__ == '__main__':
    app.run_server(debug=True)
