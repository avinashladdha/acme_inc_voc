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
from datetime import datetime, timedelta



import logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)


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
    keyword_df_temp.columns = ['Keyword', "Frequency"]
    keyword_df_temp = keyword_df_temp.sort_values(["Frequency"], ascending = False)

    return keyword_df_temp

def plot_wordcloud(list):
    list_updated = [word for word in list if word not in stop_words]
    d = Counter(list_updated)
    wc = WordCloud(stopwords = stop_words,background_color='white', width=550, height=400,max_words=30)
    
    wc.fit_words(d)
    return wc.to_image()


# Function to filter dataframe from list of chosen filters 


def update_dictionary(input_dict):
    for i in list(input_dict.keys()):
        if input_dict[i] == '' or input_dict[i] == 'None' or input_dict[i] == None or input_dict[i]==[]: ## Also check for [] to address empty lists 
            input_dict[i] = filt_values[i]
    return input_dict
#############################################               DATA           ###################

## ingesting dataframe 

list_adhoc = ['stars','Stars','STARS', 'star','don','nan','wakefit']
stop_words = list(STOPWORDS) + list_adhoc
data = pd.read_csv('./data/df_raw.csv')
print(len(data))
print(data.review_date.min())
print(data.review_date.max())
data = data.rename(columns={data.columns[0]: 'review_id'})
data['product_parent'] = data['product_parent'].str.lower()
data['product_id'] = data['product_id'].str.lower()
data['platform'] = data['platform'].str.lower()
data = data[data['Week']!='c']

## Add first date of week 
data['review_date'] = pd.to_datetime(data['review_date'])
data['week_start'] = data['review_date'].apply( lambda x: x - timedelta(days=x.weekday()))

# Product Type = Product parent
# Sub Product Type = Prouct id

# building rating_df prior to gvoid str/int/flot conversion issue 
## Building a top_product sentiment table 
rating_df = data.groupby(['product_id','star_rating'], as_index = False)['review_id'].count()

rating_df = rating_df[rating_df['review_id']>10]
rating_df['star_rating'] =rating_df['star_rating'].astype(float)
rating_df['review_id'] =rating_df['review_id'].astype(float)
rating_df['rating_mult'] = rating_df['star_rating']*rating_df['review_id']

#rating_df_gpd = rating_df.groupby(['product_id'], as_index= False).apply({lambda x: x['rating_mult'].sum()/x['review_id'].sum()})


rating_df_gpd = rating_df.groupby(['product_id'], as_index= False).agg({'rating_mult':'sum','review_id':'sum'})

rating_df_gpd['weighted_rating'] = round(rating_df_gpd['rating_mult']/rating_df_gpd['review_id'],2)
rating_df_gpd = rating_df_gpd.drop(['rating_mult'], axis= 1)
rating_df_gpd.columns = ['Sub Product Type','Review Count','Product Rating']
rating_df_gpd['Product Rating'] = rating_df_gpd['Product Rating'].apply(lambda x : round(x,2))
rating_df_gpd = rating_df_gpd.sort_values(['Product Rating'], ascending = True)
rating_df_gpd = rating_df_gpd[rating_df_gpd['Sub Product Type']!='-']





# calculating date wise weighted rating of the products 

## Building a top_product sentiment table 
product_rating_df = data.groupby(['week_start','product_parent','star_rating'], as_index = False)['review_id'].count()


product_rating_df['star_rating'] =product_rating_df['star_rating'].astype(float)
product_rating_df['review_id'] =product_rating_df['review_id'].astype(float)
product_rating_df['rating_mult'] = product_rating_df['star_rating']*product_rating_df['review_id']


product_rating_df_gpd = product_rating_df.groupby(['product_parent','week_start'], as_index= False).apply(lambda x: x['rating_mult'].sum()/x['review_id'].sum())
product_rating_df_gpd.columns = ['Product Parent','week_start','Weighted Rating']
product_rating_df_gpd['Weighted Rating'] = product_rating_df_gpd['Weighted Rating'].apply(lambda x : round(x,2))
product_rating_df_gpd = product_rating_df_gpd.sort_values(['Weighted Rating'], ascending = False)

##### making static table for top 
product_rating_df_gpd_static = product_rating_df.groupby(['product_parent'], as_index= False).agg({'rating_mult':'sum','review_id':'sum'})
product_rating_df_gpd_static = product_rating_df_gpd_static[product_rating_df_gpd_static['review_id']>10]
product_rating_df_gpd_static['weighted_rating'] = round(product_rating_df_gpd_static['rating_mult']/product_rating_df_gpd_static['review_id'],2)
product_rating_df_gpd_static = product_rating_df_gpd_static.drop(['rating_mult'], axis= 1)
product_rating_df_gpd_static.columns = ['Product Type','Review Count','Product Rating']
product_rating_df_gpd_static['Product Rating'] = product_rating_df_gpd_static['Product Rating'].apply(lambda x : round(x,2))
product_rating_df_gpd_static = product_rating_df_gpd_static.sort_values(['Product Rating'], ascending = True)
# making change in data df 
#data['review_date'] = pd.to_datetime(data['review_date'])
#data['sentiment_tag'] = data['sentiment_tag'].fillna('NA')
data['star_rating'] = data['star_rating'].apply({lambda x : x.astype('str')})
data['star_rating'] = data['star_rating'].replace(to_replace=["1.0","2.0","3.0"],
           value=["1","2","3"])
## remove where sentiment cant be ascertained 


data['star_rating'] = data['star_rating'].fillna('nan')
#data = data[~data['star_rating'].isna()]
data = data[data['star_rating']!="4"]




#making a keyword dataframe
keyword_df = top_keywords_df(flatten_list(data['tags'].to_list()))



## data reuired for functions
filt_values = {'star_rating': ['1','2','3'], #'sentiment_tag': ['POSITIVE','NEGATIVE'],
             'verified_purchase': ['Y','N'],
               'product_id': list(data['product_id'].unique()),
                'product_parent': list(data['product_parent'].unique()),
               'platform': ['amazon','flipkart'],
              }

review_cols = ['product_parent','product_id','star_rating','review_date','review_body']

# the style arguments for the sidebar.
SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '22%',
    'padding': '20px 10px',
    'background-color': '#f8f9fa',
    "overflow": "scroll"
}

# the style arguments for the main content page.
CONTENT_STYLE = {
    'margin-left': '27%',
    'margin-right': '5%',
    'padding': '20px 10p'
}

TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#191970'
}

CARD_TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#0074D9',
    'font-size': '17px'
}

