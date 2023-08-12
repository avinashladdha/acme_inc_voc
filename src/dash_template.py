import dash
import dash_bootstrap_components as dbc
from dash import dcc,html
import ast
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date 
import base64
import numpy as np
from collections import Counter
from wordcloud import WordCloud, STOPWORDS
from io import BytesIO # for wordcloud 
##############################################          FUNCTIONS             ##################################################
def flatten_list(list_of_lists):
    return [item for sublist in list_of_lists for item in ast.literal_eval(sublist)]


def generate_table(dataframe, max_rows=100):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

def plot_wordcloud(list):
    d = Counter(list)
    wc = WordCloud(background_color='white', width=1080, height=360,max_words=30)
    
    wc.fit_words(d)
    return wc.to_image()

############################################# ############################################# ##########################################
## ingesting dataframe 

data = pd.read_csv('./data/df_raw.csv')
print(len(data))


# the style arguments for the sidebar.
SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '30%',
    'padding': '20px 10px',
    'background-color': '#f8f9fa',
    "overflow": "scroll"
}

# the style arguments for the main content page.
CONTENT_STYLE = {
    'margin-left': '35%',
    'margin-right': '5%',
    'padding': '20px 10p'
}

TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#191970'
}

CARD_TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#0074D9'
}

controls = dbc.FormGroup(
    [
        html.P('Date Range', style={
            'textAlign': 'center'
        }),
            dcc.DatePickerRange(
            id='my-date-picker-range',
            min_date_allowed=date(2015, 8, 5),
            max_date_allowed=date(2016, 9, 1),
            initial_visible_month=date(2015, 8, 16),
            end_date=date(2015, 9, 1), 
            start_date=date(2015, 8, 23),
            
            style = {
                        'font-size': '6px','display': 'inline-block', 'border-radius' : '2px', 
                        'border' : '1px solid #ccc', 'color': '#333', 
                        'border-spacing' : '0', 'border-collapse' :'separate',
                        'zIndex': 10
                        } 
             ),
        html.Div(id='output-container-date-picker-range')
        ,
        html.Br(),
        
        html.P('Star Rating', style={
            'textAlign': 'center'
        }),
        dcc.Dropdown(
            id='star_rating',
            options=[{
                'label': 'One',
                'value': '1'
            }, {
                'label': 'Two',
                'value': '2'
            },
                {
                    'label': 'Three',
                    'value': '3'
                },
            {
                    'label': 'Four',
                    'value': '4'
                },
            {
                    'label': 'Five',
                    'value': '5'
                }
            ],
            value="",  # default value
            multi=True
        ),
        html.Br(),
    


        html.P('Sentiment', style={
            'textAlign': 'center'
        }),
        dbc.Card([dbc.Checklist(
            id='sentiment_list',
            options=[
                {
                'label': 'Positive',
                'value': 'POSITIVE'
                },
                {
                    'label': 'Negative',
                    'value': 'NEGATIVE'
                },
                {
                    'label': 'Neutral',
                    'value': 'NEUTRAL'
                }
            ],
            value="",
            inline=True
        )]),


        html.Br(),



        html.P('Verified Purchase', style={
            'textAlign': 'center'
        }),
        dbc.Card([dbc.Checklist(
            id='verified_purchase',
            options=[
                {
                'label': 'Yes',
                'value': 'YES'
                },
                {
                    'label': 'No',
                    'value': 'NO'
                }
            ],
            value="",
            inline=True
        )]),


        html.Br(),

        html.P('Votes on Reviews', style={
            'textAlign': 'center'
        }),
        dcc.Input(id='cc_votes', value="", type='text'),
        html.Br(),



    html.P('Product Id', style={
            'textAlign': 'center'
        }),
        dcc.Dropdown(
            id='product_id',
            options=[{"label":str(i),"value":str(i)} for i in data['product_id'].unique()
            ],
            value='',  # default value
            multi=True
        ),
        html.Br(),



        dbc.Button(
            id='submit_button',
            n_clicks=0,
            children='Submit',
            color='primary',
            block=True
        ),
    ]
)

sidebar = html.Div(
    [
        html.H3('Filters', style=TEXT_STYLE),
        html.Hr(),
        controls
    ],
    style=SIDEBAR_STYLE,
)

