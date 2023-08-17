import dash
import dash_bootstrap_components as dbc
from dash import dcc,html, dash_table
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

def top_keywords_df(list):
    list_updated = [word for word in list if word not in stop_words] 
    d = Counter(list_updated)
    keyword_df_temp = pd.DataFrame(d,index=[0]).T.reset_index()
    keyword_df_temp.columns = ['Keyword', "Count"]
    keyword_df_temp = keyword_df_temp.sort_values(["Count"], ascending = False)
    return keyword_df_temp

def plot_wordcloud(list):
    list_updated = [word for word in list if word not in stop_words] 
    d = Counter(list_updated)
    wc = WordCloud(stopwords = stop_words,background_color='white', width=700, height=500,max_words=30)
    
    wc.fit_words(d)
    return wc.to_image()


# Function to filter dataframe from list of chosen filters 


def update_dictionary(input_dict):
    for i in list(input_dict.keys()):
        if input_dict[i] == '' or input_dict[i] == 'None' or input_dict[i] == None or input_dict[i]==[]: ## Also check for [] to address empty lists 
            input_dict[i] = filt_values[i]
    return input_dict
#############################################               DATA           ################### ##########################################

## ingesting dataframe 

list_adhoc = ['stars','Stars','STARS', 'star']
stop_words = list(STOPWORDS) + list_adhoc
data = pd.read_csv('./data/df_raw.csv')
print(len(data))

convert_to_str = ['star_rating','total_votes']
data[convert_to_str] = data[convert_to_str].astype('str')

#making a keyword dataframe

keyword_df = top_keywords_df(flatten_list(data['tags'].to_list()))
print(keyword_df.head())


## data reuired for functions
filt_values = {'star_rating': ['1','2','3','4','5'], 'sentiment_tag': ['POSITIVE','NEGATIVE'],
             'verified_purchase': ['Y','N'],
               'total_votes': ['1','2','3','4','5'], 
               'product_id': list(data['product_id'].unique())}





# the style arguments for the sidebar.
SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '20%',
    'padding': '20px 10px',
    'background-color': '#f8f9fa',
    "overflow": "scroll"
}

# the style arguments for the main content page.
CONTENT_STYLE = {
    'margin-left': '25%',
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

CARD_TEXT_STYLE_SMALL = {
    'textAlign': 'center',
    'color': '#D3D3D3'
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
            value=['1','2','3','4','5'],  # default value
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
                'value': 'Y'
                },
                {
                    'label': 'No',
                    'value': 'N'
                }
            ],
            value="",
            inline=True
        )]),


        html.Br(),

        # html.P('Votes on Reviews', style={
        #     'textAlign': 'center'
        # }),
        # dcc.Input(id='cc_votes', value=list(data['total_votes'].unique())[0:3], type='text'),
        # html.Br(),

        html.P('Votes on Reviews', style={
            'textAlign': 'center'
        }),
        dcc.Dropdown(
            id='cc_votes',
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
            value=['1','2','3','4','5'],  # default value
            multi=True
        ),
        html.Br(),

        

    html.P('Product Id', style=
           {'textAlign': 'center',
            }),
        dcc.Dropdown(
            id='product_id',
            options=[{"label":str(i),"value":str(i)} for i in data['product_id'].unique()
            ],
            value=list(data['product_id'].unique())[0:6],  # default value
            multi=True,
            style={
                'maxHeight' :'200px',
                #'overflow-y':'auto'

            }
        ),
        html.Br(),

        dbc.Button(
            id='clear_button',
            n_clicks=0,
            children='Remove All Filters',
            color='primary',
            block=True
        ),

        dbc.Button(
            id='submit_button',
            n_clicks=0,
            children='Apply Filters',
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
                        html.H6('Percentage of positive reviews across the feedback.'),
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
            dcc.Graph(id='graph_1'), md=8
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
            html.Img(id ="wordcloud_img") , md = 8
        ),
        # dbc.Col(
        #     dbc.Card(

        #             dbc.CardBody(
        #                 [
        #                     html.H4(id='card_title_filter', children=['Reviews considered for graph'], className='card-title',
        #                             style=CARD_TEXT_STYLE),
        #                     html.P(id='card_text_filter', children='children', style=CARD_TEXT_STYLE_SMALL),
        #                 ]
        #             )
        
        #     ),md = 3
            
        # ),

         dbc.Col(
            dash_table.DataTable(
            id='table_kw',
            columns=[{"name": i, "id": i} for i in keyword_df.columns],
            #data=keyword_df.head(10).to_dict('records'),
        ), md=3
        )


    ]
)

