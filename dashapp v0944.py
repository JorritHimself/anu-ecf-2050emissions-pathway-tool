# Packages
import pandas as pd
import numpy as np
import xlrd # Required dependency for pd.read_excel
import re # for some string manipulation with regex
import ast
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

### Import the prepped input data
df_full = pd.read_csv('./db/preppeddata.csv')
### Import the picker settings
df_picker_in = pd.read_excel('./db/inputpickerlist.xlsx', sheet_name="pickersettings")

# Sort sectors with LULUCF at the bottom, others on top
df_full['sectorsorted']=df_full['sector']
df_full.loc[(df_full['sector']=='LULUCF'), 'sectorsorted'] = '0 LULUCF'
df_full.loc[(df_full['sector']=='Electricity generation'), 'sectorsorted'] = '1 Electricity generation'
df_full.loc[(df_full['sector']=='Residential'), 'sectorsorted'] = '2 Residential'
df_full = df_full.sort_values(['sectorsorted', 'year'], ascending=[True, True])

# Define list of states
statelist = ['National', 'ACT', 'NSW', 'NT', 'QLD', 'SA', 'TAS', 'VIC', 'WA']
smallnumberstates = ['ACT', 'NT', 'TAS']
# Define list of picker names: this will be used in a loop to create a dictionary of values to set pickersettinsg for each state
# We dont need pickers names/values for 2031-2050 here as default values are the same for both periods
pickerlist = ['services_emis_picker1930','mining_emis_picker1930','manufacturing_emis_picker1930','gas_water_waste_emis_picker1930','construction_emis_picker1930',
              'com_transp_emis_picker1930','agrifor_emis_picker1930','electricity_emis_picker1930','residential_emis_picker1930',
              'lulucf_emis_pickerbase', 'lulucf_emis_pickergrow',
              'services_valadd_picker','mining_valadd_picker','manufacturing_valadd_picker','gas_water_waste_valadd_picker',
              'construction_valadd_picker','com_transp_valadd_picker','agrifor_valadd_picker','electricity_valadd_picker',
              'electricity_growth_picker']
# Define list of picker settings: this will be used in a loop to create a dictionary of vlues to set pickersettinsg for each state
pickersettinglist = ['value', 'steps']

# Define list of colors for the sectors
my_discrete_color_map={"LULUCF": '#8C564B',
                       "Residential": '#FF7F0E',
                       "Electricity generation":'#D62728',
                       "Agriculture & Forestry":'#2CA02C',
                       "Agriculture":'#2CA02C',
                       "Commercial Transport": '#9467BD',
                       "Construction": '#1F77B4',
                       "Gas, Water & Waste Services":'#E377C2',
                       "Manufacturing":'#BCBD22',
                       "Mining":'#7F7F7F',
                       "Services": '#17BECF'}

# Define all the notes

services_emis_note_text = "Emissions for ANZSIC industry divisions DIV F - H, J - S Commercial Services, as reported in the State and Territory Greenhouse Gas Inventories"
mining_emis_note_text = "Emissions for ANZSIC industry division DIV B Mining, as reported in the State and Territory Greenhouse Gas Inventories"
manufacturing_emis_note_text = "Emissions for ANZSIC industry division DIV C Manufacturing, as reported in the State and Territory Greenhouse Gas Inventories"
gas_water_waste_emis_note_text = "Emissions for ANZSIC industry division DIV D Electricity, Gas, Water and Waste Services, as reported in the State and Territory Greenhouse Gas Inventories, minus emissions reported under electricity generation"
construction_emis_note_text = "Emissions for ANZSIC industry division DIV E Construction, as reported in the State and Territory Greenhouse Gas Inventories"
com_transp_emis_note_text = "Emissions for ANZSIC industry division DIV I Transport, Postal and Warehousing, as reported in the State and Territory Greenhouse Gas Inventories"
agriculture_emis_note_text = "Emissions as reported in the National Greenhouse Gas Inventory – UNFCCC classifications - 3 Agriculture"
residential_emis_note_text = "Residential emissions including private transport, as reported in the State and Territory Greenhouse Gas Inventories"
electricity_emis_note_text = "Emissions as reported via NEMSight, or via the Energy Update 2020 for Australia, NT, and WA. Assumed zero for the ACT."
total_emis_note_text = "Total emissions from all the activities listed above"

gross_emis_note_text = "These are the remaining emissions from all economic activities. Small levels of remaining emissions by 2050 can be compensated with LULUCF or negative emission technologies."
lulucf_note_text = "LULUCF is short for land-use, land use change and forestry. Negative emission technologies include e.g., carbon capture and storage (CCS). These processes can extract carbon dioxide from the air and store them in a sink, for example increased vegetation. Data on historical LULUCF levels as reported in the National Greenhouse Gas Inventory – UNFCCC classifications - 4 LULUCF." 
lulucf_emis_note_text = "Here you can set the expected baseline LULUCF emissions, as a constant number for the entire period 2019 to 2050."
lulucf_emis_growth_note_text = "Here you can set how rapidly you expect LULUCF and negative emission technologies to grow each year."
net_emis_note_text = "These are the gross emissions plus LULUCF & Negative emisssion technologies. Scientific consensus is that this number needs to get to zero by 2050 in order to limit global warming to 1.5 degrees."

services_valadd_note_text = "Value added for ANZSIC industry division Agriculture, forestry and fishing"
mining_valadd_note_text = "Value added for ANZSIC industry division Mining"
manufacturing_valadd_note_text = "Value added for ANZSIC industry division Manufacturing"
gas_water_waste_valadd_note_text = "Value added for ANZSIC industry sub-divisions 27 Gas supply, 28 Water supply, sewerage and drainage services"
construction_valadd_note_text = "Value added for ANZSIC industry division Construction"
com_transp_valadd_note_text = "Value added for ANZSIC industry division Transport, Postal and Warehousing"
agriculture_valadd_note_text = "Value added for ANZSIC industry division Agriculture, forestry and fishing. Note that emissions reported above are for Agriculture only. For the calculation of emission intensity, the emissions for the Agricultural sector only are divided by the total value added for the three sub-divisions Agriculture, forestry and fishing."
electricity_valadd_note_text = "Value added for ANZSIC industry sub-divisions 26 Electricity supply"
total_valadd_note_text = "Total value added for all sectors listed above"

emis_red_note_text = "Emission reductions are reported here as negative numbers. Positive numbers mean emissions increased compared to 2005 levels."

#######################  HTML divs styles for the overall layout  ######################
# #rgba(242, 241, 239, 1)
# #f8f9fa
# the style arguments for the header
my_header_style = {
    "width": "100%",
    "padding": "0 2% 0 2%",
    "color": "rgba(0,0,139,1)",
    "background-color": "#f8f9fa",
}
# the style arguments for the subheader with the tool explanation
my_subheader_style = {
    "width": "100%",
    "padding": "0 2% 0 2%",
    "background-color": "#f8f9fa",
}
# the style arguments for the header
my_tablist_style = {
    "position": "sticky",
    "top": 0,
    "background-color": "#f8f9fa",
    'zIndex': 9999,
}
# the style arguments for the sidebar. Sticky on top: scrolls untill 50px from top
my_left_pane_style = {
    "position": "sticky",
    "top": 37,
    "width": "55%",
    "background-color": "#f8f9fa",
}
# the styles for the main content position it to the right of the sidebar and
# add some padding.
my_right_pane_style = {
    "position": "relative",
    "top": -804,
    "margin-left": "53.7%",
    "background-color": "#ffffff",
}
# the style that fills the whole screen essentially
my_envelop_style = {
    "width": "100%",
    "max-width":"1536px",
    "margin": "auto",
    "background-color": "#f8f9fa"
}
my_background_style = {
    "width": "100%",
    "background-color": "#ffffff",
    "height": "768px",
    "position": "sticky",
}

### List of starting figures and other output
# These need to be deifned prior to the app layout
# But will be created during update in the callback, inlcuding layout
## Emissions figure
fig_emissions_total = go.Figure()
## Added value figure
fig_added_value_total = go.Figure()
## Emission intensity figure
fig_emis_int = go.Figure()
## Electricity generation and carbon intensity
# A bit special because of the dual axes
fig_elec_gen_int = make_subplots(specs=[[{"secondary_y": True}]])
## Population and per capita emissions
fig_pop_per_capita = make_subplots(specs=[[{"secondary_y": True}]])
## Emission intesnity index figure
fig_emis_int_index = make_subplots(specs=[[{"secondary_y": False}]])


### Define the app
# Note an additional stylesheet is loaded locally, see assets/bootstrap_modified.css
app = dash.Dash(__name__)

### App layout elements
header = html.Div(style=my_header_style, children=[
            html.Div(html.H1('Net-zero 2050 emissions pathway tool for Australia'))
            ])

subheader = html.Div(style=my_subheader_style, className='no-print', children=[
            html.Div(html.H3('With this tool you can develop pathways to reach net-zero emissions for Australia by 2050, a target considered necessary to keep global warming below 1.5 degrees.')),
            html.Div(html.H3('In each of the tabs below, you can make such trajectories separately for each State or Territory.')),
            html.Div(html.H3('You can make changes to the annual emissions growth, for both the near and long-term for each sector, and see how much closer this gets us to net-zero by 2050.')),
            html.Div(html.H3('Note that in the figures, you can click on the name f a sector in the legend to make it disappear from the results, or double click on the name to see the results for that sector only.')),
            html.Div(html.H3("For more explanation on how to use this tool, and how it was developed, see the 'About' page.")),
            html.Div(html.H3("For more information on ANU's research on energy transitions and long-term emissisons strategies, see the 'Reports' page."),style={"padding-bottom": "0.3rem"}),
            html.Div(html.H3('')),
            ])

tabheader = html.Div(style=my_tablist_style, className='no-print', children=[  # backgroundColor here is for the whole webpage
    dbc.Container([
        dcc.Tabs(id='tabslist', value='National', children=[
            dcc.Tab(label='Australia', value='National'),
            dcc.Tab(label='ACT', value='ACT'),
            dcc.Tab(label='NSW', value='NSW'),
            dcc.Tab(label='NT', value='NT'),
            dcc.Tab(label='QLD', value='QLD'),
            dcc.Tab(label='SA', value='SA'),
            dcc.Tab(label='TAS', value='TAS'),
            dcc.Tab(label='VIC', value='VIC'),
            dcc.Tab(label='WA', value='WA'),
            dcc.Tab(label='About', value='about'),
            dcc.Tab(label='Reports', value='reports')
            ]),
        ], fluid=True, style={"padding":"0px 0px 0px 0px"}), 
    ])

left_pane_io  = html.Div(style=my_left_pane_style, children=[
    dbc.Container([
        html.Div(id='left-pane-output')
        ], fluid=True),
    ])


right_pane_figs  = html.Div(style=my_right_pane_style, children=[
    dbc.Container([
        html.Div(id='right-pane-output')
        ], fluid=True),
    ])



### Define the app layout with tabs: content 'right-pane-output' is generated based on the tab selection
#app.layout = html.Div([dcc.Location(id="url"), header, sidebar, content])

app.layout = html.Div([html.Div([header, subheader, tabheader, left_pane_io, right_pane_figs], style=my_envelop_style)], style=my_background_style)



    
        
### Define app content based on tab choice. 
### The picker value selection is a separate callback, below this block
@app.callback(Output('left-pane-output', 'children'),
              [Input('tabslist', 'value')])