content_first_row = dbc.Row([
    dbc.Col(
        dbc.Card(
            [

                dbc.CardBody(
                    [
                        html.H4(id='card_title_1', children=['Total reviews analyzed'], className='card-title',
                                style=CARD_TEXT_STYLE),
                        html.P(id='card_text_1', children='children', style=CARD_TEXT_STYLE),
                    ]
                )
            ]
        ),
        md=3
    ),
    dbc.Col(
        dbc.Card(
            [

                dbc.CardBody(
                    [
                        html.H4('Total Positive Reviews', className='card-title', style=CARD_TEXT_STYLE),
                        html.P(id='card_text_2', children='children', style=CARD_TEXT_STYLE),
                    ]
                ),
            ]

        ),
        md=3
    ),
    dbc.Col(
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H4('Total Negative Reviews', className='card-title', style=CARD_TEXT_STYLE),
                        html.P(id='card_text_3', children='children', style=CARD_TEXT_STYLE),
                    ]
                ),
            ]

        ),
        md=3
    ),
    dbc.Col(
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H4('Sentiment score', className='card-title', style=CARD_TEXT_STYLE),
                        html.P(id='card_text_4', children=' ', style=CARD_TEXT_STYLE),
                    ]
                ),
            ]
        ),
        md=3
    )
])

content_second_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='graph_1'), md=12
        ),
        # dbc.Col(
        #     dcc.Graph(id='graph_2'), md=4
        # ),
        # dbc.Col(
        #     dcc.Graph(id='graph_3'), md=4
        # )
    ]
)

content_third_row = dbc.Row(
    [
        dbc.Col(
            
            #dcc.Graph(id='graph_4', figure="fig"), #md=12,
            html.Img(id ="wordcloud_img")
        )
    ]
)

content_fourth_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='graph_5'), md=6
        ),
        dbc.Col(
            dcc.Graph(id='graph_6'), md=6
        )
    ]
)

content = html.Div(
    [
        html.H2('Vire Insights | VoC v1.0', style=TEXT_STYLE),
        
        html.H4('Overall summary for selected time window', style=TEXT_STYLE),
        html.Hr(),
        content_first_row,
        content_second_row,

        html.H4('Review profiling:', style=TEXT_STYLE),
        html.Hr(),
        content_third_row,
        content_fourth_row
    ],
    style=CONTENT_STYLE
)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([sidebar, content])





## Callback code -- Left to right , top down

## TOTAL REVIEWS
@app.callback(
    Output('card_text_1', 'children'),
   # Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date') ,
  #  [State('dropdown', 'value'), State('check_list', 'value'),
    #  ]
   )
#def update_card_text_1(n_clicks, dropdown_value, check_list_value, start_date, end_date):
def update_card_text_1(start_date, end_date):
    # print(n_clicks)
    # print(dropdown_value)
    # print(range_slider_value)
    # print(check_list_value)
    print(start_date)
    temp_df = data[(data['review_date']>start_date)&(data['review_date']<end_date)]
    #print(temp_df)
    # Sample data and figure
    return len(temp_df)



## POSITIVE REVIEWS
@app.callback(
    Output('card_text_2', 'children'),
   # Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date') ,
  #  [State('dropdown', 'value'), State('check_list', 'value'),
    #  ]
    )
#def update_card_text_1(n_clicks, dropdown_value, check_list_value, start_date, end_date):
def update_card_text_2(start_date, end_date):
    # print(n_clicks)
    # print(dropdown_value)
    # print(range_slider_value)
    # print(check_list_value)
    print(start_date)
    temp_df = data[(data['review_date']>start_date)&(data['review_date']<end_date)&(data['sentiment_tag']=="POSITIVE")]
    #print(temp_df)
    # Sample data and figure
    return len(temp_df)



## NEGATIVE REVIEWS
@app.callback(
    Output('card_text_3', 'children'),
   # Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date') ,
  #  [State('dropdown', 'value'), State('check_list', 'value'),
    #  ]
    )
#def update_card_text_1(n_clicks, dropdown_value, check_list_value, start_date, end_date):
def update_card_text_3(start_date, end_date):
    # print(n_clicks)
    # print(dropdown_value)
    # print(range_slider_value)
    # print(check_list_value)
    print(start_date)
    temp_df = data[(data['review_date']>start_date)&(data['review_date']<end_date)&(data['sentiment_tag']=="NEGATIVE")]
    #print(temp_df)
    # Sample data and figure
    return len(temp_df)



## SENTIMENT SCORE
@app.callback(
    Output('card_text_4', 'children'),
   # Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date') ,
  #  [State('dropdown', 'value'), State('check_list', 'value'),
    #  ]
    )