content_fourth_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='graph_5'),md=5
        ),
        dbc.Col(
            dcc.Graph(id='graph_6'),md=5
        ),
    ]
)

content = html.Div(
    [
        html.H2('Vire Insights | VoC v1.0', style=TEXT_STYLE),
        html.H4('Overall summary for selected time window', style=TEXT_STYLE),
        html.Hr(),
        content_first_row,
        html.Hr(),
        content_second_row,
        html.H3('Review profiling', style=TEXT_STYLE),
        html.Div(    
            [html.Label('Count of reviews filtered for analysis:'),html.P(html.Div(id='count_header'))]),
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
    [Output('card_text_1', 'children'),
    Output('count_header','children')],
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
def update_card_text_1(n_clicks, start_date, end_date,star_rating, sentiment_list, verified_purchase,cc_votes, product_id):

    temp_df = data.query('review_date > @start_date & review_date < @end_date')

    print("************************************")
    filt_dict = {'star_rating':star_rating,
                 'sentiment_tag': sentiment_list, 
                  'verified_purchase':verified_purchase,
                 'total_votes' : cc_votes, 
                 'product_id' : product_id}
    
    filt_dict_updated = update_dictionary(filt_dict)


    for key, val in filt_dict_updated.items():
        #print("Filtering {}".format(key))
        temp_df = temp_df[temp_df[key].isin(val)]
#        print("Len of dataframe = {}".format(len(temp_df)))

    return len(temp_df),len(temp_df)


## POSITIVE REVIEWS
@app.callback(
    Output('card_text_2', 'children'),
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
def update_card_text_2(n_clicks, start_date, end_date,star_rating, sentiment_list, verified_purchase,cc_votes, product_id):
    temp_df = data.query('review_date > @start_date & review_date < @end_date')

    print("************************************")
    filt_dict = {'star_rating':star_rating,
                 'sentiment_tag': sentiment_list, 
                  'verified_purchase':verified_purchase,
                 'total_votes' : cc_votes, 
                 'product_id' : product_id}
    
    filt_dict_updated = update_dictionary(filt_dict)


    for key, val in filt_dict_updated.items():
        #print("Filtering {}".format(key))
        temp_df = temp_df[temp_df[key].isin(val)]

    temp_df = temp_df[(temp_df['review_date']>start_date)&(temp_df['review_date']<end_date)&(temp_df['sentiment_tag']=="POSITIVE")]
    return len(temp_df)


## NEGATIVE REVIEWS
@app.callback(
    Output('card_text_3', 'children'),
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')],
    [State('star_rating', 'value'), 
     State('sentiment_list', 'value'), 
     State('verified_purchase', 'value'), 
     State('cc_votes', 'value'), 
     State('product_id', 'value')]
    )
    #def update_card_text_1(n_clicks, dropdown_value, check_list_value, start_date, end_date):
def update_card_text_3(n_clicks, start_date, end_date,star_rating, sentiment_list, verified_purchase,cc_votes, product_id):
    temp_df = data.query('review_date > @start_date & review_date < @end_date')

    print("************************************")
    filt_dict = {'star_rating':star_rating,
                 'sentiment_tag': sentiment_list, 
                  'verified_purchase':verified_purchase,
                 'total_votes' : cc_votes, 
                 'product_id' : product_id}
    
    filt_dict_updated = update_dictionary(filt_dict)


    for key, val in filt_dict_updated.items():
        #print("Filtering {}".format(key))
        temp_df = temp_df[temp_df[key].isin(val)]
    temp_df = temp_df[(temp_df['review_date']>start_date)&(temp_df['review_date']<end_date)&(temp_df['sentiment_tag']=="NEGATIVE")]

    return len(temp_df)



## SENTIMENT SCORE
@app.callback(
    Output('card_text_4', 'children'),
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')],
    [State('star_rating', 'value'), 
     State('sentiment_list', 'value'), 
     State('verified_purchase', 'value'), 
     State('cc_votes', 'value'), 
     State('product_id', 'value')]
    )
    #def update_card_text_1(n_clicks, dropdown_value, check_list_value, start_date, end_date):
def update_card_text_4(n_clicks, start_date, end_date,star_rating, sentiment_list, verified_purchase,cc_votes, product_id):
    temp_df = data.query('review_date > @start_date & review_date < @end_date')

    print("************************************")
    filt_dict = {'star_rating':star_rating,
                 'sentiment_tag': sentiment_list, 
                  'verified_purchase':verified_purchase,
                 'total_votes' : cc_votes, 
                 'product_id' : product_id}
    
    filt_dict_updated = update_dictionary(filt_dict)


    for key, val in filt_dict_updated.items():
        #print("Filtering {}".format(key))
        temp_df = temp_df[temp_df[key].isin(val)]
    temp_df = data[(data['review_date']>start_date)&(data['review_date']<end_date)&(data['sentiment_tag']=="NEGATIVE")]

    len_neg = len(temp_df[(temp_df['review_date']>start_date)&(temp_df['review_date']<end_date)&(temp_df['sentiment_tag']=="NEGATIVE")])
    len_pos = len(temp_df[(temp_df['review_date']>start_date)&(temp_df['review_date']<end_date)&(temp_df['sentiment_tag']=="POSITIVE")])
    #print(temp_df)
    # Sample data and figure
    return round((100*(len_pos)/(len_pos+len_neg)),1)


## LINE CHART 
@app.callback(
    Output('graph_1', 'figure'),
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')],
    [State('star_rating', 'value'), 
     State('sentiment_list', 'value'), 
     State('verified_purchase', 'value'), 
     State('cc_votes', 'value'), 
     State('product_id', 'value')]
    )

def update_graph_1(n_clicks, start_date, end_date,star_rating, sentiment_list, verified_purchase,cc_votes, product_id):

    temp_df = data.query('review_date > @start_date & review_date < @end_date')

    print("************************************")
    filt_dict = {'star_rating':star_rating,
                 'sentiment_tag': sentiment_list, 
                  'verified_purchase':verified_purchase,
                 'total_votes' : cc_votes, 
                 'product_id' : product_id}
    
    filt_dict_updated = update_dictionary(filt_dict)


    for key, val in filt_dict_updated.items():
        #print("Filtering {}".format(key))
        temp_df = temp_df[temp_df[key].isin(val)]

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
    fig.update_layout(title='Trendline of feedback sentiment')
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


## WORDCLOUD 
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
def update_graph_4(n_clicks, start_date, end_date,star_rating, sentiment_list, verified_purchase,cc_votes, product_id):
    print("*************")

    temp_df = data.query('review_date > @start_date & review_date < @end_date')
    print("************************************")

    filt_dict = {'star_rating':star_rating,
                 'sentiment_tag': sentiment_list, 
                  'verified_purchase':verified_purchase,
                 'total_votes' : cc_votes, 
                 'product_id' : product_id}
    
    filt_dict_updated = update_dictionary(filt_dict)


    #print("Filtered dictionary :{}".format(filt_dict_updated))

    for key, val in filt_dict_updated.items():
        print("Filtering {}".format(key))
        temp_df = temp_df[temp_df[key].isin(val)]
        print("Len of dataframe = {}".format(len(temp_df)))
    if len(temp_df) >0:

    # Sample data and figure
        img = BytesIO()
        word_list = flatten_list(temp_df['tags'].to_list())
        #print(word_list)
        fig = plot_wordcloud(word_list)
        fig.save(img, format="PNG")

        return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())
    else :
        return str({"update"})

#####################################################################################

## KEYWORD TABLE
@app.callback(
    Output('table_kw', 'data'),
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
def update_keyword_table(n_clicks, start_date, end_date,star_rating, sentiment_list, verified_purchase,cc_votes, product_id):


    temp_df = data.query('review_date > @start_date & review_date < @end_date')
    print("************************************")

    filt_dict = {'star_rating':star_rating,
                 'sentiment_tag': sentiment_list, 
                  'verified_purchase':verified_purchase,
                 'total_votes' : cc_votes, 
                 'product_id' : product_id}
    
    filt_dict_updated = update_dictionary(filt_dict)
    print("Filtered dictionary :{}".format(filt_dict_updated))

    for key, val in filt_dict_updated.items():
        print("Filtering {}".format(key))
        temp_df = temp_df[temp_df[key].isin(val)]
        print("Len of dataframe = {}".format(len(temp_df)))
        print("Top KW dataframe...")
        print(top_keywords_df(flatten_list(temp_df['tags'].to_list())))

    if len(temp_df) >0:
        keyword_df = top_keywords_df(flatten_list(temp_df['tags'].to_list()))
        print(keyword_df)
        return keyword_df.head(10).to_dict('rows')
    
    else :
        return "Insufficient data"

## HORIZONTAL BAR CHART
@app.callback(
    #Output('graph_4', 'img'),
    Output('graph_5', 'figure'),
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
def update_graph_5(n_clicks, start_date, end_date,star_rating, sentiment_list, verified_purchase,cc_votes, product_id):
    print("*************")
    print("Star rating :{}".format(star_rating))
    star_rating_str = str(star_rating)[1:-1]
    temp_df = data.query('review_date > @start_date & review_date < @end_date')
    print("************************************")
    filt_dict = {'star_rating':star_rating,
                 'sentiment_tag': sentiment_list, 
                  'verified_purchase':verified_purchase,
                 'total_votes' : cc_votes, 
                 'product_id' : product_id}
    
    filt_dict_updated = update_dictionary(filt_dict)


    print("Filtered dictionary :{}".format(filt_dict_updated))

    for key, val in filt_dict_updated.items():
        print("Filtering {}".format(key))
        temp_df = temp_df[temp_df[key].isin(val)]
        print("Len of dataframe = {}".format(len(temp_df)))

    grouped_df = temp_df.groupby(['star_rating'], as_index= False)['review_id'].count()

    if len(temp_df) >0:
        fig = go.Figure([go.Bar(x = grouped_df['review_id'], y = grouped_df['star_rating'], marker_color = '#FA8072',
                             orientation = 'h',
                             textposition = 'outside'
                             ),
                 ])
        

        fig.update_xaxes(showline=True,
                linewidth=1,
                linecolor='grey',
                mirror=True)

        fig.update_yaxes(showline=True,
                linewidth=1,
                linecolor='grey',
                mirror=True)

        return fig
    else :
        return str({"update"})

#####################################################################################


 ## PIE CHART       
@app.callback(
    #Output('graph_4', 'img'),
    Output('graph_6', 'figure'),
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
def update_graph_6(n_clicks, start_date, end_date,star_rating, sentiment_list, verified_purchase,cc_votes, product_id):
    print("*************")
    print("Star rating :{}".format(star_rating))
    star_rating_str = str(star_rating)[1:-1]
    temp_df = data.query('review_date > @start_date & review_date < @end_date')


    print("************************************")

    filt_dict = {'star_rating':star_rating,
                 'sentiment_tag': sentiment_list, 
                  'verified_purchase':verified_purchase,
                 'total_votes' : cc_votes, 
                 'product_id' : product_id}
    
    filt_dict_updated = update_dictionary(filt_dict)


    print("Filtered dictionary :{}".format(filt_dict_updated))

    for key, val in filt_dict_updated.items():
        print("Filtering {}".format(key))
        temp_df = temp_df[temp_df[key].isin(val)]
        print("Len of dataframe = {}".format(len(temp_df)))

    grouped_df = temp_df.groupby(['sentiment_tag'], as_index= False)['review_id'].count()

    if len(temp_df) >0:
        fig =  px.pie(
          grouped_df,
            values='review_id',
            names='sentiment_tag',
            hole=.3,
            )
        return fig
    else :
        return str({"update"})

#####################################################################################       



#Update dropDown1 options
@app.callback([
        Output('my-date-picker-range', 'start_date'),
        Output('my-date-picker-range', 'end_date'),
        Output('star_rating', 'value'), 
        Output('sentiment_list', 'value'), 
        Output('verified_purchase', 'value'), 
        Output('cc_votes', 'value'), 
        Output('product_id', 'value')],
        [Input('clear_button', 'n_clicks')],
        )

def clearDropDown1(n_clicks):
    if n_clicks != 0: #Don't clear options when loading page for the first time
        return ['2015-07-01','2015-09-15',['1','2','3','4','5'],['POSITIVE','NEGATIVE'],
             ['Y','N'],
             ['1','2','3','4','5'], 
             list(data['product_id'].unique())
               ] #Return an empty list of options










if __name__ == '__main__':
    app.run_server(port='8085')