CARD_TEXT_STYLE_SMALL = {
    'textAlign': 'center',
    'color': '#D3D3D3'
}

controls = dbc.FormGroup(
    [
        html.P('Date Range', style={
            'textAlign': 'left',"width": "100%"
            }),
                html.Div(dcc.DatePickerRange(
                id='my-date-picker-range',
                display_format = 'DD-MM-YYYY',
                min_date_allowed=date(2022, 1, 5),
                max_date_allowed=date(2023, 10, 31),
                initial_visible_month=date(2022,11, 1),
                end_date=date(2023, 9, 30), 
                start_date=date(2022, 11, 1),

                style = {
                            'font-size': '5px','display': 'inline-block',# 'border-radius' : '2px', 
                            #'border' : '1px solid #ccc', 'color': '#333', 
                            'border-spacing' : '5', 'border-collapse' :'separate',
                            'zIndex': 10 ,  "width": "100%" ,
                            # 'padding-left': '1px',
                            # 'padding-right': '1px' 
                            } 
                         ),
                         style={
                'textAlign': 'center',"width": "100%"
                                }
                        ),
            html.Div(id='output-container-date-picker-range'),
            html.P('Reviews time duration :  November 2022 - September 2023', style={
                'textAlign': 'center',"width": "100%", 'font-size': '12px'
            })
        ,
        html.Br(),
        
        
        html.P('Platform', style=
               {'textAlign': 'left',
                }),
            html.Div([dcc.Dropdown(
                id='platform',
                options=[{"label":str(i),"value":str(i)} for i in data['platform'].unique()],
                value=list(data['platform'].unique())[0:10],  # default value
                multi=True,
                style={
                    'maxHeight' :'400px',
                    'minHeight' :'50px',

                }
            )]),

        
        html.P('Star Rating', style={
                'textAlign': 'left'
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
                # {
                #         'label': 'Four',
                #         'value': '4'
                #     },
                # {
                #         'label': 'Five',
                #         'value': '5'
                #     }
                ],
                value=['1','2','3'],  # default value
                multi=True
            ),
        html.Br(),
    

        html.P('Verified Purchase', style={
            'textAlign': 'left'
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
                value=["Y","N"],
                inline=True
            )]),

        html.Br(),


    html.P('Product Type', style=
           {'textAlign': 'left',
            }),
        html.Div([dcc.Dropdown(
            id='product_parent',
            options=[{"label":str(i),"value":str(i)} for i in data['product_parent'].unique()
            ],
            value=list(data['product_parent'].unique()),  # default value
            multi=True,
            style={
                'maxHeight' :'400px',
                'minHeight' :'50px',
                # 'height' :'200px',
                # 'overflow-y':'auto'

            }
        )]),
        
        

    html.P('Sub Product Type', style=
           {'textAlign': 'left',
            }),
        html.Div([dcc.Dropdown(
            id='product_id',
            options=[{"label":str(i),"value":str(i)} for i in data['product_id'].unique()
            ],
            value=list(data['product_id'].unique()),  # default value
            multi=True,
            style={
               # 'maxHeight' :'500px',
                'minHeight' :'50px',
                'height' :'150px',
                'overflow-y':'scroll'

            }
        )]),
        
        

        html.Br(),

        dbc.Button(
            id='clear_button',
            n_clicks=0,
            children='Remove All Filters',
            color='secondary',
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


content_summary_row = dbc.Row([
    dbc.Col([
       html.P(["""OVERALL SUMMARY:\n\n""",html.Br(),"""The reviews highlight multiple issues with Wakefit products including poor quality, flawed design, and subpar customer service. Customers reported problems with mattresses being too soft, causing back pain, and not living up to the 'orthopedic' label. The delivery and assembly process was criticized for being inconvenient and damaging to the products. Some customers also reported receiving defective or damaged items, including beds with uneven legs, wardrobes with cracks, and sofas that arrived dirty and wet. Customer service was described as unresponsive and unhelpful in resolving these issues. The company's return policy was also criticized for being inconsistent across different platforms. Despite some positive comments about affordability and aesthetics, the overall sentiment was of disappointment and frustration."""],
                  style={"border":"2px black solid",
                           "width" : "100%",
                            "height" :'100%',
                            "padding-top": "40px",
                            'font-size': '14px'
                           }) 
              ] 
            ),
                                ]
                                ) 



table_header = [
    html.Thead(html.Tr([html.Th("Product Type"), html.Th("Likes"),html.Th("Dislikes")]))
                ]

row1 = html.Tr([html.Td("mattress"), 

    html.Td(["""1. Affordable: Customers appreciated the reasonable pricing of the product.""",html.Br(),
    """2. Comfort: Some customers found the mattress comfortable for their sleep.""",html.Br(),
    """3. Quality: The product was appreciated for its good quality and accurate size."""]),

    html.Td(["""1. Quality and Comfort: Many customers complained about the mattress being too soft, leading to back pain and discomfort. They also mentioned that the mattress did not provide the orthopedic support as advertised.""", html.Br(),

    """2. False Advertising and Reviews: Customers felt deceived by the positive reviews and felt that the brand was manipulating reviews. They also mentioned false promises made by the customer support regarding the adjustment period and return policy.""", html.Br(),

    """3. Poor Customer Service: Customers were unhappy with the customer service provided by Wakefit. They mentioned issues with the return and replacement process, and felt that the brand did not stand behind their product."""])
           ])

row2 = html.Tr([html.Td("ew furniture"), 

        html.Td(["""
        1. Timely delivery and efficient assembly: Customers appreciated the prompt delivery and quick assembly of the products.""", html.Br(),

        """2. Quality and design: Many customers praised the quality and design of the products, mentioning that they were sturdy and aesthetically pleasing.""", html.Br(),

        """3. Ample storage space: The products were commended for providing ample storage space, which customers found useful.
        """]),

        html.Td(["""
        1. Poor installation and fitting: Customers complained about the poor installation and fitting of the products, particularly the beds. They mentioned gaps between the bed's structure and the floor, which led to dust accumulation. """, html.Br(),

        """2. Defective pieces and poor customer service: Some customers received defective pieces and had a difficult time returning the product or getting it replaced. They also complained about the poor customer service from Wakefit, with slow responses and lack of assistance in resolving their issues..""", html.Br(),

        """3. Quality and durability issues: Customers raised concerns about the quality and durability of the products. They mentioned issues like the chair's back snapping unexpectedly, the bed frame being made of thin plywood, and the wardrobe missing a locking slot. They also mentioned that the products were not as sturdy as they expected.
        """]), 
        ])

row3 = html.Tr([html.Td("accessories"), 

        html.Td(["""1. The products are initially comfortable and well-designed, providing a positive first impression.""", html.Br(),

        """2. The products are easy to use and set up, with items like pillows growing in size once removed from the packaging.""",
        html.Br(),    
        """3. The products initially provide good support and cushioning, particularly in the case of the pillows."""])
                
                ,
        html.Td(["""1. Quality and Durability: Many customers complained about the poor quality and durability of the products. They mentioned that the products, such as pillows and bean bags, lost their shape and comfort after a few weeks of use. Some also mentioned that the products tore apart easily, indicating poor material quality. """, html.Br(),

        """2. Misleading Product Information: Customers felt misled by the product information provided. For example, some customers who purchased bean bags complained that the size of the product was smaller than what was advertised. Others mentioned that the product did not come with the promised additional items, such as extra synthetic fibre for pillows or extra beans for bean bags.""",
        html.Br(),    
        """3. Customer Service: There were complaints about poor customer service, with customers mentioning that they were asked to delete negative reviews in exchange for additional product components that were never delivered. Others mentioned that their issues were not addressed satisfactorily, and they felt that the company was not committed to resolving their concerns."""])

        ])

row4 = html.Tr([html.Td("sofa"), 

    html.Td(["""--"""]),

    html.Td(["""
    1. Poor Quality: Customers complained about the poor quality of the products, including uneven ottoman tops, loose legs, and fabric threads coming out from the sofa stitches. Some customers also mentioned that the products were not durable and started showing defects within a few months. """, html.Br(),

    """2. Inadequate Customer Support: Customers were not satisfied with the customer support provided by the company. They reported unprofessional behavior, lack of follow-up on complaints, and inadequate repairs. Some customers also mentioned that the company did not honor the warranty of the products.""", html.Br(),

    """3. Delivery Issues: Customers faced issues with the delivery of the products. Some reported that the products were delivered in a poor condition, covered in dirt and grime. Others mentioned that the delivery was delayed, and the delivery personnel behaved rudely."""]), 

               
               ])

row5 = html.Tr([html.Td("hw furniture"), 


    html.Td(["""
    1. Quality of wood: Some customers were pleased with the quality of the wood used in the product.""", html.Br(),

    """2. Product design: The design of the product was appreciated by some customers who found it aesthetically pleasing.""", html.Br(),

    """3. Customer service: Despite some negative experiences, there were customers who appreciated the promptness and courtesy of the customer service team.
    """]),

    html.Td(["""
    1. Poor Quality and Durability: Many customers complained about the poor quality of the products, including the use of low-quality materials, poor finishing, and products breaking or getting damaged within a short period of use. """, html.Br(),

    """2. Delivery and Installation Issues: Customers faced issues with delayed deliveries, multiple delivery attempts, and poor installation services. Some customers also mentioned that the installation process was complicated and not user-friendly.""", html.Br(),

    """3. Poor Customer Service: Customers were dissatisfied with the customer service provided by Wakefit. Complaints included unresponsiveness, lack of assistance in resolving product issues, and difficulties in getting refunds or replacements.
    """]), 
               
               
               
               ])


table_body = [html.Tbody([row1, row2, row3, row4,row5])]
llm_summary_table = dbc.Table(table_header + table_body, bordered=True,style = {
                     'fontFamily': 'Arial',
                      'fontSize': '12px'
                  })



content_summary_table = dbc.Row(
    [       
        
        dbc.Col(
            dash_table.DataTable(
            id='table_top_products_parent',
            columns=[{"name": i, "id": i} for i in product_rating_df_gpd_static.columns],
            style_cell={'textAlign': 'center'},                
                style_cell_conditional=[
                        {
            'if': {'column_id': 'Product Type'},
                    'textAlign': 'left'
                        }
                        ],
            data = product_rating_df_gpd_static.tail(5).to_dict('records')
        ), md=6
        ),
        
        dbc.Col(
            dash_table.DataTable(
            id='table_top_products',
            columns=[{"name": i, "id": i} for i in rating_df_gpd.columns],
            style_cell={'textAlign': 'center'},
            style_cell_conditional=[
                                    {'if': {'column_id': 'Sub Product Type'},
                                    'textAlign': 'left'}
                                    ],

            data = rating_df_gpd.tail(5).to_dict('records')
        ), md=6 , style = {'width' : '5'}
        ),
        
        
        

        
        
    ]
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
                    ],style={"height": "10rem"}
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
                        html.H4('1 Star Reviews (%)', className='card-title', style=CARD_TEXT_STYLE),
                    
                              # style={
                              #   'textAlign': 'center',"width": "100%", 'font-size': '10px'
                              #       }
                              # ),
                        html.P(id='card_text_2', children='children', style=CARD_TEXT_STYLE)
                        # html.P(id='card_text_2_sub', children='children', style={
                        #         'textAlign': 'center',"width": "100%", 'font-size': '9px'
                        #             }),
                    ]
                    ,style={"height": "10rem"}
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
                        html.H4('2 Star Reviews (%)', className='card-title', style=CARD_TEXT_STYLE),
                      
                              # style={
                              #   'textAlign': 'center',"width": "100%", 'font-size': '10px'
                              #       }
                              # ),
                        html.P(id='card_text_3', children='children', style=CARD_TEXT_STYLE)
                        # html.P(id='card_text_3_sub', children='children', style={
                        #         'textAlign': 'center',"width": "100%", 'font-size': '9px'
                        #             }),
                    ],style={"height": "10rem"}
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
                        html.H4('3 Star Reviews (%)', className='card-title', style=CARD_TEXT_STYLE),
                        