#def update_card_text_1(n_clicks, dropdown_value, check_list_value, start_date, end_date):
def update_card_text_4(start_date, end_date):
    # print(n_clicks)
    # print(dropdown_value)
    # print(range_slider_value)
    # print(check_list_value)
    print(start_date)
    len_neg = len(data[(data['review_date']>start_date)&(data['review_date']<end_date)&(data['sentiment_tag']=="NEGATIVE")])
    len_pos = len(data[(data['review_date']>start_date)&(data['review_date']<end_date)&(data['sentiment_tag']=="POSITIVE")])
    #print(temp_df)
    # Sample data and figure
    return round((100*(len_pos-len_neg)/(len_pos+len_neg)),1)





@app.callback(
    Output('graph_1', 'figure'),
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')]
    )
    # [State('dropdown', 'value'), State('range_slider', 'value'), State('check_list', 'value')
    #  ])
def update_graph_1(n_clicks,start_date, end_date):

    temp_df = data[(data['review_date']>start_date)&(data['review_date']<end_date)]

    grouped_df = temp_df.groupby(['review_date','sentiment_tag'], as_index = False)['review_id'].count()
    grouped_df = grouped_df.fillna(0)

    pivot_df = pd.pivot_table(grouped_df, values=['review_id'], index=['review_date'], columns=['sentiment_tag'],
                aggfunc='sum', fill_value=0, margins=False, dropna=False, margins_name='All', observed=False, sort=True)

    pivot_df.columns = [' '.join(col).strip() for col in pivot_df.columns.values]
    pivot_df = pivot_df.reset_index()
    pivot_df.columns = ['date','neg_cc','pos_cc']


    x = pivot_df['date']
    y1 = pivot_df['neg_cc']
    y2 = pivot_df['pos_cc']
    fig = px.line(x=x, y = [y1,y2])
    # Change title 
    fig.update_layout(title='Count of Reviews')
    # Change the x-axis name
    fig.update_xaxes(title='Date')
    # Change the y-axis name
    fig.update_yaxes(title='#Reviews')
    # Update Legend name and title 
    fig.update_layout(legend={"title":"Sentiment"})  
    series_names = ["Negative", "Positive"]

    for idx, name in enumerate(series_names):
        fig.data[idx].name = name
        fig.data[idx].hovertemplate = name
    return fig

## Wordcloud

# @app.callback(
#     #Output('graph_4', 'img'),
#     Output('wordcloud_img', 'src'),
#     [Input('submit_button', 'n_clicks'),
#     Input('my-date-picker-range', 'start_date'),
#     Input('my-date-picker-range', 'end_date')],
#     State('star_rating', 'value'), 
#     )

# def update_graph_4(n_clicks, start_date, end_date,star_rating):
#     print("*************")
#     print("Star rating :{}".format(star_rating))
#     star_rating_str = str(star_rating)[1:-1]
#     # if star_rating is not None:
#     #     temp_df = data[(data['review_date']>start_date)&(data['review_date']<end_date)]
#     # else :
#     #     temp_df = data[(data['review_date']>start_date)&(data['review_date']<end_date)&(data['star_rating'].isin(star_rating))]


#     temp_df = data.query('review_date > @start_date & review_date < @end_date')


#     print(len(temp_df))
# # Sample data and figure
#     img = BytesIO()
#     word_list = flatten_list(temp_df['tags'].to_list())
#     #print(word_list)
#     fig = plot_wordcloud(word_list)
#     fig.save(img, format="PNG")
#     return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())




@app.callback(
    #Output('graph_4', 'img'),
    Output('wordcloud_img', 'src'),
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')],
    [State('star_rating', 'value'), 
     State('sentiment_list', 'value'), 
     State('verified_purchase', 'value'), 
     State('cc_votes', 'value'), 
     State('product_id', 'value')
     
     ]
    )

def update_graph_4(n_clicks, start_date, end_date,star_rating, sentiment_list, verified_purchase, cc_votes, product_id):
    print("*************")
    print("Star rating :{}".format(star_rating))
    star_rating_str = str(star_rating)[1:-1]
    temp_df = data.query('review_date > @start_date & review_date < @end_date')
    filt_temp = [star_rating,sentiment_list, verified_purchase, cc_votes, product_id]
    print("Filt temp :{}".format(filt_temp))
    filt_temp_na = [i for i in filt_temp if len(i)>0]

    print(filt_temp_na)
    print(len(temp_df))
