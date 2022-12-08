from datetime import datetime
import imaplib
from operator import truediv
from dash import Dash, dcc, html, Input, Output, State
import dash_daq as daq
from email.mime.text import MIMEText
import dash_bootstrap_components as dbc
import mqtt
import rfid_mqtt
from helper import setMotor, setLED, updateDHT, dht, sendMail, getResponse, getMotorStatus

external_stylesheets = [dbc.themes.BOOTSTRAP]

motor_on_img = '/assets/img1.png'
motor_off_img = '/assets/img0.png'
led_on_img = '/assets/light_on.png'
led_off_img = '/assets/light_off.png'
profile_img = '/assets/profile'
is_on = False
light_email = False
temp_email = False
oldUser = rfid_mqtt.selectedUser[0]

app = Dash(__name__, update_title=None, external_stylesheets=external_stylesheets)


navbar = dbc.NavbarSimple(
    brand="Smart Home Dashboard",
    brand_href="#",
    color="primary",
    dark=True,
    style={'align-content': 'center'},
    children = [
        dbc.NavItem(
            daq.ToggleSwitch(
                id='dark-mode-switch',
                value=False
            )
        )
    ]
    
)
app.layout = html.Div([
    navbar,
    # html.H1('Dashboard', style={'margin':'20px 0px'}),

    html.Div([

        html.Div([
            html.H4('User Profile', className='h4'),
            html.Img(id='profile_img', src=profile_img, width=300, height=300),
            html.Div("Username: ", id='user-name', className='user-name'),
            html.Div("Light Intensity: ", id='light-intensity', className='user-info'),
            html.Div("Humidity: ", id='hum', className='user-info'),
            html.Div("Temperature: ", id='tem', className='user-info'),

        ], className='div1'),
            
        daq.Thermometer(
            showCurrentValue=True,
            color= "#a84849",
            id='temperature-gauge',
            label="Temperature",
            height=200,
            units="°C",
            value=dht.temperature,
            max=40,
            className='div2'
        ),

        daq.Gauge(
            showCurrentValue=True,
            color={"gradient":True,"ranges":{"blue":[0,30],"yellow":[30,70],"red":[70,100]}},
            id='humidity-gauge',
            size = 250,
            label="Humidity",
            units="%",
            value=dht.humidity,
            max=100,
            className='div3'
        ),
        
        html.Div([
            
            dcc.Slider(
                0, 1200, value=mqtt.light_sensivity, id="light_sensivity_slider", vertical=True, verticalHeight=200, className='light-slider'
            ),

            html.Div([
                html.Div(id='light_sensivity_text'),
                html.Div('Hi', id='light-email-div'),
            ]),

        ], className='div4'),


        html.Div([
            html.H4('Fan Status', className='h4'),
            html.Img(id='motor_status_img', src=motor_on_img, width=300, height=300),
        ],className='div5'),

        html.Div([
            html.H4('Light Status', className='h4'),
            html.Img(id='led_status_img', src=led_off_img, width=300, height=300),
        ],className='div6'),

    ], className='parent'),
    
    
    html.Br(),
    
    
    dcc.Interval(
        id='clientside-interval',
        n_intervals=1,
        interval=1000
    ),
    dcc.Interval(
        id='reading-interval',
        n_intervals=1,
        interval=5000
    ),
    dcc.Store(
        id='temperature', data=dht.temperature
    ),
    dcc.Store(
        id='humidity', data=dht.humidity
    ),
    dcc.Store(
        id='should-send-email', data=True
    ),
    dcc.Store(
        id='light-email-sent', data=False
    ),
    dcc.Store(
        id='light-email', data=is_on
    ),
    dcc.Interval(
        id='light-email-intervals',
        n_intervals=1,
        interval=2000
    ),
  
    
    html.Div(
        id='placeholder',
        children='qwe',
        style={'display':'none'}
    )
], style={'textAlign': 'center', 'background': '#f0f2ec'})