#                               style={
#             'textAlign': 'center',"width": "100%", 'font-size': '10px'
#                                     }
                              
                              #),
                        html.P(id='card_text_4', children=' ', style=CARD_TEXT_STYLE)
                        # html.P(id='card_text_4_sub', children='children', style={
                        #         'textAlign': 'center',"width": "100%", 'font-size': '9px'
                        #             }),
                    ],style={"height": "10rem"}
                ),
            ]
        ),
        md=3
    )
])

content_star_rating_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='graph_star_rating'), md=12
        ),
    ]
)

content_product_rating_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='graph_product_rating'), md=12
        ),
    ]
)

content_second_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='graph_1'), md=12
        ),
    ]
)


content_third_row = dbc.Row(
    [
        dbc.Col(
            
            #dcc.Graph(id='graph_4', figure="fig"), #md=12,
            html.Img(id ="wordcloud_img") , md = 8
        ),
        
        dbc.Alert(
            children='',
            id="alert-no-wordcloud",
            fade=False,
             color="white"
        ),
        

         dbc.Col(
            [dash_table.DataTable(
            id='table_kw',
            columns=[{"name": i, "id": i} for i in ['Keyword','Relevance%']],
            style_cell={'textAlign': 'center'},
                style_cell_conditional=[
                        {
            'if': {'column_id': 'Keyword'},
                    'textAlign': 'left'
                        }
                        ]
            #data=keyword_df.head(10).to_dict('records'),
                ),
             dbc.Alert(
            children='',
            id="alert-no-table-kw",
            fade=False,
            color="white"
        ),
             
             ]
                ), 

    ]
)