# Sample data and figure
    img = BytesIO()
    word_list = flatten_list(temp_df['tags'].to_list())
    #print(word_list)
    fig = plot_wordcloud(word_list)
    fig.save(img, format="PNG")
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())




#####################################################################################






@app.callback(
    Output('graph_2', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('dropdown', 'value'), State('check_list', 'value')

     ])
def update_graph_2(n_clicks, dropdown_value, range_slider_value, check_list_value):
    print(n_clicks)
    print(dropdown_value)
    print(range_slider_value)
    print(check_list_value)

    fig = {
        'data': [{
            'x': [1, 2, 3],
            'y': [3, 4, 5],
            'type': 'bar'
        }]
    }
    return fig


@app.callback(
    Output('graph_3', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('dropdown', 'value'), State('range_slider', 'value'), State('check_list', 'value'),

     ])
def update_graph_3(n_clicks, dropdown_value, range_slider_value, check_list_value, ):
    print(n_clicks)
    print(dropdown_value)
    print(range_slider_value)
    print(check_list_value)
 
    df = px.data.iris()
    fig = px.density_contour(df, x='sepal_width', y='sepal_length')
    return fig


@app.callback(
    Output('graph_4', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('dropdown', 'value'), State('range_slider', 'value'), State('check_list', 'value'),
     
     ])
def update_graph_4(n_clicks, dropdown_value, range_slider_value, check_list_value, ):
    print(n_clicks)
    print(dropdown_value)
    print(range_slider_value)
    print(check_list_value)
# Sample data and figure
    df = px.data.gapminder().query('year==2007')
    fig = px.scatter_geo(df, locations='iso_alpha', color='continent',
                         hover_name='country', size='pop', projection='natural earth')
    fig.update_layout({
        'height': 600
    })
    return fig


@app.callback(
    Output('graph_5', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('dropdown', 'value'), State('range_slider', 'value'), State('check_list', 'value'),
   
     ])
def update_graph_5(n_clicks, dropdown_value, range_slider_value, check_list_value):
    print(n_clicks)
    print(dropdown_value)
    print(range_slider_value)
    print(check_list_value)
    # Sample data and figure
    df = px.data.iris()
    fig = px.scatter(df, x='sepal_width', y='sepal_length')
    return fig


@app.callback(
    Output('graph_6', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('dropdown', 'value'), State('range_slider', 'value'), State('check_list', 'value'),
    
     ])
def update_graph_6(n_clicks, dropdown_value, range_slider_value, check_list_value):
    print(n_clicks)
    print(dropdown_value)
    print(range_slider_value)
    print(check_list_value)
  # Sample data and figure
    df = px.data.tips()
    fig = px.bar(df, x='total_bill', y='day', orientation='h')
    return fig







if __name__ == '__main__':
    app.run_server(port='8085')















# Extra code to be removed in cleaning 
# @app.callback(
#     Output('card_title_1', 'children'),
#     [Input('submit_button', 'n_clicks')],
#     [State('dropdown', 'value'), State('range_slider', 'value'), State('check_list', 'value'),

#      ])
# def update_card_title_1(n_clicks, dropdown_value, range_slider_value, check_list_value):
#     print(n_clicks)
#     print(dropdown_value)
#     print(range_slider_value)
#     print(check_list_value)
#  # Sample data and figure
#     return 'Card Tile 1 change by call back'



# @app.callback(
#     Output('graph_1', 'figure'),
#     [Input('submit_button', 'n_clicks'),
#      Input('my-date-picker-range', 'start_date'),
#     Input('my-date-picker-range', 'end_date')]

#     # [State('dropdown', 'value'), State('range_slider', 'value'), State('check_list', 'value')
#     #  ])
# def update_graph_1(n_clicks, dropdown_value, range_slider_value, check_list_value):
#     print(n_clicks)
#     print(dropdown_value)
#     print(range_slider_value)
#     print(check_list_value)

#     fig = {
#         'data': [{
#             'x': [1, 2, 3],
#             'y': [3, 4, 5]
#         }]
#     }
#     return fig



        # html.P('Check Box', style={
        #     'textAlign': 'center'
        # }),
        # dbc.Card([dbc.Checklist(
        #     id='check_list',
        #     options=[{
        #         'label': 'Value One',
        #         'value': 'value1'
        #     },
        #         {
        #             'label': 'Value Two',
        #             'value': 'value2'
        #         },
        #         {
        #             'label': 'Value Three',
        #             'value': 'value3'
        #         }
        #     ],
        #     value=['value1', 'value2'],
        #     inline=True
        # )]),