@app.callback(
    Output('user-name', 'children'),
    Output('light-intensity', 'children'),
    Output('hum', 'children'),
    Output('tem', 'children'),
    Input('light-email-intervals', 'n_intervals'),
)

def update_user_info(n_intervals):
    # check current user and send email
    global oldUser
    if rfid_mqtt.selectedUser[0] != oldUser:
        oldUser = rfid_mqtt.selectedUser[0]
        sendMail('2044092@iotvanier.com', 'iot project1', 'Hi, ' + rfid_mqtt.selectedUser[1]+ ' login in on ' + str(datetime.now()) )
    
    return 'Welcome '+ rfid_mqtt.selectedUser[1], 'Light Intensity: '+str(rfid_mqtt.selectedUser[4]), 'Humidity: ' + str(rfid_mqtt.selectedUser[3]), 'Temperature: '+ str(rfid_mqtt.selectedUser[2])



@app.callback(
    Output('humidity', 'data'),
    Output('temperature', 'data'),
    Output('should-send-email', 'data'),
    Output('motor_status_img', 'src'),
    Output('led_status_img', 'src'),
    Output('light_sensivity_slider', 'value'),
    Output('light_sensivity_text', 'children'),
    Input('clientside-interval', 'n_intervals'),
    State('should-send-email', 'data'),
    
)
def update_data(n_intervals, should_send_email):
    global light_email
    global temp_email
    light = mqtt.light_sensivity
    print(rfid_mqtt.selectedUser[1])
    if light < rfid_mqtt.selectedUser[4] and not light_email:
        light_email = True
        setLED(True)
        sendMail('2044092@iotvanier.com','LED notification', "LED is turned on at " + str(datetime.now()))
    elif light > rfid_mqtt.selectedUser[4] and light_email:
        print('led is off')
        light_email = False
        setLED(False)
    global is_on
    
    updateDHT()    #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.

    if (dht.temperature > rfid_mqtt.selectedUser[2] and temp_email):
        temp_email = False
        print('sending temp email..')
        sendMail('2044092@iotvanier.com', 'iot project1', 'Hi, The temperature is over ' + str(rfid_mqtt.selectedUser[2]) + '. Do you want to turn on the fan?')
    
    if (dht.temperature < rfid_mqtt.selectedUser[2]):
        print('turning off motor')
        # GPIO.output()
        setMotor(False)
        temp_email = True
        is_on = False
        
    return dht.humidity, dht.temperature, light_email, motor_on_img if getMotorStatus() else motor_off_img, led_on_img if light < rfid_mqtt.selectedUser[4] else led_off_img, light, 'Light brightness ' + str(light)

@app.callback(
    Output('light-email', 'data'),
    Output('light-email-sent', 'data'),
    Output('light-email-div', 'children'),
    Input('light-email-intervals', 'n_intervals'),
    State('light-email', 'data'),
    State('light-email-sent', 'data')
)
def email_status(n_intervals, should_send_email, light_email_sent):
    sse = should_send_email
    les = light_email_sent
    if (mqtt.light_sensivity < 400):
        if (not light_email_sent):
            sse = False
            les = True
            # sendmail
            print("sending email")
    else:
        sse = True
        les = False

    return sse, les, 'Email sent' if les else ''

@app.callback(
    Output('placeholder', 'children'),
    Input('reading-interval', 'n_intervals')
)
def read_email(n_intervals):
    getResponse()
    return ''

app.clientside_callback(
    """
    function(data) {
        return data;
    }
    """,
    Output("temperature-gauge", 'value'),
    Input('temperature', 'data')
)

app.clientside_callback(
    """
    function(data) {
        return data;
    }
    """,
    Output("humidity-gauge", 'value'),
    Input('humidity', 'data')
)


if __name__ == '__main__':
    mqtt.run()
    rfid_mqtt.run()
    app.run_server(debug=True, host="0.0.0.0", port="8050")