content_fourth_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='graph_5'),md=8
        ),
    ]
    )


content_dynamic_top_product_row = dbc.Row(
    [
        dbc.Col(
            [
            dash_table.DataTable(
            id='table_top_products_parent_dyn',
            columns=[{"name": i, "id": i} for i in product_rating_df_gpd_static.columns],
            style_cell={'textAlign': 'center'},
                style_cell_conditional=[
                        {
            'if': {'column_id': 'Product Type'},
                    'textAlign': 'left'
                        }
                        ]
            #data=keyword_df.head(10).to_dict('records'),
                ),

             
             ]
         ),
         dbc.Col(
            [
            dash_table.DataTable(
            id='table_top_products_dyn',
            columns=[{"name": i, "id": i} for i in rating_df_gpd.columns],
            style_cell={'textAlign': 'center'},
                style_cell_conditional=[
                        {
            'if': {'column_id': 'Product Type'},
                    'textAlign': 'left'
                        }
                        ]
            #data=keyword_df.head(10).to_dict('records'),
                ),
             
             ]
         ),
        

    ]
)


content_fifth_row = dbc.Row(
    [
        html.H4('Filtered User reviews (Most recent first)', style={
            'textAlign': 'Center'
        }),
        
        
        dbc.Col(
            dash_table.DataTable(
            id='table_reviews',
            columns=[{"name": i, "id": i} for i in ['Product Type','Sub Product Type','Star Rating','Review Date','Review Text']],
            
                
            style_cell={'textAlign': 'left', 'minWidth': '80px', #'width': '50px',
                        'maxWidth': '1000px', 
                        'whiteSpace':'normal', 'height':'auto', 'lineHeight':'20px'},
            style_cell_conditional=[
                        {'if': {'column_id': ['Review Date','Star Rating']},
                            'textAlign': 'center' ,'minWidth': '100px'}
                        ],
    
            style_table={'height': '750px' ,
                         'overflow': 'auto'
                        } ,
                export_format="csv",
                page_size=5000
               
          
        ), md=12
        )
    ]
    )



content = html.Div(
    [
        html.H2('Wakefit VoC | Vire Insights', style=TEXT_STYLE),
        content_summary_row,
        html.Br(),
        llm_summary_table,
        html.Br(),
        html.P('Worst Products and their rating:', style={
            'textAlign': 'left','padding':'5px', 'font-size': '20px'
        }),
        content_summary_table,
        html.Hr(),
        html.H4('Overall summary for selected time window', style=TEXT_STYLE),
        html.Hr(),
        content_first_row,

        html.Hr(),
        content_second_row,
        html.Hr(),
        content_star_rating_row,
        html.Br(),
        html.H4('Worst performing products (based on filters)', style=TEXT_STYLE),
        content_product_rating_row, 
        #content_sentiment_row,
        # html.H6('Top and bottom products based on sentiment score (for selected date ranges)', style={
        #                                                                 'textAlign': 'left',
        #                                                                 'color': '#191970'
        #                                                             }),
        # content_sentiment_product_row,
        html.Br(),
        content_dynamic_top_product_row,
        html.Br(),
        html.H3('Review profiling', style=TEXT_STYLE),
        html.Div(    
            [html.Label('Count of reviews filtered for analysis:'),html.P(html.Div(id='count_header'))]),
        html.Hr(),
        content_third_row,
        html.Hr(),
        # content_fourth_row,
        # html.Hr(),
        content_fifth_row
        
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
     State('product_parent', 'value'), 
     State('verified_purchase', 'value'), 
     State('product_id', 'value'),
     State('platform','value')
     ]
   )
def update_card_text_1(n_clicks, start_date, end_date,star_rating,product_parent, # sentiment_list, 
                       verified_purchase, product_id, platform):
    temp_df = data.query('review_date > @start_date & review_date < @end_date')
    print("Card text 1 length : {}".format(len(temp_df)))
    print("***************UPDATE CARD TEXT 1*********************")
    filt_dict = {'star_rating':star_rating,
              #   'sentiment_tag': sentiment_list, 
                 'product_parent' : product_parent,
                 'verified_purchase':verified_purchase,
                 'product_id' : product_id,
                 'platform' : platform
                }
    
    filt_dict_updated = update_dictionary(filt_dict)

    
    for key, val in filt_dict_updated.items():
        print(key)
        print("Dataframe length : {}".format(len(temp_df)))
        temp_df = temp_df[temp_df[key].isin(val)]

    
    return len(temp_df),len(temp_df)

## POSITIVE REVIEWS
@app.callback(Output('card_text_2', 'children'),
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')],
    [State('star_rating', 'value'), 
     State('product_parent', 'value'), 
     State('verified_purchase', 'value'), 
     State('product_id', 'value'),
     State('platform','value')
     ]
    )
def update_card_text_2(n_clicks, start_date, end_date,star_rating,product_parent, #sentiment_list,
                       verified_purchase, product_id ,platform):
    temp_df = data.query('review_date > @start_date & review_date < @end_date')
    
    print("*****************UPDATE CARD TEXT 2*******************")
    filt_dict = {'star_rating':star_rating,
                 'product_parent' : product_parent,
                  'verified_purchase':verified_purchase,
                 'product_id' : product_id,
                 'platform' : platform
                }
    
    filt_dict_updated = update_dictionary(filt_dict)


    for key, val in filt_dict_updated.items():
        temp_df = temp_df[temp_df[key].isin(val)]

        
    deno = len(temp_df)
    temp_df = temp_df[(temp_df['star_rating']=="1")]
    
    pct_num = round(100*len(temp_df)/deno,1)
    
    pct = str('{} ({}%)'.format(len(temp_df),pct_num))


    return (pct)


## NEGATIVE REVIEWS
@app.callback(Output('card_text_3', 'children'),
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')],
    [State('star_rating', 'value'), 
    State('product_parent', 'value'), 
     State('verified_purchase', 'value'), 
     State('product_id', 'value'),
     State('platform','value')
    
    ]
    )
    #def update_card_text_1(n_clicks, dropdown_value, check_list_value, start_date, end_date):