def render_sidebar(tab):
    if tab in statelist:
        ## get the rows of dat for this geo: this will be used to dynamically fill the pathway result table
        df_select = df_full[(df_full['geo']==tab) & (df_full['year']>=2005) & (df_full['sector']!="Overall")]
        ## Loop to get the right picker settings for each state and type of picker
        df_pickerselect = df_picker_in[(df_picker_in['geo']==tab)]
        df_pickerselect = df_pickerselect.set_index('picker')
        pickersetting_dict = {}
        for pickername in pickerlist:
            for pickersetting in pickersettinglist:
                pickersetting_dict[pickername + '_' + pickersetting] = df_pickerselect._get_value(pickername, pickersetting)
        return html.Div([
            dbc.Container([
                dbc.Row([
                    dbc.Col((html.Div(html.H6(' '))), width=12),
                    ],style={"background-color": "#f8f9fa"}),
                dbc.Row([
                    dbc.Col((html.Div(html.Strong('Emissions'), style={"line-height": "1"})), width=3),
                    dbc.Col((html.Div(html.H4(['Annaul emissions growth (Mt CO',html.Sub('2'),'-eq)']))), width=6, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4('Emissions reductions (% vs. 2005)', id='emis_red_note')),dbc.Tooltip(emis_red_note_text, target='emis_red_note',placement='right')), width=7, style={'text-align': 'center'}),
                    ]),
                dbc.Row([
                    dbc.Col((html.Div(html.H5(''))), width=3),
                    dbc.Col((html.Div(html.H5('Historical'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H5('Near-term'))), width=2, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H5('Long-term'))), width=2, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(['and total 2018 & 2050 emissions (Mt CO',html.Sub('2'),'-eq)']))), width=7, style={'text-align': 'center', "margin-top": "-0.3rem"}),
                    ]),
                dbc.Row([
                    dbc.Col((html.Div(html.H5(''))), width=3),
                    dbc.Col((html.Div(html.H5("2009 - 2018"))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H5('2019 - 2030'))), width=2, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H5('2031 - 2050'))), width=2, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H5('2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H5('2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H5('2030'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H5('2040'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H5('2050'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H5('2050 Mt'))), width=1, style={"text-align": "center"}),
                    ]),
                dbc.Row([
                    dbc.Col((html.Div(html.H4('Services', id='services_emis_note')),dbc.Tooltip(services_emis_note_text, target='services_emis_note',placement='right')), width=3),
                    dbc.Col((html.Div(html.H4([pickersetting_dict['services_emis_picker1930_value'],' Mt']))), width=1, style={'text-align': 'center'}),
                    dbc.Col((html.Div(dbc.Input(id='services_emis_picker1930', type="number", bs_size="sm", value=pickersetting_dict['services_emis_picker1930_value'], step=pickersetting_dict['services_emis_picker1930_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(dbc.Input(id='services_emis_picker3150', type="number", bs_size="sm", value=pickersetting_dict['services_emis_picker1930_value'], step=pickersetting_dict['services_emis_picker1930_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(html.H4(id='services_emis_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='services_emisred_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='services_emisred_2030'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='services_emisred_2040'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='services_emisred_2050'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='services_emis_2050'))), width=1, style={"text-align": "center"}),
                    ],style={"background-color": "rgba(23,190,207,0.5)"}),
                dbc.Row([
                    dbc.Col((html.Div(html.H4('Mining', id='mining_emis_note')),dbc.Tooltip(mining_emis_note_text, target='mining_emis_note',placement='right')), width=3),
                    dbc.Col((html.Div(html.H4([pickersetting_dict['mining_emis_picker1930_value'],' Mt']))), width=1, style={'text-align': 'center'}),
                    dbc.Col((html.Div(dbc.Input(id='mining_emis_picker1930', type="number", bs_size="sm", value=pickersetting_dict['mining_emis_picker1930_value'], step=pickersetting_dict['mining_emis_picker1930_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(dbc.Input(id='mining_emis_picker3150', type="number", bs_size="sm", value=pickersetting_dict['mining_emis_picker1930_value'], step=pickersetting_dict['mining_emis_picker1930_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(html.H4(id='mining_emis_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='mining_emisred_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='mining_emisred_2030'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='mining_emisred_2040'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='mining_emisred_2050'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='mining_emis_2050'))), width=1, style={"text-align": "center"}),
                    ],style={"background-color": "rgba(127,127,127,0.5)"}),
                dbc.Row([
                    dbc.Col((html.Div(html.H4('Manufacturing', id='manufacturing_emis_note')),dbc.Tooltip(manufacturing_emis_note_text, target='manufacturing_emis_note',placement='right')), width=3),
                    dbc.Col((html.Div(html.H4([pickersetting_dict['manufacturing_emis_picker1930_value'],' Mt']))), width=1, style={'text-align': 'center'}),
                    dbc.Col((html.Div(dbc.Input(id='manufacturing_emis_picker1930', type="number", bs_size="sm", value=pickersetting_dict['manufacturing_emis_picker1930_value'], step=pickersetting_dict['manufacturing_emis_picker1930_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(dbc.Input(id='manufacturing_emis_picker3150', type="number", bs_size="sm", value=pickersetting_dict['manufacturing_emis_picker1930_value'], step=pickersetting_dict['manufacturing_emis_picker1930_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(html.H4(id='manufacturing_emis_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='manufacturing_emisred_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='manufacturing_emisred_2030'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='manufacturing_emisred_2040'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='manufacturing_emisred_2050'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='manufacturing_emis_2050'))), width=1, style={"text-align": "center"}),
                    ],style={"background-color": "rgba(188,189,34,0.5)"}),
                dbc.Row([
                    dbc.Col((html.Div(html.H4('Gas, water & waste services', id='gas_water_waste_emis_note')),dbc.Tooltip(gas_water_waste_emis_note_text, target='gas_water_waste_emis_note',placement='right')), width=3),
                    dbc.Col((html.Div(html.H4([pickersetting_dict['gas_water_waste_emis_picker1930_value'],' Mt']))), width=1, style={'text-align': 'center'}),
                    dbc.Col((html.Div(dbc.Input(id='gas_water_waste_emis_picker1930', type="number", bs_size="sm", value=pickersetting_dict['gas_water_waste_emis_picker1930_value'], step=pickersetting_dict['gas_water_waste_emis_picker1930_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(dbc.Input(id='gas_water_waste_emis_picker3150', type="number", bs_size="sm", value=pickersetting_dict['gas_water_waste_emis_picker1930_value'], step=pickersetting_dict['gas_water_waste_emis_picker1930_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(html.H4(id='gas_water_waste_emis_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='gas_water_waste_emisred_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='gas_water_waste_emisred_2030'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='gas_water_waste_emisred_2040'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='gas_water_waste_emisred_2050'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='gas_water_waste_emis_2050'))), width=1, style={"text-align": "center"}),
                    ],style={"background-color": "rgba(227,119,194,0.5)"}),
                dbc.Row([
                    dbc.Col((html.Div(html.H4('Construction', id='construction_emis_note')),dbc.Tooltip(construction_emis_note_text, target='construction_emis_note',placement='right')), width=3),
                    dbc.Col((html.Div(html.H4([pickersetting_dict['construction_emis_picker1930_value'],' Mt']))), width=1, style={'text-align': 'center'}),
                    dbc.Col((html.Div(dbc.Input(id='construction_emis_picker1930', type="number", bs_size="sm", value=pickersetting_dict['construction_emis_picker1930_value'], step=pickersetting_dict['construction_emis_picker1930_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(dbc.Input(id='construction_emis_picker3150', type="number", bs_size="sm", value=pickersetting_dict['construction_emis_picker1930_value'], step=pickersetting_dict['construction_emis_picker1930_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(html.H4(id='construction_emis_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='construction_emisred_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='construction_emisred_2030'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='construction_emisred_2040'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='construction_emisred_2050'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='construction_emis_2050'))), width=1, style={"text-align": "center"}),
                    ],style={"background-color": "rgba(31,119,180,0.5)"}),
                dbc.Row([
                    dbc.Col((html.Div(html.H4('Commercial transport', id='com_transp_emis_note')),dbc.Tooltip(com_transp_emis_note_text, target='com_transp_emis_note',placement='right')), width=3),
                    dbc.Col((html.Div(html.H4([pickersetting_dict['com_transp_emis_picker1930_value'],' Mt']))), width=1, style={'text-align': 'center'}),
                    dbc.Col((html.Div(dbc.Input(id='com_transp_emis_picker1930', type="number", bs_size="sm", value=pickersetting_dict['com_transp_emis_picker1930_value'], step=pickersetting_dict['com_transp_emis_picker1930_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(dbc.Input(id='com_transp_emis_picker3150', type="number", bs_size="sm", value=pickersetting_dict['com_transp_emis_picker1930_value'], step=pickersetting_dict['com_transp_emis_picker1930_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(html.H4(id='com_transp_emis_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='com_transp_emisred_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='com_transp_emisred_2030'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='com_transp_emisred_2040'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='com_transp_emisred_2050'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='com_transp_emis_2050'))), width=1, style={"text-align": "center"}),
                    ],style={"background-color": "rgba(148,103,189,0.5)"}),
                dbc.Row([
                    dbc.Col((html.Div(html.H4('Agriculture', id='agriculture_emis_note')),dbc.Tooltip(agriculture_emis_note_text, target='agriculture_emis_note',placement='right')), width=3),
                    dbc.Col((html.Div(html.H4([pickersetting_dict['agrifor_emis_picker1930_value'],' Mt']))), width=1, style={'text-align': 'center'}),
                    dbc.Col((html.Div(dbc.Input(id='agrifor_emis_picker1930', type="number", bs_size="sm", value=pickersetting_dict['agrifor_emis_picker1930_value'], step=pickersetting_dict['agrifor_emis_picker1930_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(dbc.Input(id='agrifor_emis_picker3150', type="number", bs_size="sm", value=pickersetting_dict['agrifor_emis_picker1930_value'], step=pickersetting_dict['agrifor_emis_picker1930_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(html.H4(id='agrifor_emis_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='agrifor_emisred_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='agrifor_emisred_2030'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='agrifor_emisred_2040'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='agrifor_emisred_2050'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='agrifor_emis_2050'))), width=1, style={"text-align": "center"}),
                    ],style={"background-color": "rgba(44,160,44,0.5)"}),
                dbc.Row([
                    dbc.Col((html.Div(html.H4('Residential', id='residential_emis_note')),dbc.Tooltip(residential_emis_note_text, target='residential_emis_note',placement='right')), width=3),
                    dbc.Col((html.Div(html.H4([pickersetting_dict['residential_emis_picker1930_value'],' Mt']))), width=1, style={'text-align': 'center'}),
                    dbc.Col((html.Div(dbc.Input(id='residential_emis_picker1930', type="number", bs_size="sm", value=pickersetting_dict['residential_emis_picker1930_value'], step=pickersetting_dict['residential_emis_picker1930_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(dbc.Input(id='residential_emis_picker3150', type="number", bs_size="sm", value=pickersetting_dict['residential_emis_picker1930_value'], step=pickersetting_dict['residential_emis_picker1930_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(html.H4(id='residential_emis_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='residential_emisred_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='residential_emisred_2030'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='residential_emisred_2040'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='residential_emisred_2050'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='residential_emis_2050'))), width=1, style={"text-align": "center"}),
                    ],style={"background-color": "rgba(255,127,14,0.5)"}),
                dbc.Row([
                    dbc.Col((html.Div(html.H4('Electricity generation', id='electricity_emis_note')),dbc.Tooltip(electricity_emis_note_text, target='electricity_emis_note',placement='right')), width=3),
                    dbc.Col((html.Div(html.H4([pickersetting_dict['electricity_emis_picker1930_value'],' Mt']))), width=1, style={'text-align': 'center'}),
                    dbc.Col((html.Div(dbc.Input(id='electricity_emis_picker1930', type="number", bs_size="sm", value=pickersetting_dict['electricity_emis_picker1930_value'], step=pickersetting_dict['electricity_emis_picker1930_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(dbc.Input(id='electricity_emis_picker3150', type="number", bs_size="sm", value=pickersetting_dict['electricity_emis_picker1930_value'], step=pickersetting_dict['electricity_emis_picker1930_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(html.H4(id='electricity_emis_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='electricity_emisred_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='electricity_emisred_2030'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='electricity_emisred_2040'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='electricity_emisred_2050'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='electricity_emis_2050'))), width=1, style={"text-align": "center"}),
                    ],style={"background-color": "rgba(214,39,40,0.5)"}),
                dbc.Row([
                    dbc.Col((html.Div(html.H4('Total', id='total_emis_note')),dbc.Tooltip(total_emis_note_text, target='total_emis_note',placement='right')), width=3),
                    dbc.Col((html.Div(html.H4(id='total_emisred_Mt_hist'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='total_emisred_Mt_1930'))), width=2, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='total_emisred_Mt_3150'))), width=2, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='gross_emis_2018copy'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='total_emisred_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='total_emisred_2030'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='total_emisred_2040'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='total_emisred_2050'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='gross_emis_2050copy'))), width=1, style={"text-align": "center"}),
                    ],style={"background-color": "rgba(31, 119, 180, 0.8)"}),
                dbc.Row([
                    dbc.Col((html.Div(html.H6(' '))), width=12),
                    ],style={"background-color": "#f8f9fa"}),
                dbc.Row([
                    dbc.Col((html.Div(html.H4('Gross emissions', id='gross_emis_note')),dbc.Tooltip(gross_emis_note_text, target='gross_emis_note',placement='right')), width=3),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=2, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=2, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='gross_emis_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='gross_emis_2030'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='gross_emis_2040'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='gross_emis_2050'))), width=1, style={"text-align": "center"}),
                    ],style={"background-color": "rgba(31, 119, 180, 0.6)"}),
                dbc.Row([
                    dbc.Col((html.Div(html.H4('LULUCF & Negative emission technologies', id='lulucf_note')),dbc.Tooltip(lulucf_note_text, target='lulucf_note',placement='right')), width=8),
                    dbc.Col((html.Div(html.H4(''))), width=2, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=2, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='LULUCF_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='LULUCF_2030'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='LULUCF_2040'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='LULUCF_2050'))), width=1, style={"text-align": "center"}),
                    ],style={"background-color": "rgba(140,86,75,0.5)"}),
                dbc.Row([
                    dbc.Col((html.Div(html.H4('Baseline (Mt/y)', id='lulucf_base_note')),dbc.Tooltip(lulucf_emis_note_text, target='lulucf_base_note',placement='right')), width=3),
                    dbc.Col((html.Div(html.H4([pickersetting_dict['lulucf_emis_pickerbase_value'],' Mt']))), width=1, style={'text-align': 'center'}),
                    dbc.Col((html.Div(dbc.Input(id='lulucf_emis_pickerbase1930', type="number", bs_size="sm", value=0, step=pickersetting_dict['lulucf_emis_pickergrow_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(dbc.Input(id='lulucf_emis_pickerbase3150', type="number", bs_size="sm", value=0, step=pickersetting_dict['lulucf_emis_pickergrow_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"text-align": "center"}),
                    ],style={"background-color": "rgba(140,86,75,0.5)"}),
                dbc.Row([
                    dbc.Col((html.Div(html.H4('Annual growth (Mt/y)', id='lulucf_growth_note')),dbc.Tooltip(lulucf_emis_growth_note_text, target='lulucf_growth_note',placement='right')), width=3),
                    dbc.Col((html.Div(html.H4([pickersetting_dict['lulucf_emis_pickergrow_value'],' Mt']))), width=1, style={'text-align': 'center'}),
                    dbc.Col((html.Div(dbc.Input(id='lulucf_emis_pickergrow1930', type="number", bs_size="sm", value=0, step=pickersetting_dict['lulucf_emis_pickergrow_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(dbc.Input(id='lulucf_emis_pickergrow3150', type="number", bs_size="sm", value=0, step=pickersetting_dict['lulucf_emis_pickergrow_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"text-align": "center"}),
                    ],style={"background-color": "rgba(140,86,75,0.5)"}),
                dbc.Row([
                    dbc.Col((html.Div(html.H4(html.Strong('Net emissions', id='net_emis_note'))),dbc.Tooltip(net_emis_note_text, target='net_emis_note',placement='right')), width=3),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=2, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=2, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(html.Strong(id='net_emis_2018')))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(html.Strong(id='net_emis_2030')))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(html.Strong(id='net_emis_2040')))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(html.Strong(id='net_emis_2050')))), width=1, style={"text-align": "center"}),
                    ],style={"background-color": "rgba(31, 119, 180, 0.8)"}),
                dbc.Row([
                    dbc.Col((html.Div(html.H4(html.Strong('Net emission reductions (% vs. 2005)', id='net_emis_note'))),dbc.Tooltip(net_emis_note_text, target='net_emis_note',placement='right')), width=8),
                    dbc.Col((html.Div(html.H4(''))), width=2, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=2, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(html.Strong(id='net_emisred_2018')))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(html.Strong(id='net_emisred_2030')))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(html.Strong(id='net_emisred_2040')))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(html.Strong(id='net_emisred_2050')))), width=1, style={"text-align": "center"}),
                    ],style={"background-color": "rgba(31, 119, 180, 0.8)"}),
                dbc.Row([
                    dbc.Col((html.Div(html.H4(''))), width=12),
                    ],style={"background-color": "#f8f9fa"}),
                dbc.Row([
                    dbc.Col((html.Div(html.H4(''))), width=12),
                    ],style={"background-color": "#f8f9fa"}),
                dbc.Row([
                    dbc.Col((html.Div(html.Strong('Emission intensity'))), width=3),
                    dbc.Col((html.Div(html.H4('Electricity generation growth (%/y)'))), width=6, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(['Carbon intensity of electricity generation (g CO',html.Sub('2'),'/kWh)']))), width=7, style={"text-align": "center"}),
                    ]),
                dbc.Row([
                    dbc.Col((html.Div(html.H5(''))), width=3),
                    dbc.Col((html.Div(html.H5("2009 - 2018"))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H5('2019 - 2030'))), width=2, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H5('2031 - 2050'))), width=2, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H5('2018'))), width=5, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H5('2030'))), width=5, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H5('2040'))), width=5, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H5('2050'))), width=5, style={"text-align": "center"}),
                    ]),
                dbc.Row([
                    dbc.Col((html.Div(html.H4('Electricity generation'))), width=3),
                    dbc.Col((html.Div(html.H4([pickersetting_dict['electricity_growth_picker_value'], '%']))), width=1, style={'text-align': 'center'}),
                    dbc.Col((html.Div(dbc.Input(id='electricity_growth_picker', type="number", bs_size="sm", value=pickersetting_dict['electricity_growth_picker_value'], step=pickersetting_dict['electricity_growth_picker_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(dbc.Input(id='electricity_growth_picker', type="number", bs_size="sm", value=pickersetting_dict['electricity_growth_picker_value'], step=pickersetting_dict['electricity_growth_picker_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(html.H4(id='elec_carb_int_2018'))), width=5, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='elec_carb_int_2030'))), width=5, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='elec_carb_int_2040'))), width=5, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='elec_carb_int_2050'))), width=5, style={"text-align": "center"}),
                    ],style={"background-color": "rgba(214,39,40,0.5)"}),                
                dbc.Row([
                    dbc.Col((html.Div(html.H4(''))), width=12),
                    ],style={"background-color": "#f8f9fa"}),
                dbc.Row([
                    dbc.Col((html.Div(html.H4(''))), width=12),
                    ],style={"background-color": "#f8f9fa"}),
                dbc.Row([
                    dbc.Col((html.Div(html.Strong(''))), width=3),
                    dbc.Col((html.Div(html.H4('Value added growth (%/y)'))), width=6),
                    dbc.Col((html.Div(html.H4('Emission intensity changes (%/y)'))), width=7),
                    ]),
                dbc.Row([
                    dbc.Col((html.Div(html.H5(''))), width=3),
                    dbc.Col((html.Div(html.H5("2009 - 2018"))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H5('2019 - 2050'))), width=2, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H5(''))), width=2, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H5('2009 - 2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H5('2019 - 2030'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H5('2031 - 2050'))), width=1, style={"text-align": "center"}),
                    ]),
                dbc.Row([
                    dbc.Col((html.Div(html.H4('Services', id='services_valadd_note')),dbc.Tooltip(services_valadd_note_text, target='services_valadd_note',placement='right')), width=3),
                    dbc.Col((html.Div(html.H4([pickersetting_dict['services_valadd_picker_value'], '%']))), width=1, style={'text-align': 'center'}),
                    dbc.Col((html.Div(dbc.Input(id='services_valadd_picker', type="number", bs_size="sm", value=pickersetting_dict['services_valadd_picker_value'], step=pickersetting_dict['services_valadd_picker_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(html.H4(''))), width=2, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='services_emisint_red_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='services_emisint_red_2030'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='services_emisint_red_2050'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"background-color": "#f8f9fa"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"background-color": "#f8f9fa"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"background-color": "#f8f9fa"}),
                    ],style={"background-color": "rgba(23,190,207,0.5)"}),
                dbc.Row([
                    dbc.Col((html.Div(html.H4('Mining', id='mining_valadd_note')),dbc.Tooltip(mining_valadd_note_text, target='mining_valadd_note',placement='right')), width=3),
                    dbc.Col((html.Div(html.H4([pickersetting_dict['mining_valadd_picker_value'], '%']))), width=1, style={'text-align': 'center'}),
                    dbc.Col((html.Div(dbc.Input(id='mining_valadd_picker', type="number", bs_size="sm", value=pickersetting_dict['mining_valadd_picker_value'], step=pickersetting_dict['mining_valadd_picker_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(html.H4(''))), width=2, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='mining_emisint_red_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='mining_emisint_red_2030'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='mining_emisint_red_2050'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"background-color": "#f8f9fa"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"background-color": "#f8f9fa"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"background-color": "#f8f9fa"}),
                    ],style={"background-color": "rgba(127,127,127,0.5)"}),
                dbc.Row([
                    dbc.Col((html.Div(html.H4('Manufacturing', id='manufacturing_valadd_note')),dbc.Tooltip(manufacturing_valadd_note_text, target='manufacturing_valadd_note',placement='right')), width=3),
                    dbc.Col((html.Div(html.H4([pickersetting_dict['manufacturing_valadd_picker_value'], '%']))), width=1, style={'text-align': 'center'}),
                    dbc.Col((html.Div(dbc.Input(id='manufacturing_valadd_picker', type="number", bs_size="sm", value=pickersetting_dict['manufacturing_valadd_picker_value'], step=pickersetting_dict['manufacturing_valadd_picker_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(html.H4(''))), width=2, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='manufacturing_emisint_red_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='manufacturing_emisint_red_2030'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='manufacturing_emisint_red_2050'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"background-color": "#f8f9fa"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"background-color": "#f8f9fa"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"background-color": "#f8f9fa"}),
                    ],style={"background-color": "rgba(188,189,34,0.5)"}),
                dbc.Row([
                    dbc.Col((html.Div(html.H4('Gas, water & waste services', id='gas_water_waste_valadd_note')),dbc.Tooltip(gas_water_waste_valadd_note_text, target='gas_water_waste_valadd_note',placement='right')), width=3),
                    dbc.Col((html.Div(html.H4([pickersetting_dict['gas_water_waste_valadd_picker_value'], '%']))), width=1, style={'text-align': 'center'}),
                    dbc.Col((html.Div(dbc.Input(id='gas_water_waste_valadd_picker', type="number", bs_size="sm", value=pickersetting_dict['gas_water_waste_valadd_picker_value'], step=pickersetting_dict['gas_water_waste_valadd_picker_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(html.H4(''))), width=2, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='gas_water_waste_emisint_red_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='gas_water_waste_emisint_red_2030'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='gas_water_waste_emisint_red_2050'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"background-color": "#f8f9fa"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"background-color": "#f8f9fa"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"background-color": "#f8f9fa"}),
                    ],style={"background-color": "rgba(227,119,194,0.5)"}),
                dbc.Row([
                    dbc.Col((html.Div(html.H4('Construction', id='construction_valadd_note')),dbc.Tooltip(construction_valadd_note_text, target='construction_valadd_note',placement='right')), width=3),
                    dbc.Col((html.Div(html.H4([pickersetting_dict['construction_valadd_picker_value'], '%']))), width=1, style={'text-align': 'center'}),
                    dbc.Col((html.Div(dbc.Input(id='construction_valadd_picker', type="number", bs_size="sm", value=pickersetting_dict['construction_valadd_picker_value'], step=pickersetting_dict['construction_valadd_picker_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(html.H4(''))), width=2, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='construction_emisint_red_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='construction_emisint_red_2030'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='construction_emisint_red_2050'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"background-color": "#f8f9fa"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"background-color": "#f8f9fa"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"background-color": "#f8f9fa"}),
                    ],style={"background-color": "rgba(31,119,180,0.5)"}),
                dbc.Row([
                    dbc.Col((html.Div(html.H4('Commercial transport', id='com_transp_valadd_note')),dbc.Tooltip(com_transp_valadd_note_text, target='com_transp_valadd_note',placement='right')), width=3),
                    dbc.Col((html.Div(html.H4([pickersetting_dict['com_transp_valadd_picker_value'], '%']))), width=1, style={'text-align': 'center'}),
                    dbc.Col((html.Div(dbc.Input(id='com_transp_valadd_picker', type="number", bs_size="sm", value=pickersetting_dict['com_transp_valadd_picker_value'], step=pickersetting_dict['com_transp_valadd_picker_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(html.H4(''))), width=2, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='com_transp_emisint_red_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='com_transp_emisint_red_2030'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='com_transp_emisint_red_2050'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"background-color": "#f8f9fa"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"background-color": "#f8f9fa"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"background-color": "#f8f9fa"}),
                    ],style={"background-color": "rgba(148,103,189,0.5)"}),
                dbc.Row([
                    dbc.Col((html.Div(html.H4('Agriculture & Forestry', id='agrifor_valadd_note')),dbc.Tooltip(agriculture_valadd_note_text, target='agrifor_valadd_note',placement='right')), width=3),
                    dbc.Col((html.Div(html.H4([pickersetting_dict['agrifor_valadd_picker_value'], '%']))), width=1, style={'text-align': 'center'}),
                    dbc.Col((html.Div(dbc.Input(id='agrifor_valadd_picker', type="number", bs_size="sm", value=pickersetting_dict['agrifor_valadd_picker_value'], step=pickersetting_dict['agrifor_valadd_picker_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(html.H4(''))), width=2),
                    dbc.Col((html.Div(html.H4(id='agrifor_emisint_red_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='agrifor_emisint_red_2030'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='agrifor_emisint_red_2050'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"background-color": "#f8f9fa"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"background-color": "#f8f9fa"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"background-color": "#f8f9fa"}),
                    ],style={"background-color": "rgba(44,160,44,0.5)"}),
                dbc.Row([
                    dbc.Col((html.Div(html.H4('Electricity generation', id='electricity_valadd_note')),dbc.Tooltip(electricity_valadd_note_text, target='electricity_valadd_note',placement='right')), width=3),
                    dbc.Col((html.Div(html.H4([pickersetting_dict['electricity_valadd_picker_value'], '%']))), width=1, style={'text-align': 'center'}),
                    dbc.Col((html.Div(dbc.Input(id='electricity_valadd_picker', type="number", bs_size="sm", value=pickersetting_dict['electricity_valadd_picker_value'], step=pickersetting_dict['electricity_valadd_picker_steps']))), width=2, style={"text-align": "center", "padding-top":"0.15rem"}),
                    dbc.Col((html.Div(html.H4(''))), width=2, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='electricity_emisint_red_2018'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='electricity_emisint_red_2030'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='electricity_emisint_red_2050'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"background-color": "#f8f9fa"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"background-color": "#f8f9fa"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"background-color": "#f8f9fa"}),
                    ],style={"background-color": "rgba(214,39,40,0.5)"}),
                dbc.Row([
                    dbc.Col((html.Div(html.H4('Total', id='total_valadd_note')),dbc.Tooltip(total_valadd_note_text, target='total_valadd_note',placement='right')), width=3),
                    dbc.Col((html.Div(html.H4(id='total_val_add_hist'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='total_val_add_1950'))), width=2, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=2, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='total_emis_int_red_hist'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='total_emis_int_red_1930'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(id='total_emis_int_red_3150'))), width=1, style={"text-align": "center"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"background-color": "#f8f9fa"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"background-color": "#f8f9fa"}),
                    dbc.Col((html.Div(html.H4(''))), width=1, style={"background-color": "#f8f9fa"}),
                    ],style={"background-color": "rgba(31, 119, 180, 0.8)"}),
                dbc.Row([
                    dbc.Col((html.Div(html.H6(' '))), width=12),
                    ],style={"background-color": "#f8f9fa"}),
               dbc.Row([
                    html.Div(html.H3('This tool is provided by the Centre for Climate and Energy Policy, Crawford School of Public Policy, The Australian National University, with funding support by the 2050 Pathways Platform. Contact for queries and comments: ccep@anu.edu.au')),
                    ]),
                dbc.Row([
                    html.Div(html.H3('Emission pathway tool concept and data compilation by Paul Wyrwoll, Jorrit Gosens, Zeba Anjum, Frank Jotzo.')),
                    ]),
                dbc.Row([
                    html.Div(html.H3('Website & web application in Python/Dash/Plotly by Jorrit Gosens.')),
                    ]),
                ], fluid=True, style={"padding": "5px 20px 20px 20px", 'backgroundColor': 'f8f9fa', "position": "sticky", "top": 60, 'zIndex': 9999}), ### This is for padding aroudn the entire app: fill the entire screen, but keep padding top right bottom left at x pixels
            ])
        
    elif tab == 'about':
        return html.Div([
            html.H2('About this tool'),
            html.H3('This tool is provided by the Centre for Climate and Energy Policy, Crawford School of Public Policy, The Australian National University, with funding support by the 2050 Pathways Platform.'),
            html.H3('Contact for queries and comments: ccep@anu.edu.au'),
            html.H3('Emission pathway tool concept and data compilation by Paul Wyrwoll, Jorrit Gosens, Zeba Anjum, Frank Jotzo.'),
            html.H3(['This website & web application was built in Python/Dash/Plotly by Jorrit Gosens. Source code here: ', html.A("(link)", href='https://github.com/JorritHimself/Australian-Emission-Model-Dash', target="_blank"), '.']),
            html.Div(html.H2('How to use this tool'),style={"margin-top": "1.5rem"}),
            html.H3('Explanation todo'),
            html.H3(['For a brief tutorial see this youtube clip here (actually also todo): ', html.A("(link)", href='http://youtube.com', target="_blank"), '.']),
            html.Div(html.H2('Sources and methodological notes'),style={"margin-top": "1.5rem"}),
            html.H2('Data used in this tool'),
            html.H3(['The complete set of data as used in this tool can be downloaded here: ', html.A("(link)", href='http://aus2050emis.org/assets/ANU%20Australian%20emissions%20pathway%20tool%20-%20input%20data.xlsx', target="_blank"), '.']),
            html.H2('Emissions'),
            html.H3(['The primary source of emissions data is the State and Territory Greenhouse Gas Inventories, Department of Industry, Science, Energy and Resources: ', html.A("(link)", href='https://www.industry.gov.au/data-and-publications/state-and-territory-greenhouse-gas-inventories', target="_blank"), '.']),
            html.H3(['For emmissions from agiculture and LULUCF, we used data from the National Greenhouse Gas Inventory – UNFCCC classifications, also provided by the Department of Industry, Science, Energy and Resources : ', html.A("(link)", href='https://ageis.climatechange.gov.au/UNFCCC.aspx', target="_blank"), '.']),
            html.H3('For the sub-national level, the State and Territory Greenhouse Gas Inventories does not split out emmissions from electricity generation versus gas, water, & waste services. We divided the two by subtracting emissions from electricity generation, as determined below.'),
            html.H3('For emmissions from electricity generation, for the national level, we used the numbers from the State and Territory Greenhouse Gas Inventories, Department of Industry, Science, Energy and Resources'),
            html.H3(['For emmissions from electricity generation, for NSW, QLD, SA, TAS, VIC, we used AEMO data, via NEMSight: ', html.A("(link)", href='http://analytics.com.au/energy-analysis/nemsight-trading-tool', target="_blank"), '.']),
            html.H3(['Emmissions from electricity generation for NT and WA are estimated by using emission intensity as reported in the Electricity sector emissions and generation data, Clean Energy Regulator: ', html.A("(link)", href='http://www.cleanenergyregulator.gov.au/NGER/National%20greenhouse%20and%20energy%20reporting%20data/electricity-sector-emissions-and-generation-data', target="_blank"), '. These emission intensity numbers were then multiplied with electricity generation numbers from the Energy Update 2020, Table O: ', html.A("(link)", href='https://www.energy.gov.au/publications/australian-energy-update-2020', target="_blank"), '.']),
            html.H3('We chose to use the electricity emissions (for NT and WA) from the Energy Update rather than from the Clean Energy Regulator, as 1) the former has longer time-series, and 2) the emissions data for electricity generation from the Clean energy regulator in some years are larger than the total emissions reported for electricity, gas, water, and waste services combined, as reported in the State and Territory Greenhouse Gas Inventories.'),
            html.H3('The emissions intensity of electricity generation for NT and WA for the period 2005-2013 is presumed equal to the intensity reported in 2014, the earliest year for which this data is available.'),
            html.H3('Emmissions from electricity generation for the ACT are set to zero. The emissions are instead shown as part of NSW emissions. The ACT is part of the NSW region in the National Electricity Market. The ACT has renewable energy generation under contract that equates to the total electricity use in the ACT, and thus claims zero emissions from electricity generation for the ACT.'),
            html.H2('Value added'),
            html.H3(['Data used is the Industry Added Value by industry division or industry subdivision, provided by the Australian Bureau of Statistics: ', html.A("(link)", href='https://www.abs.gov.au/AUSSTATS/abs@.nsf/DetailsPage/8155.02017-18?OpenDocument', target="_blank"), '.']),
            html.H3('Industry data was reported in financial years and has been averaged to convert to calender years.'),
            html.H3("For the State level, the industry division 'Electricity, Gas, Water & Waste Services' was split into 'Electricity generation' and 'Gas, Water & Waste Services' by using the same percentage split between the two reported for the national level."),
            html.H2('Inflation'),
            html.H3(['To recalculate value added as 2019 AUD, we used the RBA Inflation calculator: ', html.A("(link)", href='https://www.rba.gov.au/calculator/', target="_blank"), '.']),
            html.H2('Population'),
            html.H3(['Population statistics via the Australian Bureau of Statistics: ', html.A("(link)", href='https://www.abs.gov.au/statistics/people/population/historical-population/latest-release', target="_blank"), '.']),
            html.Div(html.H3(['For future population numbers, we used the Series B projections from the Australian Bureau of Statistics: ', html.A("(link)", href='https://www.abs.gov.au/statistics/people/population/population-projections-australia/latest-release', target="_blank"), '.']),style={"padding-bottom": "10rem"}),
            ])
    elif tab == 'reports':
        return html.Div([
            html.H3('Here will be some other reports and links to the CCEP website etc')
            ])
    
    
### Define app content based on tab choice. 
### The picker value selection is a separate callback, below this block
@app.callback(Output('right-pane-output', 'children'),
              [Input('tabslist', 'value')])
def render_content(tab):
    if tab in statelist:
        return html.Div([
            dbc.Container([
                dbc.Row([html.Div(dcc.Graph(id='emissions_total', figure = fig_emissions_total))]),
                dbc.Row([html.Div(dcc.Graph(id='emis_int_index', figure = fig_emis_int_index))]),
                dbc.Row([html.Div(dcc.Graph(id='elec_gen_int', figure = fig_elec_gen_int))]),
                dbc.Row([html.Div(dcc.Graph(id='pop_per_capita_emis', figure = fig_pop_per_capita))]),
                dbc.Row([html.Div(dcc.Graph(id='value_added_total', figure = fig_added_value_total))]),
                dbc.Row([html.Div(dcc.Graph(id='emis_int', figure = fig_emis_int))]),
                ]),
            ])

### Use picker input to update the figures and table contents all in one callback
@app.callback(
    [Output('emissions_total', 'figure'),
     Output('value_added_total', 'figure'),
     Output('emis_int', 'figure'),
     Output('elec_gen_int', 'figure'),
     Output('pop_per_capita_emis', 'figure'),
     Output('emis_int_index', 'figure'),
     Output('services_emisred_2018', 'children'),
     Output('services_emisred_2030', 'children'),
     Output('services_emisred_2040', 'children'),
     Output('services_emisred_2050', 'children'),
     Output('mining_emisred_2018', 'children'),
     Output('mining_emisred_2030', 'children'),
     Output('mining_emisred_2040', 'children'),
     Output('mining_emisred_2050', 'children'),
     Output('manufacturing_emisred_2018', 'children'),
     Output('manufacturing_emisred_2030', 'children'),
     Output('manufacturing_emisred_2040', 'children'),
     Output('manufacturing_emisred_2050', 'children'),
     Output('gas_water_waste_emisred_2018', 'children'),
     Output('gas_water_waste_emisred_2030', 'children'),
     Output('gas_water_waste_emisred_2040', 'children'),
     Output('gas_water_waste_emisred_2050', 'children'),
     Output('construction_emisred_2018', 'children'),
     Output('construction_emisred_2030', 'children'),
     Output('construction_emisred_2040', 'children'),
     Output('construction_emisred_2050', 'children'),
     Output('com_transp_emisred_2018', 'children'),
     Output('com_transp_emisred_2030', 'children'),
     Output('com_transp_emisred_2040', 'children'),
     Output('com_transp_emisred_2050', 'children'),
     Output('agrifor_emisred_2018', 'children'),
     Output('agrifor_emisred_2030', 'children'),
     Output('agrifor_emisred_2040', 'children'),
     Output('agrifor_emisred_2050', 'children'),
     Output('residential_emisred_2018', 'children'),
     Output('residential_emisred_2030', 'children'),
     Output('residential_emisred_2040', 'children'),
     Output('residential_emisred_2050', 'children'),
     Output('electricity_emisred_2018', 'children'),
     Output('electricity_emisred_2030', 'children'),
     Output('electricity_emisred_2040', 'children'),
     Output('electricity_emisred_2050', 'children'),
     Output('services_emis_2018', 'children'),
     Output('mining_emis_2018', 'children'),
     Output('manufacturing_emis_2018', 'children'),
     Output('gas_water_waste_emis_2018', 'children'),
     Output('construction_emis_2018', 'children'),
     Output('com_transp_emis_2018', 'children'),
     Output('agrifor_emis_2018', 'children'),
     Output('residential_emis_2018', 'children'),
     Output('electricity_emis_2018', 'children'),
     Output('services_emis_2050', 'children'),
     Output('mining_emis_2050', 'children'),
     Output('manufacturing_emis_2050', 'children'),
     Output('gas_water_waste_emis_2050', 'children'),
     Output('construction_emis_2050', 'children'),
     Output('com_transp_emis_2050', 'children'),
     Output('agrifor_emis_2050', 'children'),
     Output('residential_emis_2050', 'children'),
     Output('electricity_emis_2050', 'children'),
     Output('total_emisred_Mt_hist', 'children'),
     Output('total_emisred_Mt_1930', 'children'),
     Output('total_emisred_Mt_3150', 'children'),
     Output('total_emisred_2018', 'children'),
     Output('total_emisred_2030', 'children'),
     Output('total_emisred_2040', 'children'),
     Output('total_emisred_2050', 'children'),
     Output('net_emisred_2018', 'children'),
     Output('net_emisred_2030', 'children'),
     Output('net_emisred_2040', 'children'),
     Output('net_emisred_2050', 'children'),
     Output('gross_emis_2018', 'children'),
     Output('gross_emis_2030', 'children'),
     Output('gross_emis_2040', 'children'),
     Output('gross_emis_2050', 'children'),
     Output('gross_emis_2018copy', 'children'),
     Output('gross_emis_2050copy', 'children'),
     Output('LULUCF_2018', 'children'),
     Output('LULUCF_2030', 'children'),
     Output('LULUCF_2040', 'children'),
     Output('LULUCF_2050', 'children'),
     Output('net_emis_2018', 'children'),
     Output('net_emis_2030', 'children'),
     Output('net_emis_2040', 'children'),
     Output('net_emis_2050', 'children'),
     Output('total_val_add_hist', 'children'),
     Output('total_val_add_1950', 'children'),
     Output('elec_carb_int_2018', 'children'),
     Output('elec_carb_int_2030', 'children'),
     Output('elec_carb_int_2040', 'children'),
     Output('elec_carb_int_2050', 'children'),
     Output('services_emisint_red_2018', 'children'),
     Output('services_emisint_red_2030', 'children'),
     Output('services_emisint_red_2050', 'children'),
     Output('mining_emisint_red_2018', 'children'),
     Output('mining_emisint_red_2030', 'children'),
     Output('mining_emisint_red_2050', 'children'),
     Output('manufacturing_emisint_red_2018', 'children'),
     Output('manufacturing_emisint_red_2030', 'children'),
     Output('manufacturing_emisint_red_2050', 'children'),
     Output('gas_water_waste_emisint_red_2018', 'children'),
     Output('gas_water_waste_emisint_red_2030', 'children'),
     Output('gas_water_waste_emisint_red_2050', 'children'),
     Output('construction_emisint_red_2018', 'children'),
     Output('construction_emisint_red_2030', 'children'),
     Output('construction_emisint_red_2050', 'children'),
     Output('com_transp_emisint_red_2018', 'children'),
     Output('com_transp_emisint_red_2030', 'children'),
     Output('com_transp_emisint_red_2050', 'children'),
     Output('agrifor_emisint_red_2018', 'children'),
     Output('agrifor_emisint_red_2030', 'children'),
     Output('agrifor_emisint_red_2050', 'children'),
     Output('electricity_emisint_red_2018', 'children'),
     Output('electricity_emisint_red_2030', 'children'),
     Output('electricity_emisint_red_2050', 'children'),
     Output('total_emis_int_red_hist', 'children'),
     Output('total_emis_int_red_1930', 'children'),
     Output('total_emis_int_red_3150', 'children'),
     ],
    [Input('agrifor_emis_picker1930', 'value'),
     Input('com_transp_emis_picker1930', 'value'),
     Input('construction_emis_picker1930', 'value'),
     Input('electricity_emis_picker1930', 'value'),
     Input('gas_water_waste_emis_picker1930', 'value'),
     Input('manufacturing_emis_picker1930', 'value'),
     Input('mining_emis_picker1930', 'value'),
     Input('residential_emis_picker1930', 'value'),
     Input('services_emis_picker1930', 'value'),
     Input('agrifor_emis_picker3150', 'value'),
     Input('com_transp_emis_picker3150', 'value'),
     Input('construction_emis_picker3150', 'value'),
     Input('electricity_emis_picker3150', 'value'),
     Input('gas_water_waste_emis_picker3150', 'value'),
     Input('manufacturing_emis_picker3150', 'value'),
     Input('mining_emis_picker3150', 'value'),
     Input('residential_emis_picker3150', 'value'),
     Input('services_emis_picker3150', 'value'),
     Input('agrifor_valadd_picker', 'value'),
     Input('com_transp_valadd_picker', 'value'),
     Input('construction_valadd_picker', 'value'),
     Input('electricity_valadd_picker', 'value'),
     Input('gas_water_waste_valadd_picker', 'value'),
     Input('manufacturing_valadd_picker', 'value'),
     Input('mining_valadd_picker', 'value'),
     Input('services_valadd_picker', 'value'),
     Input('lulucf_emis_pickerbase1930', 'value'),
     Input('lulucf_emis_pickerbase3150', 'value'),
     Input('lulucf_emis_pickergrow1930', 'value'),
     Input('lulucf_emis_pickergrow3150', 'value'),
     Input('electricity_growth_picker', 'value'),
     Input('tabslist', 'value')
     ]
)

def update_all_outputs(agrifor_emis_trend1930, com_transp_emis_trend1930, construction_emis_trend1930, electricity_emis_trend1930,
                       gas_water_waste_emis_trend1930, manufacturing_emis_trend1930, mining_emis_trend1930, residential_emis_trend1930, services_emis_trend1930,
                       agrifor_emis_trend3150, com_transp_emis_trend3150, construction_emis_trend3150, electricity_emis_trend3150,
                       gas_water_waste_emis_trend3150, manufacturing_emis_trend3150, mining_emis_trend3150, residential_emis_trend3150, services_emis_trend3150,
                       agrifor_valadd_trend,com_transp_valadd_trend,construction_valadd_trend, electricity_valadd_trend,
                       gas_water_waste_valadd_trend, manufacturing_valadd_trend, mining_valadd_trend, services_valadd_trend,
                       lulucf_emis_base1930, lulucf_emis_base3150, lulucf_emis_growth1930, lulucf_emis_growth3150, electricity_growth_trend, tab):
    df_select = df_full[(df_full['geo']==tab) & (df_full['year']>=2005) & (df_full['sector']!="Overall")]
### ### Emissions output per sector:
    ## First line: intermediate result: emissions levels in 2018 ('finaly'), + number of years since 2018 *annual emission growth 2019-2030
    ## Second line: emissions can not be less then zero, so we fix that here, also because totals for 2030 would be calculated on this value
    ## Third line: move corrected intermediate result to output
    ## Fourth line: If emissions in 2030 are already zero, we only add annual increases in all years since 2030
    ## Fifth line: If emissions in 2030 are not yet zero, we take the level in 2030 + number of years since 2030 *annual emission growth 2031-2050
    ## Sixth line again is to prevent emissions in each sector to go negative. Exception is LULUCF, this can go negative
    ### 'Agriculture & Forestry' emmissions:
    df_select.loc[(df_select['sector']=='Agriculture & Forestry') & (df_select['yrs_since_final_obs']>0) & (df_select['yrs_since_final_obs']),'emissions_MtCo2_base2030'] = df_select['emissions_MtCo2_finaly']+agrifor_emis_trend1930*df_select['yrs_since_final_obs']
    df_select.loc[(df_select['sector']=='Agriculture & Forestry') & (df_select['yrs_since_final_obs']>12),'emissions_MtCo2_base2030'] = df_select['emissions_MtCo2_finaly']+agrifor_emis_trend1930*12
    df_select.loc[(df_select['sector']=='Agriculture & Forestry') & (df_select['emissions_MtCo2_base2030']<0), 'emissions_MtCo2_base2030'] = 0
    df_select.loc[(df_select['sector']=='Agriculture & Forestry') & (df_select['yrs_since_final_obs']>0), 'emissions_MtCo2_output'] = df_select['emissions_MtCo2_base2030']
    df_select.loc[(df_select['sector']=='Agriculture & Forestry') & (df_select['yrs_since_final_obs']>12) & (df_select['emissions_MtCo2_base2030']<=0), 'emissions_MtCo2_output'] = agrifor_emis_trend3150*(df_select['yrs_since_final_obs']-12)
    df_select.loc[(df_select['sector']=='Agriculture & Forestry') & (df_select['yrs_since_final_obs']>12) & (df_select['emissions_MtCo2_base2030']>0), 'emissions_MtCo2_output'] =  df_select['emissions_MtCo2_base2030'] + agrifor_emis_trend3150*(df_select['yrs_since_final_obs']-12)
    df_select.loc[(df_select['sector']=='Agriculture & Forestry') & (df_select['emissions_MtCo2_output']<0), 'emissions_MtCo2_output'] = 0
    ### 'Commercial Transport' emmissions: 
    df_select.loc[(df_select['sector']=='Commercial Transport') & (df_select['yrs_since_final_obs']>0) & (df_select['yrs_since_final_obs']),'emissions_MtCo2_base2030'] = df_select['emissions_MtCo2_finaly']+com_transp_emis_trend1930*df_select['yrs_since_final_obs']
    df_select.loc[(df_select['sector']=='Commercial Transport') & (df_select['yrs_since_final_obs']>12),'emissions_MtCo2_base2030'] = df_select['emissions_MtCo2_finaly']+com_transp_emis_trend1930*12
    df_select.loc[(df_select['sector']=='Commercial Transport') & (df_select['emissions_MtCo2_base2030']<0), 'emissions_MtCo2_base2030'] = 0
    df_select.loc[(df_select['sector']=='Commercial Transport') & (df_select['yrs_since_final_obs']>0), 'emissions_MtCo2_output'] = df_select['emissions_MtCo2_base2030']
    df_select.loc[(df_select['sector']=='Commercial Transport') & (df_select['yrs_since_final_obs']>12) & (df_select['emissions_MtCo2_base2030']<=0), 'emissions_MtCo2_output'] = com_transp_emis_trend3150*(df_select['yrs_since_final_obs']-12)
    df_select.loc[(df_select['sector']=='Commercial Transport') & (df_select['yrs_since_final_obs']>12) & (df_select['emissions_MtCo2_base2030']>0), 'emissions_MtCo2_output'] =  df_select['emissions_MtCo2_base2030'] + com_transp_emis_trend3150*(df_select['yrs_since_final_obs']-12)
    df_select.loc[(df_select['sector']=='Commercial Transport') & (df_select['emissions_MtCo2_output']<0), 'emissions_MtCo2_output'] = 0
    ### 'Construction' emmissions: 
    df_select.loc[(df_select['sector']=='Construction') & (df_select['yrs_since_final_obs']>0) & (df_select['yrs_since_final_obs']),'emissions_MtCo2_base2030'] = df_select['emissions_MtCo2_finaly']+construction_emis_trend1930*df_select['yrs_since_final_obs']
    df_select.loc[(df_select['sector']=='Construction') & (df_select['yrs_since_final_obs']>12),'emissions_MtCo2_base2030'] = df_select['emissions_MtCo2_finaly']+construction_emis_trend1930*12
    df_select.loc[(df_select['sector']=='Construction') & (df_select['emissions_MtCo2_base2030']<0), 'emissions_MtCo2_base2030'] = 0
    df_select.loc[(df_select['sector']=='Construction') & (df_select['yrs_since_final_obs']>0), 'emissions_MtCo2_output'] = df_select['emissions_MtCo2_base2030']
    df_select.loc[(df_select['sector']=='Construction') & (df_select['yrs_since_final_obs']>12) & (df_select['emissions_MtCo2_base2030']<=0), 'emissions_MtCo2_output'] = construction_emis_trend3150*(df_select['yrs_since_final_obs']-12)
    df_select.loc[(df_select['sector']=='Construction') & (df_select['yrs_since_final_obs']>12) & (df_select['emissions_MtCo2_base2030']>0), 'emissions_MtCo2_output'] =  df_select['emissions_MtCo2_base2030'] + construction_emis_trend3150*(df_select['yrs_since_final_obs']-12)
    df_select.loc[(df_select['sector']=='Construction') & (df_select['emissions_MtCo2_output']<0), 'emissions_MtCo2_output'] = 0
    ### 'Electricity generation' emmissions: 
    df_select.loc[(df_select['sector']=='Electricity generation') & (df_select['yrs_since_final_obs']>0) & (df_select['yrs_since_final_obs']),'emissions_MtCo2_base2030'] = df_select['emissions_MtCo2_finaly']+electricity_emis_trend1930*df_select['yrs_since_final_obs']
    df_select.loc[(df_select['sector']=='Electricity generation') & (df_select['yrs_since_final_obs']>12),'emissions_MtCo2_base2030'] = df_select['emissions_MtCo2_finaly']+electricity_emis_trend1930*12
    df_select.loc[(df_select['sector']=='Electricity generation') & (df_select['emissions_MtCo2_base2030']<0), 'emissions_MtCo2_base2030'] = 0
    df_select.loc[(df_select['sector']=='Electricity generation') & (df_select['yrs_since_final_obs']>0), 'emissions_MtCo2_output'] = df_select['emissions_MtCo2_base2030']
    df_select.loc[(df_select['sector']=='Electricity generation') & (df_select['yrs_since_final_obs']>12) & (df_select['emissions_MtCo2_base2030']<=0), 'emissions_MtCo2_output'] = electricity_emis_trend3150 * (df_select['yrs_since_final_obs'] - 12)
    df_select.loc[(df_select['sector']=='Electricity generation') & (df_select['yrs_since_final_obs']>12) & (df_select['emissions_MtCo2_base2030']>0), 'emissions_MtCo2_output'] =  df_select['emissions_MtCo2_base2030'] + electricity_emis_trend3150 * (df_select['yrs_since_final_obs'] - 12)
    df_select.loc[(df_select['sector']=='Electricity generation') & (df_select['emissions_MtCo2_output']<0), 'emissions_MtCo2_output'] = 0
    ### 'Gas, Water & Waste Services' emmissions: 
    df_select.loc[(df_select['sector']=='Gas, Water & Waste Services') & (df_select['yrs_since_final_obs']>0) & (df_select['yrs_since_final_obs']),'emissions_MtCo2_base2030'] = df_select['emissions_MtCo2_finaly'] + gas_water_waste_emis_trend1930 * df_select['yrs_since_final_obs']
    df_select.loc[(df_select['sector']=='Gas, Water & Waste Services') & (df_select['yrs_since_final_obs']>12),'emissions_MtCo2_base2030'] = df_select['emissions_MtCo2_finaly']+gas_water_waste_emis_trend1930 * 12
    df_select.loc[(df_select['sector']=='Gas, Water & Waste Services') & (df_select['emissions_MtCo2_base2030']<0), 'emissions_MtCo2_base2030'] = 0
    df_select.loc[(df_select['sector']=='Gas, Water & Waste Services') & (df_select['yrs_since_final_obs']>0), 'emissions_MtCo2_output'] = df_select['emissions_MtCo2_base2030']
    df_select.loc[(df_select['sector']=='Gas, Water & Waste Services') & (df_select['yrs_since_final_obs']>12) & (df_select['emissions_MtCo2_base2030']<=0), 'emissions_MtCo2_output'] = gas_water_waste_emis_trend3150 * (df_select['yrs_since_final_obs'] - 12)
    df_select.loc[(df_select['sector']=='Gas, Water & Waste Services') & (df_select['yrs_since_final_obs']>12) & (df_select['emissions_MtCo2_base2030']>0), 'emissions_MtCo2_output'] =  df_select['emissions_MtCo2_base2030'] + gas_water_waste_emis_trend3150 * (df_select['yrs_since_final_obs']-12)
    df_select.loc[(df_select['sector']=='Gas, Water & Waste Services') & (df_select['emissions_MtCo2_output']<0), 'emissions_MtCo2_output'] = 0
    ### 'Manufacturing' emmissions: 
    df_select.loc[(df_select['sector']=='Manufacturing') & (df_select['yrs_since_final_obs']>0) & (df_select['yrs_since_final_obs']),'emissions_MtCo2_base2030'] = df_select['emissions_MtCo2_finaly'] + manufacturing_emis_trend1930 * df_select['yrs_since_final_obs']
    df_select.loc[(df_select['sector']=='Manufacturing') & (df_select['yrs_since_final_obs']>12),'emissions_MtCo2_base2030'] = df_select['emissions_MtCo2_finaly'] + manufacturing_emis_trend1930 * 12
    df_select.loc[(df_select['sector']=='Manufacturing') & (df_select['emissions_MtCo2_base2030']<0), 'emissions_MtCo2_base2030'] = 0
    df_select.loc[(df_select['sector']=='Manufacturing') & (df_select['yrs_since_final_obs']>0), 'emissions_MtCo2_output'] = df_select['emissions_MtCo2_base2030']
    df_select.loc[(df_select['sector']=='Manufacturing') & (df_select['yrs_since_final_obs']>12) & (df_select['emissions_MtCo2_base2030']<=0), 'emissions_MtCo2_output'] = manufacturing_emis_trend3150*(df_select['yrs_since_final_obs']-12)
    df_select.loc[(df_select['sector']=='Manufacturing') & (df_select['yrs_since_final_obs']>12) & (df_select['emissions_MtCo2_base2030']>0), 'emissions_MtCo2_output'] =  df_select['emissions_MtCo2_base2030'] + manufacturing_emis_trend3150*(df_select['yrs_since_final_obs']-12)
    df_select.loc[(df_select['sector']=='Manufacturing') & (df_select['emissions_MtCo2_output']<0), 'emissions_MtCo2_output'] = 0
    ### Mining' emmissions: 
    df_select.loc[(df_select['sector']=='Mining') & (df_select['yrs_since_final_obs']>0) & (df_select['yrs_since_final_obs']),'emissions_MtCo2_base2030'] = df_select['emissions_MtCo2_finaly']+mining_emis_trend1930*df_select['yrs_since_final_obs']
    df_select.loc[(df_select['sector']=='Mining') & (df_select['yrs_since_final_obs']>12),'emissions_MtCo2_base2030'] = df_select['emissions_MtCo2_finaly'] + mining_emis_trend1930*12
    df_select.loc[(df_select['sector']=='Mining') & (df_select['emissions_MtCo2_base2030']<0), 'emissions_MtCo2_base2030'] = 0
    df_select.loc[(df_select['sector']=='Mining') & (df_select['yrs_since_final_obs']>0), 'emissions_MtCo2_output'] = df_select['emissions_MtCo2_base2030']
    df_select.loc[(df_select['sector']=='Mining') & (df_select['yrs_since_final_obs']>12) & (df_select['emissions_MtCo2_base2030']<=0), 'emissions_MtCo2_output'] = mining_emis_trend3150*(df_select['yrs_since_final_obs']-12)
    df_select.loc[(df_select['sector']=='Mining') & (df_select['yrs_since_final_obs']>12) & (df_select['emissions_MtCo2_base2030']>0), 'emissions_MtCo2_output'] =  df_select['emissions_MtCo2_base2030'] + mining_emis_trend3150*(df_select['yrs_since_final_obs']-12)
    df_select.loc[(df_select['sector']=='Mining') & (df_select['emissions_MtCo2_output']<0), 'emissions_MtCo2_output'] = 0
    ### 'Residential' emmissions: 
    df_select.loc[(df_select['sector']=='Residential') & (df_select['yrs_since_final_obs']>0) & (df_select['yrs_since_final_obs']),'emissions_MtCo2_base2030'] = df_select['emissions_MtCo2_finaly']+residential_emis_trend1930*df_select['yrs_since_final_obs']
    df_select.loc[(df_select['sector']=='Residential') & (df_select['yrs_since_final_obs']>12),'emissions_MtCo2_base2030'] = df_select['emissions_MtCo2_finaly']+residential_emis_trend1930*12
    df_select.loc[(df_select['sector']=='Residential') & (df_select['emissions_MtCo2_base2030']<0), 'emissions_MtCo2_base2030'] = 0
    df_select.loc[(df_select['sector']=='Residential') & (df_select['yrs_since_final_obs']>0), 'emissions_MtCo2_output'] = df_select['emissions_MtCo2_base2030']
    df_select.loc[(df_select['sector']=='Residential') & (df_select['yrs_since_final_obs']>12) & (df_select['emissions_MtCo2_base2030']<=0), 'emissions_MtCo2_output'] = residential_emis_trend3150 * (df_select['yrs_since_final_obs'] - 12)
    df_select.loc[(df_select['sector']=='Residential') & (df_select['yrs_since_final_obs']>12) & (df_select['emissions_MtCo2_base2030']>0), 'emissions_MtCo2_output'] = df_select['emissions_MtCo2_base2030'] + residential_emis_trend3150 * (df_select['yrs_since_final_obs'] - 12)
    df_select.loc[(df_select['sector']=='Residential') & (df_select['emissions_MtCo2_output']<0), 'emissions_MtCo2_output'] = 0
    ### 'Services' emmissions: 
    df_select.loc[(df_select['sector']=='Services') & (df_select['yrs_since_final_obs']>0) & (df_select['yrs_since_final_obs']),'emissions_MtCo2_base2030'] = df_select['emissions_MtCo2_finaly']+services_emis_trend1930*df_select['yrs_since_final_obs']
    df_select.loc[(df_select['sector']=='Services') & (df_select['yrs_since_final_obs']>12),'emissions_MtCo2_base2030'] = df_select['emissions_MtCo2_finaly']+services_emis_trend1930*12
    df_select.loc[(df_select['sector']=='Services') & (df_select['emissions_MtCo2_base2030']<0), 'emissions_MtCo2_base2030'] = 0
    df_select.loc[(df_select['sector']=='Services') & (df_select['yrs_since_final_obs']>0), 'emissions_MtCo2_output'] = df_select['emissions_MtCo2_base2030']
    df_select.loc[(df_select['sector']=='Services') & (df_select['yrs_since_final_obs']>12) & (df_select['emissions_MtCo2_base2030']<=0), 'emissions_MtCo2_output'] = services_emis_trend3150*(df_select['yrs_since_final_obs']-12)
    df_select.loc[(df_select['sector']=='Services') & (df_select['yrs_since_final_obs']>12) & (df_select['emissions_MtCo2_base2030']>0), 'emissions_MtCo2_output'] =  df_select['emissions_MtCo2_base2030'] + services_emis_trend3150*(df_select['yrs_since_final_obs']-12)
    df_select.loc[(df_select['sector']=='Services') & (df_select['emissions_MtCo2_output']<0), 'emissions_MtCo2_output'] = 0
    ### LULUCF emissions: 
    ### Note again these may go negative. Also input and calculation is much more straightfoward: annual level plus annual growth*years since last obs
    df_select.loc[(df_select['sector']=='LULUCF') & (df_select['yrs_since_final_obs']>0),'emissions_MtCo2_output'] = lulucf_emis_base1930 + lulucf_emis_growth1930 * df_select['yrs_since_final_obs']
    df_select.loc[(df_select['sector']=='LULUCF') & (df_select['yrs_since_final_obs']>12),'emissions_MtCo2_output'] = lulucf_emis_base3150 + lulucf_emis_growth3150 * (df_select['yrs_since_final_obs'] - 12)

### ### Value added: only since 2009
    ### For value added trends, we need picker 1 plus picker value 
    df_select.loc[(df_select['sector']=='Services') & (df_select['yrs_since_final_obs']>0),'ind_val_add_output'] = df_select['ind_val_add_2019_bln_finaly'] * np.power((1+(services_valadd_trend/100)),df_select['yrs_since_final_obs'])
    df_select.loc[(df_select['sector']=='Mining') & (df_select['yrs_since_final_obs']>0),'ind_val_add_output'] = df_select['ind_val_add_2019_bln_finaly']*np.power((1+(mining_valadd_trend/100)),df_select['yrs_since_final_obs'])
    df_select.loc[(df_select['sector']=='Manufacturing') & (df_select['yrs_since_final_obs']>0),'ind_val_add_output'] = df_select['ind_val_add_2019_bln_finaly']*np.power((1+(manufacturing_valadd_trend/100)),df_select['yrs_since_final_obs'])
    df_select.loc[(df_select['sector']=='Gas, Water & Waste Services') & (df_select['yrs_since_final_obs']>0),'ind_val_add_output'] = df_select['ind_val_add_2019_bln_finaly']*np.power((1+(gas_water_waste_valadd_trend/100)),df_select['yrs_since_final_obs'])
    df_select.loc[(df_select['sector']=='Construction') & (df_select['yrs_since_final_obs']>0),'ind_val_add_output'] = df_select['ind_val_add_2019_bln_finaly']*np.power((1+(construction_valadd_trend/100)),df_select['yrs_since_final_obs'])
    df_select.loc[(df_select['sector']=='Commercial Transport') & (df_select['yrs_since_final_obs']>0),'ind_val_add_output'] = df_select['ind_val_add_2019_bln_finaly']*np.power((1+(com_transp_valadd_trend/100)),df_select['yrs_since_final_obs'])
    df_select.loc[(df_select['sector']=='Agriculture & Forestry') & (df_select['yrs_since_final_obs']>0),'ind_val_add_output'] = df_select['ind_val_add_2019_bln_finaly']*np.power((1+(agrifor_valadd_trend/100)),df_select['yrs_since_final_obs'])
    df_select.loc[(df_select['sector']=='Electricity generation') & (df_select['yrs_since_final_obs']>0),'ind_val_add_output'] = df_select['ind_val_add_2019_bln_finaly']*np.power((1+(electricity_valadd_trend/100)),df_select['yrs_since_final_obs'])

### ### Emission intensity calculation, also only since 2009:
    df_select['emis_int_outp']=df_select['emissions_MtCo2_output']/df_select['ind_val_add_output']
    df_select_emis_int = df_select[df_select.sector != 'LULUCF']
    df_select_emis_int = df_select_emis_int[df_select_emis_int.sector != 'Residential']
    df_select_emis_int = df_select_emis_int[df_select_emis_int.year>= 2009]

### ### Electricity generation and emission intensity dynamically based on picker input
    df_select_elec = df_select[(df_select['sector']=="Electricity generation")]
    ### Calculate growth of electricity output in GWh (same growth as with value added):
    df_select_elec.loc[(df_select_elec['yrs_since_final_obs']>0),'elec_gen_GWh_output'] = df_select_elec['elec_gen_GWh_finaly']*np.power((1+(electricity_growth_trend/100)),df_select_elec['yrs_since_final_obs'])
    ### Calculate emission intensity (note emissions have been calculated above):
    df_select_elec['elec_carb_int_outp']=1000 * df_select_elec['emissions_MtCo2_output'] / df_select_elec['elec_gen_GWh_output']
    ### Roudn the carbon intentsity
    df_select_elec['elec_carb_int_outp']=round(df_select_elec['elec_carb_int_outp'],2)
    df_select_elec['elec_gen_GWh_output']=round(df_select_elec['elec_gen_GWh_output'],0)

### ### Round numbers to be displayed in graphs and tables
    df_select['emissions_MtCo2_output_orig_decimals'] = df_select['emissions_MtCo2_output']
    if tab in smallnumberstates:
        df_select['emissions_MtCo2_output']=round(df_select['emissions_MtCo2_output'],2)
    else:
        df_select['emissions_MtCo2_output']=round(df_select['emissions_MtCo2_output'],1)
### # Other stuff sournded equally
    df_select['ind_val_add_output']=round(df_select['ind_val_add_output'],1)
    df_select_emis_int['emis_int_outp']=round(df_select['emis_int_outp'],2)
    df_select['elec_carb_int_outp']=round(df_select['elec_carb_int_outp'],2)
    df_select['elec_gen_GWh_output']=round(df_select['elec_gen_GWh_output'],0)

### ### Calculate the emission reductions
    df_select['emis_reduc']= -100 * (1 - (df_select['emissions_MtCo2_output'] / df_select['emissions_MtCo2_baseyear']))
### ### Sensible decimal numbers for the emission reductions, and add percentage symbol here    
    df_select['emis_reduc']=round(df_select['emis_reduc'],1)
    df_select['emis_reduc']=df_select['emis_reduc'].apply(str)
    df_select['emis_reduc']=df_select['emis_reduc'] + '%'

### ### Define emissions total figure with dynamic input
    # Temp rename agri sector
    df_select['sector'] = df_select['sector'].str.replace(re.escape('Agriculture & Forestry'),'Agriculture')
    fig_emissions_total = px.area(df_select, x="year", y="emissions_MtCo2_output", color="sector",
                                  color_discrete_map=my_discrete_color_map,
                                  labels={"year": "", "emissions_MtCo2_output": "CO<sub>2</sub> Emissions (Mt CO<sub>2</sub>-eq/y)"},
                                  title="CO<sub>2</sub> Emissions by sector",
                                  width=695, height=375)
    fig_emissions_total.update_layout(transition_duration=350,
                                      template="plotly_white",
                                      legend_traceorder="reversed",
                                      title_font_color="#1F77B4",
                                      title_font_size=18,
                                      title_font_family="Rockwell",
                                      title_x=0.02,
                                      margin=dict(t=40, r=0, b=0, l=65, pad=0))
    fig_emissions_total.update_xaxes(showline=True, linewidth=1, linecolor='black', gridcolor='rgba(149, 165, 166, 0.6)', mirror=True)
    fig_emissions_total.update_yaxes(showline=True, linewidth=1, linecolor='black', gridcolor='rgba(149, 165, 166, 0.6)', mirror=True)
    # Rename agri sector again
    df_select['sector'] = df_select['sector'].str.replace(re.escape('Agriculture'),'Agriculture & Forestry')
    
### ### Define value added figure with dynamic input
    df_select_val_add = df_select[df_select.sector != 'LULUCF']
    df_select_val_add = df_select_val_add[df_select_val_add.sector != 'Residential']
    df_select_val_add = df_select_val_add[df_select_val_add.year>= 2009]
    fig_added_value_total = px.area(df_select_val_add, x="year", y="ind_val_add_output", color="sector",
                                    color_discrete_map=my_discrete_color_map,
                                    labels={"year": "", "ind_val_add_output": "Value added (billion 2019 AUD)<sub> </sub>"},
                                    title="Value added by sector",
                                    width=700, height=375)
    fig_added_value_total.update_layout(transition_duration=350,
                                        template="plotly_white",
                                        legend_traceorder="reversed",
                                        title_font_color="#1F77B4",
                                        title_font_size=18,
                                        title_font_family="Rockwell",
                                        title_x=0.02,
                                        margin=dict(t=40, r=0, b=0, l=65, pad=0))
    fig_added_value_total.update_xaxes(showline=True, linewidth=1, linecolor='black', gridcolor='rgba(149, 165, 166, 0.6)', mirror=True)
    fig_added_value_total.update_yaxes(showline=True, linewidth=1, linecolor='black', gridcolor='rgba(149, 165, 166, 0.6)', mirror=True)

### ### Emission intensity graph with dynamic input
    fig_emis_int = px.line(df_select_emis_int, x="year", y="emis_int_outp", color="sector",
                           color_discrete_sequence=['#D62728', '#2CA02C', '#9467BD', '#8C564B', '#E377C2', '#BCBD22', '#7F7F7F', '#17BECF'],
                           labels={"year": "", "emis_int_outp": "Emission intensity (kg CO<sub>2</sub>-eq/2019 AUD)"},
                           title="Emission intensity by sector",
                           width=700, height=375)
    fig_emis_int.update_layout(template="plotly_white",
                                        legend_traceorder="reversed",
                                        title_font_color="#1F77B4",
                                        title_font_size=18,
                                        title_font_family="Rockwell",
                                        title_x=0.02,
                                        margin=dict(t=40, r=0, b=0, l=65, pad=0))
    fig_emis_int.update_xaxes(showline=True, linewidth=1, linecolor='black', gridcolor='rgba(149, 165, 166, 0.6)', mirror=True)
    fig_emis_int.update_yaxes(showline=True, linewidth=1, linecolor='black', gridcolor='rgba(149, 165, 166, 0.6)', mirror=True)

### ### Redefine Electricity generation and carbon intensity figure again, but with dynamic input
    # Make dictionary for dual y-axis figure
    year_dict = df_select_elec['year'].tolist()
    gwh_dict = df_select_elec['elec_gen_GWh_output'].tolist()
    elec_carb_int_dict = df_select_elec['elec_carb_int_outp'].tolist()
    # create df_select_elec
    fig_elec_gen_int = make_subplots(specs=[[{"secondary_y": True}]])
    # Add traces
    fig_elec_gen_int.add_scatter(x=year_dict, y=elec_carb_int_dict, name="Carbon intensity", mode="lines", line=dict(width=2, color="black"), secondary_y=False)
    fig_elec_gen_int.add_scatter(x=year_dict, y=gwh_dict, name="Electricity generation", mode="lines", line=dict(width=2, color="rgba(214,39,40,1)"), secondary_y=True)
    fig_elec_gen_int.update_layout(template="plotly_white",
                                   legend_traceorder="reversed",
                                   title_text="Electricity generation and carbon intensity",
                                   title_font_color="#1F77B4",
                                   title_font_size=18,
                                   title_font_family="Rockwell",
                                   title_x=0.02,
                                   margin=dict(t=40, r=0, b=0, l=65, pad=0),
                                   width=675, height=340)
    fig_elec_gen_int.update_xaxes(showline=True, linewidth=1, linecolor='black', gridcolor='rgba(149, 165, 166, 0.6)', mirror=True)
    fig_elec_gen_int.update_yaxes(showline=True, linewidth=1, linecolor='black', gridcolor='rgba(149, 165, 166, 0.6)', mirror=True)
    # Set y-axes titles
    fig_elec_gen_int.update_yaxes(title_text="Carbon intensity (kg CO<sub>2</sub>-eq/kWh)", secondary_y=False)
    fig_elec_gen_int.update_yaxes(title_text="Electricity generation (GWh)<sub> </sub>", secondary_y=True)
    # y-axis range
    max_elec_gen_int = max(elec_carb_int_dict) + 0.2
    fig_elec_gen_int.update_layout(yaxis=dict(range=[0,max_elec_gen_int]))

### ### Update all the pathway result outputs
    # Emission reduction: services
    services_emisred_2018 = df_select.loc[(df_select['sector']=='Services') & (df_select['year']==2018),'emis_reduc']
    services_emisred_2030 = df_select.loc[(df_select['sector']=='Services') & (df_select['year']==2030),'emis_reduc']
    services_emisred_2040 = df_select.loc[(df_select['sector']=='Services') & (df_select['year']==2040),'emis_reduc']
    services_emisred_2050 = df_select.loc[(df_select['sector']=='Services') & (df_select['year']==2050),'emis_reduc']
    # Emission reduction: mining
    mining_emisred_2018 = df_select.loc[(df_select['sector']=='Mining') & (df_select['year']==2018),'emis_reduc']
    mining_emisred_2030 = df_select.loc[(df_select['sector']=='Mining') & (df_select['year']==2030),'emis_reduc']
    mining_emisred_2040 = df_select.loc[(df_select['sector']=='Mining') & (df_select['year']==2040),'emis_reduc']
    mining_emisred_2050 = df_select.loc[(df_select['sector']=='Mining') & (df_select['year']==2050),'emis_reduc']
    # Emission reduction: manufacturing
    manufacturing_emisred_2018 = df_select.loc[(df_select['sector']=='Manufacturing') & (df_select['year']==2018),'emis_reduc']
    manufacturing_emisred_2030 = df_select.loc[(df_select['sector']=='Manufacturing') & (df_select['year']==2030),'emis_reduc']
    manufacturing_emisred_2040 = df_select.loc[(df_select['sector']=='Manufacturing') & (df_select['year']==2040),'emis_reduc']
    manufacturing_emisred_2050 = df_select.loc[(df_select['sector']=='Manufacturing') & (df_select['year']==2050),'emis_reduc']
    # Emission reduction: Gas, water & waste
    gas_water_waste_emisred_2018 = df_select.loc[(df_select['sector']=='Gas, Water & Waste Services') & (df_select['year']==2018),'emis_reduc']
    gas_water_waste_emisred_2030 = df_select.loc[(df_select['sector']=='Gas, Water & Waste Services') & (df_select['year']==2030),'emis_reduc']
    gas_water_waste_emisred_2040 = df_select.loc[(df_select['sector']=='Gas, Water & Waste Services') & (df_select['year']==2040),'emis_reduc']
    gas_water_waste_emisred_2050 = df_select.loc[(df_select['sector']=='Gas, Water & Waste Services') & (df_select['year']==2050),'emis_reduc']
    # Emission reduction: Construction
    construction_emisred_2018 = df_select.loc[(df_select['sector']=='Construction') & (df_select['year']==2018),'emis_reduc']
    construction_emisred_2030 = df_select.loc[(df_select['sector']=='Construction') & (df_select['year']==2030),'emis_reduc']
    construction_emisred_2040 = df_select.loc[(df_select['sector']=='Construction') & (df_select['year']==2040),'emis_reduc']
    construction_emisred_2050 = df_select.loc[(df_select['sector']=='Construction') & (df_select['year']==2050),'emis_reduc']
    # Emission reduction: Commercial transport
    com_transp_emisred_2018 = df_select.loc[(df_select['sector']=='Commercial Transport') & (df_select['year']==2018),'emis_reduc']
    com_transp_emisred_2030 = df_select.loc[(df_select['sector']=='Commercial Transport') & (df_select['year']==2030),'emis_reduc']
    com_transp_emisred_2040 = df_select.loc[(df_select['sector']=='Commercial Transport') & (df_select['year']==2040),'emis_reduc']
    com_transp_emisred_2050 = df_select.loc[(df_select['sector']=='Commercial Transport') & (df_select['year']==2050),'emis_reduc']
    # Emission reduction: Agriculture & Forestry
    agrifor_emisred_2018 = df_select.loc[(df_select['sector']=='Agriculture & Forestry') & (df_select['year']==2018),'emis_reduc']
    agrifor_emisred_2030 = df_select.loc[(df_select['sector']=='Agriculture & Forestry') & (df_select['year']==2030),'emis_reduc']
    agrifor_emisred_2040 = df_select.loc[(df_select['sector']=='Agriculture & Forestry') & (df_select['year']==2040),'emis_reduc']
    agrifor_emisred_2050 = df_select.loc[(df_select['sector']=='Agriculture & Forestry') & (df_select['year']==2050),'emis_reduc']
    # Emission reduction: Residential
    residential_emisred_2018 = df_select.loc[(df_select['sector']=='Residential') & (df_select['year']==2018),'emis_reduc']
    residential_emisred_2030 = df_select.loc[(df_select['sector']=='Residential') & (df_select['year']==2030),'emis_reduc']
    residential_emisred_2040 = df_select.loc[(df_select['sector']=='Residential') & (df_select['year']==2040),'emis_reduc']
    residential_emisred_2050 = df_select.loc[(df_select['sector']=='Residential') & (df_select['year']==2050),'emis_reduc']
    # Emission reduction: Electricity
    electricity_emisred_2018 = df_select.loc[(df_select['sector']=='Electricity generation') & (df_select['year']==2018),'emis_reduc']
    electricity_emisred_2030 = df_select.loc[(df_select['sector']=='Electricity generation') & (df_select['year']==2030),'emis_reduc']
    electricity_emisred_2040 = df_select.loc[(df_select['sector']=='Electricity generation') & (df_select['year']==2040),'emis_reduc']
    electricity_emisred_2050 = df_select.loc[(df_select['sector']=='Electricity generation') & (df_select['year']==2050),'emis_reduc']

### # 2018 and 2050 emissions in Mt by sector
    # For layout with Mt
    df_select['emissions_MtCo2_output_Mt'] = df_select['emissions_MtCo2_output'].apply(str)
    df_select['emissions_MtCo2_output_Mt'] = df_select['emissions_MtCo2_output_Mt'] + ' Mt'
    services_emis_2018 = df_select.loc[(df_select['sector']=='Services') & (df_select['year']==2018),'emissions_MtCo2_output_Mt']
    mining_emis_2018 = df_select.loc[(df_select['sector']=='Mining') & (df_select['year']==2018),'emissions_MtCo2_output_Mt']
    manufacturing_emis_2018 = df_select.loc[(df_select['sector']=='Manufacturing') & (df_select['year']==2018),'emissions_MtCo2_output_Mt']
    gas_water_waste_emis_2018 = df_select.loc[(df_select['sector']=='Gas, Water & Waste Services') & (df_select['year']==2018),'emissions_MtCo2_output_Mt']
    construction_emis_2018 = df_select.loc[(df_select['sector']=='Construction') & (df_select['year']==2018),'emissions_MtCo2_output_Mt']
    com_transp_emis_2018 = df_select.loc[(df_select['sector']=='Commercial Transport') & (df_select['year']==2018),'emissions_MtCo2_output_Mt']
    agrifor_emis_2018 = df_select.loc[(df_select['sector']=='Agriculture & Forestry') & (df_select['year']==2018),'emissions_MtCo2_output_Mt']
    residential_emis_2018 = df_select.loc[(df_select['sector']=='Residential') & (df_select['year']==2018),'emissions_MtCo2_output_Mt']
    electricity_emis_2018 = df_select.loc[(df_select['sector']=='Electricity generation') & (df_select['year']==2018),'emissions_MtCo2_output_Mt']
    services_emis_2050 = df_select.loc[(df_select['sector']=='Services') & (df_select['year']==2050),'emissions_MtCo2_output_Mt']
    mining_emis_2050 = df_select.loc[(df_select['sector']=='Mining') & (df_select['year']==2050),'emissions_MtCo2_output_Mt']
    manufacturing_emis_2050 = df_select.loc[(df_select['sector']=='Manufacturing') & (df_select['year']==2050),'emissions_MtCo2_output_Mt']
    gas_water_waste_emis_2050 = df_select.loc[(df_select['sector']=='Gas, Water & Waste Services') & (df_select['year']==2050),'emissions_MtCo2_output_Mt']
    construction_emis_2050 = df_select.loc[(df_select['sector']=='Construction') & (df_select['year']==2050),'emissions_MtCo2_output_Mt']
    com_transp_emis_2050 = df_select.loc[(df_select['sector']=='Commercial Transport') & (df_select['year']==2050),'emissions_MtCo2_output_Mt']
    agrifor_emis_2050 = df_select.loc[(df_select['sector']=='Agriculture & Forestry') & (df_select['year']==2050),'emissions_MtCo2_output_Mt']
    residential_emis_2050 = df_select.loc[(df_select['sector']=='Residential') & (df_select['year']==2050),'emissions_MtCo2_output_Mt']
    electricity_emis_2050 = df_select.loc[(df_select['sector']=='Electricity generation') & (df_select['year']==2050),'emissions_MtCo2_output_Mt']

### # Total emissions and emissions reductions
    # Net emission reductions %
    df_select_netpc = df_select
    df_select_netpc = df_select_netpc.groupby(['geo', 'year'], as_index=False).agg({'emissions_MtCo2_output':'sum',
                                                                                  'emissions_MtCo2_output_orig_decimals': 'sum',
                                                                                  'ind_val_add_output': 'sum',
                                                                                  'emissions_MtCo2_baseyear': 'sum'})
    df_select_netpc['emis_reduc']= -100 * (1 - (df_select_netpc['emissions_MtCo2_output'] / df_select_netpc['emissions_MtCo2_baseyear']))
    # Net emission intensity index
    df_select_netpc['emis_int_output'] = df_select_netpc['emissions_MtCo2_output_orig_decimals'] / df_select_netpc['ind_val_add_output']
    df_select_netpc['emis_int_baseyear'] = np.where(df_select_netpc['year'] == 2010, df_select_netpc['emis_int_output'], 0)
    df_select_netpc['emis_int_baseyear'] = df_select_netpc.emis_int_baseyear.max()
    df_select_netpc['emis_int_index'] =  100 * df_select_netpc['emis_int_output'] / df_select_netpc['emis_int_baseyear']
    
    # Gross emission reductions: stick lulucf in separate column. And get rid of LULUCF emissions for calculation of reduction %ages
    df_select_summ = df_select
    df_select_summ['lulucf'] = df_select_summ['emissions_MtCo2_output']
    df_select_summ.loc[df_select_summ['sector'] == 'LULUCF', 'emissions_MtCo2_output'] = 0
    df_select_summ.loc[df_select_summ['sector'] == 'LULUCF', 'emissions_MtCo2_output_orig_decimals'] = 0
    df_select_summ.loc[df_select_summ['sector'] == 'LULUCF', 'emissions_MtCo2_baseyear'] = 0
    df_select_summ.loc[df_select_summ['sector'] != 'LULUCF', 'lulucf'] = 0
    # Total emissions, value added, and lulucf
    df_select_summ = df_select_summ.groupby(['geo', 'year'], as_index=False).agg({'emissions_MtCo2_output':'sum',
                                                                                  'emissions_MtCo2_output_orig_decimals': 'sum',
                                                                                  'ind_val_add_output': 'sum',
                                                                                  'emissions_MtCo2_baseyear': 'sum',
                                                                                  'lulucf': 'sum',
                                                                                  'population': 'min'})
    df_select_summ['emis_reduc']= -100 * (1 - (df_select_summ['emissions_MtCo2_output'] / df_select_summ['emissions_MtCo2_baseyear']))
    df_select_summ['net_emis']=df_select_summ['emissions_MtCo2_output'] + df_select_summ['lulucf']
    

    
### ### Emission reductiosn Mt
    # For 2009-2018
    df_select_summ['emissions_MtCo2_output_lag10'] = df_select_summ['emissions_MtCo2_output_orig_decimals'].shift(9)
    df_select_summ['avg_annu_emis_grow_Mt'] = 0.1 * (df_select_summ['emissions_MtCo2_output_orig_decimals'] - df_select_summ['emissions_MtCo2_output_lag10'])
    if tab in smallnumberstates:
        df_select_summ['avg_annu_emis_grow_Mt']=round(df_select_summ['avg_annu_emis_grow_Mt'], 3)
    else:
        df_select_summ['avg_annu_emis_grow_Mt']=round(df_select_summ['avg_annu_emis_grow_Mt'], 2)
    df_select_summ['avg_annu_emis_grow_Mt'] = df_select_summ['avg_annu_emis_grow_Mt'].apply(str)
    df_select_summ['avg_annu_emis_grow_Mt'] = df_select_summ['avg_annu_emis_grow_Mt'] + ' Mt'
    total_emisred_Mt_hist = df_select_summ.loc[df_select_summ['year'] == 2018, 'avg_annu_emis_grow_Mt']
    # For 2019-2030 & 2031-2050
    df_select_summ['emissions_MtCo2_output_lag1'] = df_select_summ['emissions_MtCo2_output_orig_decimals'].shift(1)
    df_select_summ['annu_emis_grow_Mt'] = df_select_summ['emissions_MtCo2_output_orig_decimals'] - df_select_summ['emissions_MtCo2_output_lag1']
    if tab in smallnumberstates:
        df_select_summ['annu_emis_grow_Mt']=round(df_select_summ['annu_emis_grow_Mt'], 3)
    else:
        df_select_summ['annu_emis_grow_Mt']=round(df_select_summ['annu_emis_grow_Mt'], 2)
    df_select_summ['annu_emis_grow_Mt'] = df_select_summ['annu_emis_grow_Mt'].apply(str)
    df_select_summ['annu_emis_grow_Mt'] = df_select_summ['annu_emis_grow_Mt'] + ' Mt'
    total_emisred_Mt_1930 = df_select_summ.loc[df_select_summ['year'] == 2019, 'annu_emis_grow_Mt']
    total_emisred_Mt_3150 = df_select_summ.loc[df_select_summ['year'] == 2031, 'annu_emis_grow_Mt']
### ### Sensible decimal numbers for the % emission reductions, and add percentage symbol here
    df_select_summ['emis_reduc']=round(df_select_summ['emis_reduc'],1)
    df_select_summ['emis_reduc']=df_select_summ['emis_reduc'].apply(str)
    df_select_summ['emis_reduc']=df_select_summ['emis_reduc'] + '%'
    # Net emission version
    df_select_netpc['emis_reduc']=round(df_select_netpc['emis_reduc'],1)
    df_select_netpc['emis_reduc']=df_select_netpc['emis_reduc'].apply(str)
    df_select_netpc['emis_reduc']=df_select_netpc['emis_reduc'] + '%'
### ### Assign variables for emission reductions % total
    total_emisred_2018 = df_select_summ.loc[df_select_summ['year'] == 2018, 'emis_reduc']
    total_emisred_2030 = df_select_summ.loc[df_select_summ['year'] == 2030, 'emis_reduc']
    total_emisred_2040 = df_select_summ.loc[df_select_summ['year'] == 2040, 'emis_reduc']
    total_emisred_2050 = df_select_summ.loc[df_select_summ['year'] == 2050, 'emis_reduc']
    # Net emission version
    net_emisred_2018 = df_select_netpc.loc[df_select_netpc['year'] == 2018, 'emis_reduc']
    net_emisred_2030 = df_select_netpc.loc[df_select_netpc['year'] == 2030, 'emis_reduc']
    net_emisred_2040 = df_select_netpc.loc[df_select_netpc['year'] == 2040, 'emis_reduc']
    net_emisred_2050 = df_select_netpc.loc[df_select_netpc['year'] == 2050, 'emis_reduc']
 
### # Gross emissions with rounding
    if tab in smallnumberstates:
        df_select_summ['emissions_MtCo2_output']=round(df_select_summ['emissions_MtCo2_output'], 2)
    else:
        df_select_summ['emissions_MtCo2_output']=round(df_select_summ['emissions_MtCo2_output'], 1)
    df_select_summ['emissions_MtCo2_output_Mt'] = df_select_summ['emissions_MtCo2_output'].apply(str)
    df_select_summ['emissions_MtCo2_output_Mt'] = df_select_summ['emissions_MtCo2_output_Mt'] + ' Mt'
    gross_emis_2018 = df_select_summ.loc[df_select_summ['year']==2018,'emissions_MtCo2_output_Mt']
    gross_emis_2030 = df_select_summ.loc[df_select_summ['year']==2030,'emissions_MtCo2_output_Mt']
    gross_emis_2040 = df_select_summ.loc[df_select_summ['year']==2040,'emissions_MtCo2_output_Mt']
    gross_emis_2050 = df_select_summ.loc[df_select_summ['year']==2050,'emissions_MtCo2_output_Mt']
    gross_emis_2018copy = gross_emis_2018
    gross_emis_2050copy = gross_emis_2050
### # LULUCF emissions
    LULUCF_2018 = df_select.loc[(df_select['sector']=='LULUCF') & (df_select['year']==2018),'emissions_MtCo2_output_Mt']
    LULUCF_2030 = df_select.loc[(df_select['sector']=='LULUCF') & (df_select['year']==2030),'emissions_MtCo2_output_Mt']
    LULUCF_2040 = df_select.loc[(df_select['sector']=='LULUCF') & (df_select['year']==2040),'emissions_MtCo2_output_Mt']
    LULUCF_2050 = df_select.loc[(df_select['sector']=='LULUCF') & (df_select['year']==2050),'emissions_MtCo2_output_Mt']
### # Net emissions
    if tab in smallnumberstates:
        df_select_summ['net_emis']=round(df_select_summ['net_emis'],2)
    else:
        df_select_summ['net_emis']=round(df_select_summ['net_emis'],1)
    df_select_summ['net_emis_Mt'] = df_select_summ['net_emis'].apply(str)
    df_select_summ['net_emis_Mt'] = df_select_summ['net_emis_Mt'] + ' Mt'
    net_emis_2018 = df_select_summ.loc[df_select_summ['year']==2018,'net_emis_Mt']
    net_emis_2030 = df_select_summ.loc[df_select_summ['year']==2030,'net_emis_Mt']
    net_emis_2040 = df_select_summ.loc[df_select_summ['year']==2040,'net_emis_Mt']
    net_emis_2050 = df_select_summ.loc[df_select_summ['year']==2050,'net_emis_Mt']
### # Emission intensity of electricity generation
    df_select_elec['elec_carb_int_outp'] = df_select_elec.elec_carb_int_outp.apply(str)
    df_select_elec['elec_carb_int_outp_g'] = df_select_elec['elec_carb_int_outp'] + ' g/kWh'
    elec_carb_int_2018 = df_select_elec.loc[df_select_elec['year']==2018,'elec_carb_int_outp_g']
    elec_carb_int_2030 = df_select_elec.loc[df_select_elec['year']==2030,'elec_carb_int_outp_g']
    elec_carb_int_2040 = df_select_elec.loc[df_select_elec['year']==2040,'elec_carb_int_outp_g']
    elec_carb_int_2050 = df_select_elec.loc[df_select_elec['year']==2050,'elec_carb_int_outp_g']
### ### Total value added changes
    # For 2009-2018
    df_select_summ['ind_val_add_output_lag10'] = df_select_summ['ind_val_add_output'].shift(9)
    df_select_summ['ind_val_add_total_hist'] = np.power(df_select_summ['ind_val_add_output'] / df_select_summ['ind_val_add_output_lag10'], 0.1)
    df_select_summ['ind_val_add_total_hist'] = 100 * (df_select_summ['ind_val_add_total_hist'] - 1)
    df_select_summ['ind_val_add_total_hist'] = round(df_select_summ['ind_val_add_total_hist'], 1)
    df_select_summ['ind_val_add_total_hist'] = df_select_summ['ind_val_add_total_hist'].apply(str)
    df_select_summ['ind_val_add_total_hist'] = df_select_summ['ind_val_add_total_hist'] + '%'
    total_val_add_hist = df_select_summ.loc[df_select_summ['year'] == 2018, 'ind_val_add_total_hist']
    # For 2019-2030 & 2031-2050
    df_select_summ['ind_val_add_output_lag1'] = df_select_summ['ind_val_add_output'].shift(1)
    df_select_summ['ind_val_add_total_1950'] = df_select_summ['ind_val_add_output'] / df_select_summ['ind_val_add_output_lag1']
    df_select_summ['ind_val_add_total_1950'] = 100 * (df_select_summ['ind_val_add_total_1950'] - 1)
    df_select_summ['ind_val_add_total_1950'] = round(df_select_summ['ind_val_add_total_1950'], 1)
    df_select_summ['ind_val_add_total_1950'] = df_select_summ['ind_val_add_total_1950'].apply(str)
    df_select_summ['ind_val_add_total_1950'] = df_select_summ['ind_val_add_total_1950'] + '%'
    total_val_add_1950 = df_select_summ.loc[df_select_summ['year'] == 2020, 'ind_val_add_total_1950']

### ### Emission intensity changes by sector
    # For 2009-2018
    df_select['emis_int_outp'] = df_select['emissions_MtCo2_output'] / df_select['ind_val_add_output']
    df_select['emis_int_outp_lag10'] = df_select['emis_int_outp'].shift(9)
    df_select['emis_int_outp_hist'] = np.power(df_select['emis_int_outp'] / df_select['emis_int_outp_lag10'], 0.1)
    df_select['emis_int_outp_hist'] = 100 * (df_select['emis_int_outp_hist'] - 1)
    df_select['emis_int_outp_hist'] = round(df_select['emis_int_outp_hist'], 1)
    df_select['emis_int_outp_hist'] = df_select['emis_int_outp_hist'].apply(str)
    df_select['emis_int_outp_hist'] = df_select['emis_int_outp_hist'] + '%'
    # For 2019-2030
    df_select['emis_int_outp_lag12'] = df_select['emis_int_outp'].shift(11)
    df_select['emis_int_outp_1930'] = np.power(df_select['emis_int_outp'] / df_select['emis_int_outp_lag12'], 1 / 12)
    df_select['emis_int_outp_1930'] = 100 * (df_select['emis_int_outp_1930'] - 1)
    df_select['emis_int_outp_1930'] = round(df_select['emis_int_outp_1930'], 1)
    df_select['emis_int_outp_1930'] = df_select['emis_int_outp_1930'].apply(str)
    df_select['emis_int_outp_1930'] = df_select['emis_int_outp_1930'] + '%'
    # For 2031-2050
    df_select['emis_int_outp_lag20'] = df_select['emis_int_outp'].shift(19)
    df_select['emis_int_outp_3150'] = np.power(df_select['emis_int_outp'] / df_select['emis_int_outp_lag20'], 1 / 20)
    df_select['emis_int_outp_3150'] = 100 * (df_select['emis_int_outp_3150'] - 1)
    df_select['emis_int_outp_3150'] = round(df_select['emis_int_outp_3150'], 1)
    df_select['emis_int_outp_3150'] = df_select['emis_int_outp_3150'].apply(str)
    df_select['emis_int_outp_3150'] = df_select['emis_int_outp_3150'] + '%'
    # Annual reductions in emission intensity: services
    services_emisint_red_2018 = df_select.loc[(df_select['sector']=='Services') & (df_select['year']==2018),'emis_int_outp_hist']
    services_emisint_red_2030 = df_select.loc[(df_select['sector']=='Services') & (df_select['year']==2030),'emis_int_outp_1930']
    services_emisint_red_2050 = df_select.loc[(df_select['sector']=='Services') & (df_select['year']==2050),'emis_int_outp_3150']
    # Annual reductions in emission intensity: Mining
    mining_emisint_red_2018 = df_select.loc[(df_select['sector']=='Mining') & (df_select['year']==2018),'emis_int_outp_hist']
    mining_emisint_red_2030 = df_select.loc[(df_select['sector']=='Mining') & (df_select['year']==2030),'emis_int_outp_1930']
    mining_emisint_red_2050 = df_select.loc[(df_select['sector']=='Mining') & (df_select['year']==2050),'emis_int_outp_3150']
    # Annual reductions in emission intensity: Manufacturing
    manufacturing_emisint_red_2018 = df_select.loc[(df_select['sector']=='Manufacturing') & (df_select['year']==2018),'emis_int_outp_hist']
    manufacturing_emisint_red_2030 = df_select.loc[(df_select['sector']=='Manufacturing') & (df_select['year']==2030),'emis_int_outp_1930']
    manufacturing_emisint_red_2050 = df_select.loc[(df_select['sector']=='Manufacturing') & (df_select['year']==2050),'emis_int_outp_3150']
    # Annual reductions in emission intensity: Gas, Water & waste services
    gas_water_waste_emisint_red_2018 = df_select.loc[(df_select['sector']=='Gas, Water & Waste Services') & (df_select['year']==2018),'emis_int_outp_hist']
    gas_water_waste_emisint_red_2030 = df_select.loc[(df_select['sector']=='Gas, Water & Waste Services') & (df_select['year']==2030),'emis_int_outp_1930']
    gas_water_waste_emisint_red_2050 = df_select.loc[(df_select['sector']=='Gas, Water & Waste Services') & (df_select['year']==2050),'emis_int_outp_3150']
    # Annual reductions in emission intensity: Construction
    construction_emisint_red_2018 = df_select.loc[(df_select['sector']=='Construction') & (df_select['year']==2018),'emis_int_outp_hist']
    construction_emisint_red_2030 = df_select.loc[(df_select['sector']=='Construction') & (df_select['year']==2030),'emis_int_outp_1930']
    construction_emisint_red_2050 = df_select.loc[(df_select['sector']=='Construction') & (df_select['year']==2050),'emis_int_outp_3150']
    # Annual reductions in emission intensity: Commercial transport
    com_transp_emisint_red_2018 = df_select.loc[(df_select['sector']=='Commercial Transport') & (df_select['year']==2018),'emis_int_outp_hist']
    com_transp_emisint_red_2030 = df_select.loc[(df_select['sector']=='Commercial Transport') & (df_select['year']==2030),'emis_int_outp_1930']
    com_transp_emisint_red_2050 = df_select.loc[(df_select['sector']=='Commercial Transport') & (df_select['year']==2050),'emis_int_outp_3150']
    # Annual reductions in emission intensity: Agriculture & Forestry
    agrifor_emisint_red_2018 = df_select.loc[(df_select['sector']=='Agriculture & Forestry') & (df_select['year']==2018),'emis_int_outp_hist']
    agrifor_emisint_red_2030 = df_select.loc[(df_select['sector']=='Agriculture & Forestry') & (df_select['year']==2030),'emis_int_outp_1930']
    agrifor_emisint_red_2050 = df_select.loc[(df_select['sector']=='Agriculture & Forestry') & (df_select['year']==2050),'emis_int_outp_3150']
    # Annual reductions in emission intensity: Electricity generation
    electricity_emisint_red_2018 = df_select.loc[(df_select['sector']=='Electricity generation') & (df_select['year']==2018),'emis_int_outp_hist']
    electricity_emisint_red_2030 = df_select.loc[(df_select['sector']=='Electricity generation') & (df_select['year']==2030),'emis_int_outp_1930']
    electricity_emisint_red_2050 = df_select.loc[(df_select['sector']=='Electricity generation') & (df_select['year']==2050),'emis_int_outp_3150']

### ### Emission intensity changes total
    # Use net emisisons for this
    df_select_summ['total_emis_int'] = df_select_summ['net_emis'] / df_select_summ['ind_val_add_output']
    # For 2009-2018
    df_select_summ['total_emis_int_lag10'] = df_select_summ['total_emis_int'].shift(9)
    df_select_summ['total_emis_int_red_hist'] = np.power(df_select_summ['total_emis_int'] / df_select_summ['total_emis_int_lag10'], 0.1)
    df_select_summ['total_emis_int_red_hist'] = 100 * (df_select_summ['total_emis_int_red_hist'] - 1)
    df_select_summ['total_emis_int_red_hist'] = round(df_select_summ['total_emis_int_red_hist'], 1)
    df_select_summ['total_emis_int_red_hist'] = df_select_summ['total_emis_int_red_hist'].apply(str)
    df_select_summ['total_emis_int_red_hist'] = df_select_summ['total_emis_int_red_hist'] + '%'
    # For 2019-2030
    df_select_summ['total_emis_int_lag12'] = df_select_summ['total_emis_int'].shift(11)
    df_select_summ['total_emis_int_red_1930'] = np.power(df_select_summ['total_emis_int'] / df_select_summ['total_emis_int_lag12'], 1 / 12)
    df_select_summ['total_emis_int_red_1930'] = 100 * (df_select_summ['total_emis_int_red_1930'] - 1)
    df_select_summ['total_emis_int_red_1930'] = round(df_select_summ['total_emis_int_red_1930'], 1)
    df_select_summ['total_emis_int_red_1930'] = df_select_summ['total_emis_int_red_1930'].apply(str)
    df_select_summ['total_emis_int_red_1930'] = df_select_summ['total_emis_int_red_1930'] + '%'
    # For 2031-2050
    df_select_summ['total_emis_int_lag20'] = df_select_summ['total_emis_int'].shift(19)
    df_select_summ['total_emis_int_red_3150'] = np.power(df_select_summ['total_emis_int'] / df_select_summ['total_emis_int_lag20'], 1 / 20)
    df_select_summ['total_emis_int_red_3150'] = 100 * (df_select_summ['total_emis_int_red_3150'] - 1)
    df_select_summ['total_emis_int_red_3150'] = round(df_select_summ['total_emis_int_red_3150'], 1)
    df_select_summ['total_emis_int_red_3150'] = df_select_summ['total_emis_int_red_3150'].apply(str)
    df_select_summ['total_emis_int_red_3150'] = df_select_summ['total_emis_int_red_3150'] + '%'
    # Outputs
    total_emis_int_red_hist = df_select_summ.loc[df_select_summ['year'] == 2018, 'total_emis_int_red_hist']
    total_emis_int_red_1930 = df_select_summ.loc[df_select_summ['year'] == 2030, 'total_emis_int_red_1930']
    total_emis_int_red_3150 = df_select_summ.loc[df_select_summ['year'] == 2050, 'total_emis_int_red_3150']

### ### Define Per capita emission figure again, but with dynamic input
    # Per capita emissions
    df_select_summ['pcap_emissions'] = df_select_summ['net_emis'] / df_select_summ['population']
    # Roudn numbers
    df_select_summ['population'] = round(df_select_summ['population'], 2)
    df_select_summ['pcap_emissions'] = round(df_select_summ['pcap_emissions'], 2)
    # Make dictionary for dual y-axis figure
    year_new_dict = df_select_summ['year'].tolist()
    pop_dict = df_select_summ['population'].tolist()
    pcap_emis_dict = df_select_summ['pcap_emissions'].tolist()
    # redefine figure with dynamic input
    # Keep here because net emissions have not been calculated earlier
    fig_pop_per_capita = make_subplots(specs=[[{"secondary_y": True}]])
    # Add traces
    fig_pop_per_capita.add_scatter(x=year_dict, y=pcap_emis_dict, name="Per capita emissions", mode="lines", line=dict(width=2, color="black"), secondary_y=False)
    fig_pop_per_capita.add_scatter(x=year_new_dict, y=pop_dict, name="Population", mode="lines", line=dict(width=2, color="rgba(31, 119, 180, 1)"), secondary_y=True)
    fig_pop_per_capita.update_layout(template="plotly_white",
                                     legend_traceorder="reversed",
                                     title_text="Population and net per capita emissions",
                                     title_font_color="#1F77B4",
                                     title_font_size=18,
                                     title_font_family="Rockwell",
                                     title_x=0.02,
                                     margin=dict(t=40, r=0, b=0, l=65, pad=0),
                                     width=672, height=340)
    fig_pop_per_capita.update_xaxes(showline=True, linewidth=1, linecolor='black', gridcolor='rgba(149, 165, 166, 0.6)', mirror=True)
    fig_pop_per_capita.update_yaxes(showline=True, linewidth=1, linecolor='black', gridcolor='rgba(149, 165, 166, 0.6)', mirror=True)
    # Set y-axes titles
    fig_pop_per_capita.update_yaxes(title_text="Net per capita emissions (t CO<sub>2</sub>-eq/person)", secondary_y=False)
    fig_pop_per_capita.update_yaxes(title_text="Population (millions)", secondary_y=True)
    # Set y-axis range
    max_pcap_emis = max(pcap_emis_dict) * 1.1
    fig_pop_per_capita.update_layout(yaxis=dict(range=[0,max_pcap_emis]))
    
### ### Redefine Emission intensity index figure with dynamic input
    # Roudn numbers
    df_select_netpc['emis_int_index'] = round(df_select_netpc['emis_int_index'], 1)
    # Create lists
    year_new_dict = df_select_netpc['year'].tolist()
    emis_int_dict = df_select_netpc['emis_int_index'].tolist()
    # redefine figure with dynamic input
    # Keep here because net emissions have not been calculated earlier
    fig_emis_int_index = make_subplots(specs=[[{"secondary_y": False}]])
    # Add traces
    fig_emis_int_index.add_scatter(x=year_new_dict, y=emis_int_dict, name="Emission intensity index", mode="lines", line=dict(width=2, color="rgba(31, 119, 180, 1)"), secondary_y=False)
    fig_emis_int_index.update_layout(template="plotly_white",
                                     title_text="Emission intensity index",
                                     title_font_color="#1F77B4",
                                     title_font_size=18,
                                     title_font_family="Rockwell",
                                     title_x=0.02,
                                     margin=dict(t=40, r=0, b=0, l=65, pad=0),
                                     width=482, height=340)
    fig_emis_int_index.update_xaxes(showline=True, linewidth=1, linecolor='black', gridcolor='rgba(149, 165, 166, 0.6)', mirror=True)
    fig_emis_int_index.update_yaxes(showline=True, linewidth=1, linecolor='black', gridcolor='rgba(149, 165, 166, 0.6)', mirror=True)
    # Set y-axes titles
    fig_emis_int_index.update_yaxes(title_text="Emission intensity index (2010=100)", secondary_y=False)
    # Set y-axis range
    emis_int_dict = emis_int_dict[4:]
    max_emis_int = max(emis_int_dict) * 1.1
    fig_emis_int_index.update_layout(yaxis=dict(range=[0,max_emis_int]))
    


    return (fig_emissions_total, fig_added_value_total, fig_emis_int, fig_elec_gen_int, fig_pop_per_capita, fig_emis_int_index,
            services_emisred_2018, services_emisred_2030, services_emisred_2040, services_emisred_2050,
            mining_emisred_2018, mining_emisred_2030, mining_emisred_2040, mining_emisred_2050,
            manufacturing_emisred_2018, manufacturing_emisred_2030, manufacturing_emisred_2040, manufacturing_emisred_2050,
            gas_water_waste_emisred_2018, gas_water_waste_emisred_2030, gas_water_waste_emisred_2040, gas_water_waste_emisred_2050,
            construction_emisred_2018, construction_emisred_2030, construction_emisred_2040, construction_emisred_2050,
            com_transp_emisred_2018, com_transp_emisred_2030, com_transp_emisred_2040, com_transp_emisred_2050,
            agrifor_emisred_2018, agrifor_emisred_2030, agrifor_emisred_2040, agrifor_emisred_2050,
            residential_emisred_2018, residential_emisred_2030, residential_emisred_2040, residential_emisred_2050,
            electricity_emisred_2018, electricity_emisred_2030, electricity_emisred_2040, electricity_emisred_2050,
            services_emis_2018, mining_emis_2018, manufacturing_emis_2018, gas_water_waste_emis_2018,
            construction_emis_2018, com_transp_emis_2018, agrifor_emis_2018, residential_emis_2018, electricity_emis_2018,
            services_emis_2050, mining_emis_2050, manufacturing_emis_2050, gas_water_waste_emis_2050,
            construction_emis_2050, com_transp_emis_2050, agrifor_emis_2050, residential_emis_2050, electricity_emis_2050,
            total_emisred_Mt_hist, total_emisred_Mt_1930, total_emisred_Mt_3150,
            total_emisred_2018, total_emisred_2030, total_emisred_2040, total_emisred_2050,
            net_emisred_2018, net_emisred_2030, net_emisred_2040, net_emisred_2050,
            gross_emis_2018, gross_emis_2030, gross_emis_2040, gross_emis_2050, gross_emis_2018copy, gross_emis_2050copy,
            LULUCF_2018, LULUCF_2030, LULUCF_2040, LULUCF_2050,
            net_emis_2018, net_emis_2030, net_emis_2040, net_emis_2050,
            total_val_add_hist, total_val_add_1950,
            elec_carb_int_2018, elec_carb_int_2030, elec_carb_int_2040, elec_carb_int_2050,
            services_emisint_red_2018, services_emisint_red_2030, services_emisint_red_2050,
            mining_emisint_red_2018, mining_emisint_red_2030, mining_emisint_red_2050,
            manufacturing_emisint_red_2018, manufacturing_emisint_red_2030, manufacturing_emisint_red_2050,
            gas_water_waste_emisint_red_2018, gas_water_waste_emisint_red_2030, gas_water_waste_emisint_red_2050,
            construction_emisint_red_2018, construction_emisint_red_2030, construction_emisint_red_2050,
            com_transp_emisint_red_2018, com_transp_emisint_red_2030, com_transp_emisint_red_2050,
            agrifor_emisint_red_2018, agrifor_emisint_red_2030, agrifor_emisint_red_2050,
            electricity_emisint_red_2018, electricity_emisint_red_2030, electricity_emisint_red_2050,
            total_emis_int_red_hist, total_emis_int_red_1930, total_emis_int_red_3150)


if __name__ == '__main__':
    app.run_server(debug=False,dev_tools_ui=False,dev_tools_props_check=False)