def update_card_text_3(n_clicks, start_date, end_date,star_rating, product_parent, # sentiment_list,
                       verified_purchase, product_id, platform):
    temp_df = data.query('review_date > @start_date & review_date < @end_date')
    
    print("*****************UPDATE CARD TEXT 3*******************")
    filt_dict = {'star_rating':star_rating,
                # 'sentiment_tag': sentiment_list, 
                 'product_parent' : product_parent,
                  'verified_purchase':verified_purchase,
                 'product_id' : product_id,
                 'platform' : platform
                }
    
    filt_dict_updated = update_dictionary(filt_dict)
    # FILTERING DATAFRAME
    for key, val in filt_dict_updated.items():
        temp_df = temp_df[temp_df[key].isin(val)]
        
    deno = len(temp_df)
    temp_df = temp_df[temp_df['star_rating'].isin(["2"])]
    pct_num = round(100*len(temp_df)/deno,1)

    pct = str('{} ({}%)'.format(len(temp_df),pct_num))
    return pct



## NEGATIVE REVIEWS
@app.callback(Output('card_text_4', 'children'),
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')],
    [State('star_rating', 'value'), 
    State('product_parent', 'value'), 
     State('verified_purchase', 'value'), 
     State('product_id', 'value'),
     State('platform','value')
    ]
    )
    #def update_card_text_1(n_clicks, dropdown_value, check_list_value, start_date, end_date):
def update_card_text_4(n_clicks, start_date, end_date,star_rating, product_parent, # sentiment_list,
                       verified_purchase, product_id, platform):
    temp_df = data.query('review_date > @start_date & review_date < @end_date')
    
    print("*****************UPDATE CARD TEXT 3*******************")
    filt_dict = {'star_rating':star_rating,
                # 'sentiment_tag': sentiment_list, 
                 'product_parent' : product_parent,
                  'verified_purchase':verified_purchase,
                 'product_id' : product_id,
                'platform' :platform}
    
    filt_dict_updated = update_dictionary(filt_dict)
    # FILTERING DATAFRAME
    for key, val in filt_dict_updated.items():
        temp_df = temp_df[temp_df[key].isin(val)]
        
    deno = len(temp_df)
    temp_df = temp_df[temp_df['star_rating'].isin(["3"])]
    pct_num = round(100*len(temp_df)/deno,1)
    pct = str('{} ({}%)'.format(len(temp_df),pct_num))
    return pct







@app.callback(
    Output('graph_star_rating', 'figure'),
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')],
    [State('star_rating', 'value'), 
     State('product_parent', 'value'), 
     State('verified_purchase', 'value'), 
     State('product_id', 'value'),
    State('platform','value')
    ]
    )

def update_graph_star_rating(n_clicks, start_date, end_date,star_rating, product_parent,# sentiment_list, 
                   verified_purchase, product_id, platform):

    temp_df = data.query('review_date > @start_date & review_date < @end_date')

    print("*************** UPDATE LINE CHART *********************")
    filt_dict = {'star_rating':star_rating,
               #  'sentiment_tag': sentiment_list, 
                 'product_parent' : product_parent,
                  'verified_purchase':verified_purchase, 
                 'product_id' : product_id,
                 'platform' : platform
                }
    
    filt_dict_updated = update_dictionary(filt_dict)


    for key, val in filt_dict_updated.items():
        temp_df = temp_df[temp_df[key].isin(val)]

    #grouped_df = temp_df.groupby(['review_date','sentiment_tag'], as_index = False)['review_id'].count()
    grouped_df = temp_df.groupby(['week_start','star_rating'], as_index = False)['review_id'].count()
    grouped_df = grouped_df.fillna(0)


    pivot_df = grouped_df.copy(deep=True)
    #pivot_df['Week']  = pivot_df['Week'].apply({lambda x :int(x)})         
    pivot_df = pivot_df.sort_values(['week_start'], ascending = True)    
    
    x = sorted(pivot_df['week_start'])
    y1 = pivot_df['review_id']
                       
    if len(pivot_df) >0 :
        tick_count = int(max(1,round((len(pivot_df)/10),0)))
        # fig1 = px.line(x=pivot_df['Week'], y = pivot_df['review_id'],#pivot_df['pos_cc']],
        #               color_discrete_sequence=["#F6635C"],labels={
        #                                                         "review_id": "Review Count", 
        #                                                         }
        #              )
        
        fig1 = px.line(x=pivot_df['week_start'], y = pivot_df['review_id'], color =pivot_df['star_rating'],
             labels={"star_rating": "Star Rating"})
        fig1.update_traces(
            hovertemplate="<br>".join([
                "Week of: %{x}",
                "Review Count: %{y}"
            ]),

            )


        layout = go.Layout(title = "Review trend for each star rating (Weekly)",showlegend = True)

        fig = go.Figure(data=fig1.data ,#+ fig2.data, 
                        layout = layout)

        fig.update_traces(showlegend=True)
        fig.update_layout(legend_title_text='Review count')

        # Update AXES name and title 
        fig.update_xaxes(title='Week')
        fig.update_xaxes(linecolor='#61677A')

        fig.update_yaxes(title='#Reviews')
        fig.update_yaxes(linecolor='#61677A')

#         fig.update_xaxes(tickangle=-45,
#                      tickmode = 'array',
#                      tickvals = grouped_df['Week'][0::tick_count],
#                      #ticktext= [d.strftime('%Y-%m-%d') for d in datelist]
#                         )

        fig.update_layout(
            {
            'plot_bgcolor' :'rgba(0,0,0,0)',
            }
                )
    else :
        return {
        "layout": {
            "xaxis": {
                "visible": True
            },
            "yaxis": {
                "visible": True
            },
            "annotations": [
                {
                    "text": "Add more data",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ]
        }
    }
        
    return fig






## LINE CHART 
@app.callback(
    Output('graph_1', 'figure'),
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')],
    [State('star_rating', 'value'), 
     State('product_parent', 'value'), 
     State('verified_purchase', 'value'), 
     State('product_id', 'value'),
    State('platform','value')
    ]
    )

def update_graph_1(n_clicks, start_date, end_date,star_rating, product_parent,# sentiment_list, 
                   verified_purchase, product_id, platform):

    temp_df = data.query('review_date > @start_date & review_date < @end_date')

    print("*************** UPDATE LINE CHART *********************")
    filt_dict = {'star_rating':star_rating,
               #  'sentiment_tag': sentiment_list, 
                 'product_parent' : product_parent,
                  'verified_purchase':verified_purchase, 
                 'product_id' : product_id,
                 'platform' : platform
                }
    
    filt_dict_updated = update_dictionary(filt_dict)


    for key, val in filt_dict_updated.items():
        temp_df = temp_df[temp_df[key].isin(val)]

    #grouped_df = temp_df.groupby(['review_date','sentiment_tag'], as_index = False)['review_id'].count()
    
    
    
    product_rating_df = temp_df.groupby(['week_start','star_rating'], as_index = False)['review_id'].count()


    product_rating_df['star_rating'] =product_rating_df['star_rating'].astype(float)
    product_rating_df['review_id'] =product_rating_df['review_id'].astype(float)
    product_rating_df['rating_mult'] = product_rating_df['star_rating']*product_rating_df['review_id']


    product_rating_df_gpd = product_rating_df.groupby(['week_start'], as_index= False).apply(lambda x: x['rating_mult'].sum()/x['review_id'].sum())
    #print(product_rating_df_gpd)
    product_rating_df_gpd.columns = ['week_start','Weighted Rating']
    product_rating_df_gpd['Weighted Rating'] = product_rating_df_gpd['Weighted Rating'].apply(lambda x : round(x,2))
    


        
    pivot_df = product_rating_df_gpd.copy(deep=True)
    #pivot_df['Week']  = pivot_df['Week'].apply({lambda x :int(x)})         
    pivot_df = pivot_df.sort_values(['week_start'], ascending = True)    
    
    x = sorted(pivot_df['week_start'])
    y1 = pivot_df['Weighted Rating']
                       
    if len(pivot_df) >0 :
        tick_count = int(max(1,round((len(pivot_df)/10),0)))
        fig1 = px.line(x=pivot_df['week_start'], y = pivot_df['Weighted Rating'],#pivot_df['pos_cc']],
                      color_discrete_sequence=["#F6635C"],labels={
                                                                "Weighted Rating": "Weighted Rating", 
                                                                }
                     )
        fig1.update_traces(
            hovertemplate="<br>".join([
                "Week of: %{x}",
                "Weighted Rating: %{y}"
            ]),

            )


        layout = go.Layout(title = "Overall weighted rating (Weekly)",showlegend = True)

        fig = go.Figure(data=fig1.data ,#+ fig2.data, 
                        layout = layout)

        fig.update_traces(showlegend=True)
        fig.update_layout(legend_title_text='Weighted Rating')

        # Update AXES name and title 
        fig.update_xaxes(title='Week')
        fig.update_xaxes(linecolor='#61677A')

        fig.update_yaxes(title='#Reviews')
        fig.update_yaxes(linecolor='#61677A')

#         fig.update_xaxes(tickangle=-45,
#                      tickmode = 'array',
#                      tickvals = grouped_df['Week'][0::tick_count],
#                      #ticktext= [d.strftime('%Y-%m-%d') for d in datelist]
#                         )

        fig.update_layout(
            {
            'plot_bgcolor' :'rgba(0,0,0,0)',
            }
                )
    else :
        return {
        "layout": {
            "xaxis": {
                "visible": True
            },
            "yaxis": {
                "visible": True
            },
            "annotations": [
                {
                    "text": "Add more data",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ]
        }
    }
        
    return fig






####### PRODUCT RATING TREND 

@app.callback(
    Output('graph_product_rating', 'figure'),
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')],
    [State('star_rating', 'value'), 
     State('product_parent', 'value'), 
     State('verified_purchase', 'value'), 
     State('product_id', 'value'),
    State('platform','value')]
    )

def update_graph_product_rating(n_clicks, start_date, end_date,star_rating, product_parent,# sentiment_list, 
                   verified_purchase, product_id, platform):
    print("-------------------------------------------- Getting product rating ")
    temp_df = data.query('review_date > @start_date & review_date < @end_date')

    print("*****************UPDATE  RATING GRAPH ******************")
    filt_dict = {'star_rating':star_rating,
                 'product_parent' : product_parent,
                  'verified_purchase':verified_purchase,
                 'product_id' : product_id,
                 'platform' : platform
                }
    
    filt_dict_updated = update_dictionary(filt_dict)


    for key, val in filt_dict_updated.items():
        temp_df = temp_df[temp_df[key].isin(val)]
    
    temp_df['Week'] = temp_df['Week'].astype('int')
    
    product_rating_df = temp_df.groupby(['week_start','product_parent','star_rating'], as_index = False)['review_id'].count()
    product_rating_df['star_rating'] =product_rating_df['star_rating'].astype(float)
    product_rating_df['review_id'] =product_rating_df['review_id'].astype(float)
    product_rating_df['rating_mult'] = product_rating_df['star_rating']*product_rating_df['review_id']


    product_rating_df_gpd = product_rating_df.groupby(['product_parent','week_start'], as_index= False).apply(lambda x: x['rating_mult'].sum()/x['review_id'].sum())
    product_rating_df_gpd.columns = ['Product Parent','Week of','Weighted Rating']
    product_rating_df_gpd['Weighted Rating'] = product_rating_df_gpd['Weighted Rating'].apply(lambda x : round(x,2))
    product_rating_df_gpd = product_rating_df_gpd.sort_values(['Weighted Rating'], ascending = False)


    temp_df = product_rating_df_gpd.copy(deep=True)
    temp_df = temp_df.reset_index(drop=True).sort_values(['Week of','Product Parent'], ascending = True)
    fig = px.line(x=temp_df['Week of'], y = temp_df['Weighted Rating'], color =temp_df['Product Parent'],
                 labels={"color": "Product Type"})
    tick_count = int(max(1,round((len(temp_df)/10),0)))
    # fig = go.Figure(go.Scatter(mode="markers",x=temp_df['Week'], y=temp_df['Weighted Rating'], marker_color =temp_df['Product Parent'], line_shape='spline'))
    # Change title 
    fig.update_layout({'title':'Product Type wise rating trend (weekly)',
                     'plot_bgcolor' :'rgba(0,0,0,0)',
                    }),
    # Change the x-axis name
    fig.update_xaxes(title='Week')
    fig.update_xaxes(linecolor='#61677A')
    # Change the y-axis name
    fig.update_yaxes(title='Product Rating')
    fig.update_yaxes(linecolor='#61677A')
    # # Update Legend name and title 
    fig.update_traces(
    hovertemplate= "<br>".join(["Week: %{x}",
                "Weighted Rating: %{y}"
            ]),

            )
    
    fig.update_xaxes(tickangle=-45,
                 tickmode = 'array',
                 tickvals = temp_df['Week of'][0::tick_count],
                 #ticktext= [d.strftime('%Y-%m-%d') for d in datelist]
                    )

        
    return fig



## WORDCLOUD 
@app.callback(
    Output('wordcloud_img', 'src'),
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')],
    [State('star_rating', 'value'), 
     State('product_parent', 'value'), 
     State('verified_purchase', 'value'), 
     State('product_id', 'value'),
     State('platform','value')
     ]
    )

def update_graph_4(n_clicks, start_date, end_date,star_rating,product_parent, # sentiment_list, 
                   verified_purchase, product_id, platform):


    temp_df = data.query('review_date > @start_date & review_date < @end_date')
    print("**************** WORDCLOUD ********************")

    filt_dict = {'star_rating':star_rating,
                 #'sentiment_tag': sentiment_list, 
                  'verified_purchase':verified_purchase,
                 'product_parent' :product_parent,
                 'product_id' : product_id,
                 'platform' : platform
                }
    
    filt_dict_updated = update_dictionary(filt_dict)


    #print("Filtered dictionary :{}".format(filt_dict_updated))

    for key, val in filt_dict_updated.items():
        #print("Filtering {}".format(key))
        temp_df = temp_df[temp_df[key].isin(val)]
        #print("Len of dataframe = {}".format(len(temp_df)))
        
    if len(temp_df) >5:

    # Sample data and figure
        img = BytesIO()
        word_list = flatten_list(temp_df['tags'].to_list())
        #print(word_list)
        fig = plot_wordcloud(word_list)
        fig.save(img, format="PNG")
    
        return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())


#####################################################################################

## KEYWORD TABLE
@app.callback(
    Output('table_kw', 'data'),
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')],
    [State('star_rating', 'value'), 
     State('product_parent', 'value'), 
     State('verified_purchase', 'value'), 
     State('product_id', 'value'),
     State('platform','value')
     ]
    )
def update_keyword_table(n_clicks, start_date, end_date,star_rating,product_parent ,# sentiment_list,
                         verified_purchase, product_id, platform):


    temp_df = data.query('review_date > @start_date & review_date < @end_date')
    print("*************** TABLE OF KEYWORDS *********************")

    filt_dict = {'star_rating':star_rating,
                # 'sentiment_tag': sentiment_list, 
                  'verified_purchase':verified_purchase,
                 'product_parent' : product_parent,
                 'product_id' : product_id,
                 'platform' : platform
                }
    
    filt_dict_updated = update_dictionary(filt_dict)


    for key, val in filt_dict_updated.items():
        #print("Filtering {}".format(key))
        temp_df = temp_df[temp_df[key].isin(val)]


    df_length = len(temp_df)
    
    word_list = flatten_list(temp_df['tags'].to_list())

    if len(temp_df) >5:
        keyword_df = top_keywords_df(flatten_list(temp_df['tags'].to_list()))
        keyword_df['Relevance%'] = round(100*keyword_df['Frequency']/df_length,2)
        keyword_df =keyword_df.drop(['Frequency'], axis = 1)
        #print(keyword_df)
        return keyword_df.head(10).to_dict('records')
    
    
    
    
    
## TOP PRODUCT ON PRODUCT ID LEVEL  TABLE
@app.callback(
    Output('table_top_products_dyn', 'data'),
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')],
    [State('star_rating', 'value'), 
     State('product_parent', 'value'), 
     State('verified_purchase', 'value'), 
     State('product_id', 'value'),
     State('platform','value')
     ]
    )
def update_keyword_table(n_clicks, start_date, end_date,star_rating,product_parent ,# sentiment_list,
                         verified_purchase, product_id, platform):


    temp_df = data.query('review_date > @start_date & review_date < @end_date')
    print("*************** TABLE OF KEYWORDS *********************")

    filt_dict = {'star_rating':star_rating,
                # 'sentiment_tag': sentiment_list, 
                  'verified_purchase':verified_purchase,
                 'product_parent' : product_parent,
                 'product_id' : product_id,
                 'platform' : platform
                }
    
    filt_dict_updated = update_dictionary(filt_dict)


    for key, val in filt_dict_updated.items():
        #print("Filtering {}".format(key))
        temp_df = temp_df[temp_df[key].isin(val)]

    
    
    rating_df = temp_df.groupby(['product_id','star_rating'], as_index = False)['review_id'].count()

    rating_df = rating_df[rating_df['review_id']>10]
    rating_df['star_rating'] =rating_df['star_rating'].astype(float)
    rating_df['review_id'] =rating_df['review_id'].astype(float)
    rating_df['rating_mult'] = rating_df['star_rating']*rating_df['review_id']

    #rating_df_gpd = rating_df.groupby(['product_id'], as_index= False).apply({lambda x: x['rating_mult'].sum()/x['review_id'].sum()})

    rating_df_gpd = rating_df.groupby(['product_id'], as_index= False).agg({'rating_mult':'sum','review_id':'sum'})
    rating_df_gpd['weighted_rating'] = round(rating_df_gpd['rating_mult']/rating_df_gpd['review_id'],2)
    rating_df_gpd = rating_df_gpd.drop(['rating_mult'], axis= 1)
    rating_df_gpd.columns = ['Sub Product Type','Review Count','Product Rating']
    rating_df_gpd['Product Rating'] = rating_df_gpd['Product Rating'].apply(lambda x : round(x,2))
    rating_df_gpd = rating_df_gpd.sort_values(['Product Rating'], ascending = True)
    rating_df_gpd = rating_df_gpd[rating_df_gpd['Sub Product Type']!='-']
    
    
    return rating_df_gpd.head(5).to_dict('records')
    
    
    
## TOP PRODUCT ON PRODUCT ID LEVEL  TABLE
@app.callback(
    Output('table_top_products_parent_dyn', 'data'),
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')],
    [State('star_rating', 'value'), 
     State('product_parent', 'value'), 
     State('verified_purchase', 'value'), 
     State('product_id', 'value'),
     State('platform','value')
     ]
    )
def update_keyword_table(n_clicks, start_date, end_date,star_rating,product_parent ,# sentiment_list,
                         verified_purchase, product_id, platform):


    temp_df = data.query('review_date > @start_date & review_date < @end_date')
    print("*************** TABLE OF KEYWORDS *********************")

    filt_dict = {'star_rating':star_rating,
                # 'sentiment_tag': sentiment_list, 
                  'verified_purchase':verified_purchase,
                 'product_parent' : product_parent,
                 'product_id' : product_id,
                 'platform' : platform
                }
    
    filt_dict_updated = update_dictionary(filt_dict)


    for key, val in filt_dict_updated.items():        #print("Filtering {}".format(key))
        temp_df = temp_df[temp_df[key].isin(val)]

        
        
    
    product_rating_df = temp_df.groupby(['week_start','product_parent','star_rating'], as_index = False)['review_id'].count()
    product_rating_df['star_rating'] =product_rating_df['star_rating'].astype(float)
    product_rating_df['review_id'] =product_rating_df['review_id'].astype(float)
    product_rating_df['rating_mult'] = product_rating_df['star_rating']*product_rating_df['review_id']


    ##### making static table for top 
    product_rating_df_gpd_static = product_rating_df.groupby(['product_parent'], as_index= False).agg({'rating_mult':'sum','review_id':'sum'})
    product_rating_df_gpd_static = product_rating_df_gpd_static[product_rating_df_gpd_static['review_id']>10]
    product_rating_df_gpd_static['weighted_rating'] = round(product_rating_df_gpd_static['rating_mult']/product_rating_df_gpd_static['review_id'],2)
    product_rating_df_gpd_static = product_rating_df_gpd_static.drop(['rating_mult'], axis= 1)
    product_rating_df_gpd_static.columns = ['Product Type','Review Count','Product Rating']
    product_rating_df_gpd_static['Product Rating'] = product_rating_df_gpd_static['Product Rating'].apply(lambda x : round(x,2))
    product_rating_df_gpd_static = product_rating_df_gpd_static.sort_values(['Product Rating'], ascending = True)

    ret_df = product_rating_df_gpd_static.copy(deep=True)
    return ret_df.to_dict('records')
    
    
    


## HORIZONTAL BAR CHART
@app.callback(
    #Output('graph_4', 'img'),
    Output('graph_5', 'figure'),
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')],
    [State('star_rating', 'value'), 
     State('product_parent', 'value'), 
     State('verified_purchase', 'value'), 
     State('product_id', 'value'),
     State('platform','value')
     ]
    )
def update_graph_5(n_clicks, start_date, end_date,star_rating,product_parent,# sentiment_list, 
                   verified_purchase, product_id, platform):

    star_rating_str = str(star_rating)[1:-1]
    temp_df = data.query('review_date > @start_date & review_date < @end_date')
    print("****************UPDATE H. BAR CHART********************")
    filt_dict = {'star_rating':star_rating,
                 # 'sentiment_tag': sentiment_list, 
                  'verified_purchase':verified_purchase, 
                 'product_parent' : product_parent,
                 'product_id' : product_id,
                 'platform' : platform
                }
    
    filt_dict_updated = update_dictionary(filt_dict)


    for key, val in filt_dict_updated.items():
        #print("Filtering {}".format(key))
        temp_df = temp_df[temp_df[key].isin(val)]
        #print("Len of dataframe = {}".format(len(temp_df)))

    grouped_df = temp_df.groupby(['star_rating'], as_index= False)['review_id'].count()

    if len(temp_df) >0:
        fig = go.Figure([go.Bar(x = grouped_df['review_id'], y = grouped_df['star_rating'], marker_color = 'royalblue',
                             orientation = 'h',
                             textposition = 'outside',
                              name=""
                             )])
        fig.update_xaxes(title='# Review Count', showline=True,
                linewidth=1,
                linecolor='grey',
                mirror=True)

        fig.update_yaxes(title = "Star rating on Marketplace",showline=True,
                linewidth=1,
                linecolor='grey',
                mirror=True)
        
        fig.update_layout(title='Bar Chart of Star Rating Distribution')
        fig.update_traces(
        hovertemplate="<br>".join([
            "#Reviews: %{x}",
            "Star Rating: %{y}"
        ])
        )

        return fig
    else :
        return {
        "layout": {
            "xaxis": {
                "visible": True
            },
            "yaxis": {
                "visible": True
            },
            "annotations": [
                {
                    "text": "No matching data found",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ]
        }
    }

#####################################################################################

## REVIEW TABLE
@app.callback(
    Output('table_reviews', 'data'),
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')],
    [State('star_rating', 'value'), 
     State('product_parent', 'value'), 
     State('verified_purchase', 'value'), 
     State('product_id', 'value'),
     State('platform','value')
     ]
    )
def update_review_table(n_clicks, start_date, end_date,star_rating, product_parent,# sentiment_list, 
                        verified_purchase, product_id, platform):

    temp_df = data.query('review_date > @start_date & review_date < @end_date')
    print("*************** TABLE OF KEYWORDS *********************")

    filt_dict = {'star_rating':star_rating,
                # 'sentiment_tag': sentiment_list, 
                  'verified_purchase': verified_purchase,
                 'product_parent' : product_parent,
                 'product_id' : product_id,
                 'platform' : platform
                }
    
    filt_dict_updated = update_dictionary(filt_dict)

    for key, val in filt_dict_updated.items():
        temp_df = temp_df[temp_df[key].isin(val)]
    
    temp_df = temp_df.sort_values(['review_date'], ascending = False)
    temp_df = temp_df[review_cols]
    temp_df['review_date'] =  temp_df['review_date'].dt.strftime('%d-%m-%Y')
    
    temp_df.columns = ['Product Type','Sub Product Type','Star Rating','Review Date','Review Text']
    
    temp_df = temp_df.drop_duplicates(['Product Type','Sub Product Type','Star Rating', 'Review Text'], keep='first')
    
    
    if len(temp_df) >0:
        return temp_df.to_dict('records') #temp_df.head(20).to_dict('records')
    
    else :
        return "Insufficient data"



#Update dropDown1 options
@app.callback([
        Output('my-date-picker-range', 'start_date'),
        Output('my-date-picker-range', 'end_date'),
        Output('star_rating', 'value'), 
        Output('product_parent', 'value'), 
        Output('verified_purchase', 'value'), 
        Output('product_id', 'value'),
        Output('platform','value')
        ],
        Input('clear_button', 'n_clicks'),
        )

def clearDropDown1(n_clicks):
    print("**************** CLEAR ALL FUNCTION ********************")
    if n_clicks != 0: #Don't clear options when loading page for the first time
        return ['2023-08-01','2023-08-31',['1','2','3','4'],
                list(data['product_parent'].unique()),#['POSITIVE','NEGATIVE'],
             ['Y','N'],
             list(data['product_id'].unique()),
            ['amazon','flipkart']
               ] #Return an empty list of options
    
    










if __name__ == '__main__':
    app.run_server(port='8085')




