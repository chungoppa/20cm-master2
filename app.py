import time
from collections import Counter
from flask import Flask, request, abort, app
import json
import urllib3

from linebot.models import *
import gspread
from oauth2client.service_account import ServiceAccountCredentials
# import locale
from werkzeug.middleware.proxy_fix import ProxyFix
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError,
    LineBotApiError)

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1, x_proto=1)

# spreadsheet
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('dumbbot-8fad35afb0c6.json', scope)
client = gspread.authorize(creds)
mainsheet = client.open('SGVN')
sheet = client.open('SGVN').sheet1
tmpordersheet = mainsheet.worksheet('tmporder')
tmpuserinfo = mainsheet.worksheet(('tmpuserinfo'))
ordersheet = mainsheet.worksheet('orders')
userinfosheet = mainsheet.worksheet('userinfo')
# questionssheet = mainsheet.worksheet('questionsInOderdelivery')
# submenusheet = mainsheet.worksheet('subMenu')
# menusheet = mainsheet.worksheet('Menu')
reportReceiver = mainsheet.worksheet('reportReceiver')

# urllib3
http = urllib3.PoolManager()
# token
# line_bot_api = LineBotApi('bOiXla2lbcGsYnZkXnhxOAkyAzuGTSDrGVZGF/hrMjlws0+DhIoFq8i9f3xjR8DHmR6KqVpU/UW+SR8yAKDyt/PEecZg5jU9AjAIPQBvYpZRrQPrzWVQCmd10l8q4E0q17mtskg/bljPsPxPFSUj9QdB04t89/1O/w1cDnyilFU=')
line_bot_api = LineBotApi('cX51Ve+hutrgp3yj8vU0+HzTgfDT3v5vJm8Z8ZswRLI09+tqBp3KzUA+wXyOiR3GovF0UEd5yip6Jfjw5gdUPv4jYWIjsvJNxifxwuM/S9LhVSbZcZCW7lREgwXT3/Zt9KNENifbpWQ8qCKRW+txiAdB04t89/1O/w1cDnyilFU=')

# Channel Secret
# handler = WebhookHandler('6c7ba1b67dfdafeb29f7b546465154c4')
handler = WebhookHandler('f958e6eee611d7493c2305a783c3586c')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(FollowEvent)
def sendGreetingms(event):

        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            uid = profile.user_id
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='ご登録ありがとうございます。 \nこちらは居酒屋「くーろん」・原田商店のページでございます。\nこちらからレストラン予約・食材、弁当のデリバリー注文が可能です。 \n下記メニューからお進みください。\n今後とも宜しくお願いします。'))

def getchars(list):
    chuoi1=''
    for c in list:
        if not c.isdigit() :
            chuoi1= chuoi1+c
        else:
            continue
    return str(chuoi1)
def getnums(list):
    print(list)
    chuoi =''
    for n in list:
        if n.isdigit():
            chuoi= chuoi+n
        else:
            break
    print(chuoi)
    return str(chuoi)
def phonenumbervalidator(phonenumber):
    digit = True
    counter = 0
    for n in phonenumber:
        counter =counter+1
        if not n.isdigit():
            digit = False
    if digit == False or counter >10 or counter<9:
        return '電話番号は数値を入力してください。'
    return 'ok'

@handler.add((MessageEvent),message=TextMessage)
def getUserinfo(event):
    text = event.message.text
    try:
        tmp = tmpordersheet.find(str(event.source.user_id))
    except:
        tmp = None
    if tmp is None:
        print("")
    else:
        col= None
        row =None
        try:
            tmp2 = tmpuserinfo.find(str(event.source.user_id))
            cell_list = tmpuserinfo.range('B' + str(tmp2.row) + ':G' + str(tmp2.row))
            for cell in cell_list:
                if cell.value == '':
                    col = cell.col
                    row = cell.row
                    break
        except:
            tmp2 = None
        if col == 2 and (not cell_list is None):
            tmpuserinfo.update_cell(row, col, text)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='電話番号を教えてください。'))
        elif col == 3 and (not cell_list is None):
            # phonenumber validator
            checker = phonenumbervalidator(text)
            if checker == 'ok':
                tmpuserinfo.update_cell(row, col, text)
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='住所を教えてください。',quick_reply=QuickReply(items=[QuickReplyButton(action=LocationAction(label='share your location'))])))
            else:
                line_bot_api.reply_message(event.reply_token ,[TextSendMessage(text=checker),TextSendMessage(text='電話番号を教えてください。')])
        # location
        elif col == 4 and (not cell_list is None):
            tmpuserinfo.update_cell(row, col, text)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='マンション名を教えてください。'))
        # datetime
        elif col == 5 and (not cell_list is None):
            tmpuserinfo.update_cell(row, col, text)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='ご希望の配達日時を教えてください。',quick_reply=QuickReply(items=[QuickReplyButton(action=DatetimePickerAction(label='pick your time',data='datetime',mode='datetime'))])))
        elif col == 6 and (not cell_list is None):
            tmpuserinfo.update_cell(row, col, text)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='その他特別な要求がありますか？。'))
        elif col == 7 and (not cell_list is None):
            tmpuserinfo.update_cell(row, col, text)
            cell_listo= []
            cell_list = tmpordersheet.range('C' + str(tmp.row) + ':Z' + str(tmp.row))
            for cell in cell_list:
                if not cell.value == '':
                    cell_listo.append(cell.value)
            line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=str(tmpuserinfo.cell(row,2).value)+'さんの注文\n'
                                                                        + '▼注文の品: \n ' + getorderfromlist(cell_listo)
                                                                        + '\n \n▼お客様の情報'
                                                                        +'\n電話番号 : '+ str(tmpuserinfo.cell(row,3).value)
                                                                        +'\n住所 : ' + str(tmpuserinfo.cell(row,4).value)
                                                                        +'\nマンション名 : ' + str(tmpuserinfo.cell(row,5).value)
                                                                        +'\n配達希望日時 : ' + str(tmpuserinfo.cell(row,6).value)
                                                                        +'\nその他: ' + str(tmpuserinfo.cell(row,7).value)

                                                                        +' \n \ngrabデリバリーを使ってお届け致します。\n配達料金50,000 vndご負担お願いいたします。'
                                                                        ,quick_reply=QuickReply(items=[
                                                                                   QuickReplyButton(
                                                                                       action=MessageAction(label="デリバリー", text="デリバリー")
                                                                                   ),QuickReplyButton(
                                                                                       action=MessageAction(label="情報変更", text="情報変更")
                                                                                   )]))
                                                           ])

        elif col is None and ( not cell_list is None) and text == 'デリバリー':
            cell_listo= []
            cell_list = tmpordersheet.range('C' + str(tmp.row) + ':Z' + str(tmp.row))
            for cell in cell_list:
                if not cell.value == '':
                    cell_listo.append(cell.value)
            receiver = reportReceiver.cell(1,1).value
            print(receiver)
            print(tmp2.row)
            line_bot_api.push_message(receiver,TextSendMessage(text=
                                                               str(tmpuserinfo.cell(tmp2.row,2).value)+'さんの注文'
                                                                        + '\n \n▼注文の品: \n '
                                                                        + getorderfromlist(cell_listo)
                                                                        + '\n▼お客様の情報'
                                                                        +'\n電話番号 : '+ str(tmpuserinfo.cell(tmp2.row,3).value)
                                                                        +'\n住所 : ' + str(tmpuserinfo.cell(tmp2.row,4).value)
                                                                        +'\nマンション名 : ' + str(tmpuserinfo.cell(tmp2.row,5).value)
                                                                        +'\n配達希望日時 : ' + str(tmpuserinfo.cell(tmp2.row,6).value)
                                                                        +'\nその他 : ' + str(tmpuserinfo.cell(tmp2.row,7).value)

                                                                    ))
            ordersheet.insert_row(tmpordersheet.row_values(tmp.row))
            userinfosheet.insert_row(tmpuserinfo.row_values(tmp2.row))
            tmpordersheet.delete_row(tmp.row)
            tmpuserinfo.delete_row(tmp2.row)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='ご注文ありがとうございます。'))

        elif col is None and (not cell_list is None) and text =='情報変更' :
            tmpuserinfo.delete_row(tmp2.row)
            line_bot_api.reply_message(event.reply_token,[TextSendMessage(text='並べ替える場合は、もう一度食材・弁当デリバリーを選択します \nさて、今私はあなたにもう一度あなたの情報を尋ねます'),TextSendMessage(text='お名前を教えてください。?')])
            new = [str(event.source.user_id), ""]
            tmpuserinfo.insert_row(new)

def getorderfromlist(list):
    strorder = ''
    tmplist = list
    totalprice = 0
    for i in Counter(tmplist):
        count = list.count(i)
        price = getpricebyname(i)*count
        totalprice = totalprice + price
        strorder = strorder + str(i) +' : x '+ str(count) +' - ' + format(price,',d')+'\n'
    return strorder + '合計 :   '+format(totalprice, ',d')

def clearorder(event):
    tmp = None
    tmp2 = None
    try:
        tmp = tmpordersheet.find(str(event.source.user_id))
        tmp2 = tmpuserinfo.find(str(event.source.user_id))
    except:
        print(' something wrong !, im not able to clear your temporary data  。')
    if not tmp is None :
        tmpordersheet.delete_row(tmp.row)
    if not tmp2 is None :
        tmpuserinfo.delete_row(tmp2.row)

def getpricebyname(name):
    if name == 'サンマの開き':
        return 60000
    elif name == '塩サバ切り身':
        return 60000
    elif name == 'サケ切り身':
        return 75000
    elif name == 'サワラの味噌漬け':
        return 65000
    elif name == '野菜サラダ':
        return 20000
    elif name == 'れんこんキンピラ':
        return 30000
    elif name == 'ひじきの炒め煮':
        return 30000
    elif name == '高菜のじゃこ炒め':
        return 30000
    elif name == '紅茶豚（スライス５枚）':
        return 110000
    elif name == '手作り冷凍餃子（５個）':
        return 35000
    elif name == '砂肝にんにく炒め':
        return 80000
    elif name == 'ハンバーグ（ソース付）':
        return 110000
    elif name == 'エビチリ':
        return 100000
    elif name == 'サバの味噌煮':
        return 100000
    elif name == '豚生姜焼き':
        return 90000
    elif name == 'レバニラ炒め':
        return 90000
    elif name == '手羽醤油焼き':
        return 90000
    elif name == '中華丼（ソースのみ）':
        return 100000

# '生鮮食品  1
def submenu1(event):
    サンマの開き = request.url_root + '/static/サンマの開き.JPG'
    塩サバ切り身 = request.url_root + '/static/塩サバ切り身.JPG'
    サケ切り身 = request.url_root + '/static/サケ切り身.JPG'
    サワラの味噌漬け = request.url_root +'/static/サワラの味噌漬け.JPG'
    carousel_template = CarouselTemplate(columns=[
        CarouselColumn(text=format(getpricebyname('サンマの開き'),',d'), title='サンマの開き',
                       thumbnail_image_url=サンマの開き, actions=[PostbackAction(label='カートに追加', data='サンマの開き')]),
        CarouselColumn(text=format(getpricebyname('塩サバ切り身'),',d'), title='塩サバ切り身',
                       thumbnail_image_url=塩サバ切り身, actions=[PostbackAction(label='カートに追加', data='塩サバ切り身')]),
        CarouselColumn(text=format(getpricebyname('サケ切り身'),',d'), title='サケ切り身',
                       thumbnail_image_url=サケ切り身, actions=[PostbackAction(label='カートに追加', data='サケ切り身')]),
        CarouselColumn(text=format(getpricebyname('サワラの味噌漬け'),',d'), title='サワラの味噌漬け',
                       thumbnail_image_url=サワラの味噌漬け, actions=[PostbackAction(label='カートに追加', data='サワラの味噌漬け')]),
    ])
    template_message = TemplateSendMessage(alt_text='Carousel alt text', template=carousel_template, quick_reply=QuickReply(items=[QuickReplyButton(action=MessageAction(label="完了", text="完了")),QuickReplyButton(action=MessageAction(label="戻る", text="戻る"))]))
    line_bot_api.push_message(event.source.user_id, template_message)

# 一品物 4
def submenu2(event):
    紅茶豚= request.url_root + '/static/紅茶豚（スライス５枚）.JPG'
    手作り = request.url_root + '/static/1.JPG'
    砂肝にんにく炒め = request.url_root + '/static/砂肝にんにく炒め.JPG'
    ハンバーグ = request.url_root +'/static/ハンバーグ（ソース付）.JPG'

    エビチリ = request.url_root +'/static/エビチリ.JPG'
    サバの味噌煮 = request.url_root + '/static/サバの味噌煮.JPG'
    豚生姜焼き = request.url_root + '/static/豚生姜焼き.JPG'
    レバニラ炒め = request.url_root + '/static/レバニラ炒め.JPG'

    手羽醤油焼き = request.url_root + '/static/手羽醤油焼き.JPG'
    中華丼 = request.url_root + '/static/中華丼（ソースのみ）.JPG'
    carousel_template = CarouselTemplate(columns=[
        CarouselColumn(text=format(getpricebyname('紅茶豚（スライス５枚）'),',d'), title='紅茶豚（スライス５枚）',
                       thumbnail_image_url=紅茶豚, actions=[PostbackAction(label='カートに追加', data='紅茶豚（スライス５枚）')]),
        CarouselColumn(text=format(getpricebyname('手作り冷凍餃子（５個）'),',d'), title='手作り冷凍餃子（５個）',
                        thumbnail_image_url=手作り, actions=[PostbackAction(label='カートに追加', data='手作り冷凍餃子（５個）')]),
        CarouselColumn(text=format(getpricebyname('砂肝にんにく炒め'),',d'), title='砂肝にんにく炒め',
                       thumbnail_image_url=砂肝にんにく炒め, actions=[PostbackAction(label='カートに追加', data='砂肝にんにく炒め')]),
        CarouselColumn(text=format(getpricebyname('ハンバーグ（ソース付）'),',d'), title='ハンバーグ',
                       thumbnail_image_url=ハンバーグ, actions=[PostbackAction(label='カートに追加', data='ハンバーグ')]),

        CarouselColumn(text=format(getpricebyname('エビチリ'),',d'),title='エビチリ',
                       thumbnail_image_url=エビチリ, actions=[PostbackAction(label='カートに追加', data='エビチリ')]),
        CarouselColumn(text=format(getpricebyname('サバの味噌煮'),',d'), title='サバの味噌煮',
                       thumbnail_image_url=サバの味噌煮, actions=[PostbackAction(label='カートに追加', data='サバの味噌煮')]),
        CarouselColumn(text=format(getpricebyname('豚生姜焼き'),',d'), title='豚生姜焼き',
                       thumbnail_image_url=豚生姜焼き, actions=[PostbackAction(label='カートに追加', data='豚生姜焼き')]),
        CarouselColumn(text=format(getpricebyname('レバニラ炒め'),',d'), title='レバニラ炒め',
                       thumbnail_image_url=レバニラ炒め, actions=[PostbackAction(label='カートに追加', data='レバニラ炒め')]),

        CarouselColumn(text=format(getpricebyname('手羽醤油焼き'),',d'), title='手羽醤油焼き',
                       thumbnail_image_url=手羽醤油焼き, actions=[PostbackAction(label='カートに追加', data='手羽醤油焼き')]),
        CarouselColumn(text=format(getpricebyname('中華丼（ソースのみ）'),',d'), title='中華丼（ソースのみ）',
                       thumbnail_image_url=中華丼, actions=[PostbackAction(label='カートに追加', data='中華丼（ソースのみ）')]),
    ])
    template_message = TemplateSendMessage(alt_text='Carousel alt text', template=carousel_template, quick_reply=QuickReply(items=[QuickReplyButton(action=MessageAction(label="完了", text="完了")),QuickReplyButton(action=MessageAction(label="戻る", text="戻る"))]))
    line_bot_api.push_message(event.source.user_id, template_message)

# お潰物・サラダ他　約一人前 2
def submenu3(event):
    野菜サラダ = request.url_root + '/static/野菜サラダ.JPG'
    carousel_template = CarouselTemplate(columns=[
        CarouselColumn(text=format(getpricebyname('野菜サラダ'),',d'), title='野菜サラダ',
                       thumbnail_image_url=野菜サラダ, actions=[PostbackAction(label='カートに追加', data='野菜サラダ')]),
    ])
    template_message = TemplateSendMessage(alt_text='Carousel alt text', template=carousel_template, quick_reply=QuickReply(items=[QuickReplyButton(action=MessageAction(label="完了", text="完了")),QuickReplyButton(action=MessageAction(label="戻る", text="戻る"))]))
    line_bot_api.push_message(event.source.user_id, template_message)

# お惣菜1袋50ｇ 約一人前 3
def submenu4(event):
    れんこんキンピラ = request.url_root + '/static/れんこんキンピラ.JPG'
    ひじきの炒め煮 = request.url_root + '/static/ひじきの炒め煮.JPG'
    高菜のじゃこ炒め = request.url_root + '/static/高菜のじゃこ炒め.JPG'
    carousel_template = CarouselTemplate(columns=[
        CarouselColumn(text=format(getpricebyname('れんこんキンピラ'),',d'), title='れんこんキンピラ',
                       thumbnail_image_url=れんこんキンピラ, actions=[PostbackAction(label='カートに追加', data='れんこんキンピラ')]),
        CarouselColumn(text=format(getpricebyname('ひじきの炒め煮'),',d'), title='ひじきの炒め煮',
                       thumbnail_image_url=ひじきの炒め煮, actions=[PostbackAction(label='カートに追加', data='ひじきの炒め煮')]),
        CarouselColumn(text=format(getpricebyname('高菜のじゃこ炒め'),',d'), title='サケ切り身',
                       thumbnail_image_url=高菜のじゃこ炒め, actions=[PostbackAction(label='カートに追加', data='高菜のじゃこ炒め')]),
    ])
    template_message = TemplateSendMessage(alt_text='Carousel alt text', template=carousel_template, quick_reply=QuickReply(items=[QuickReplyButton(action=MessageAction(label="完了", text="完了")),QuickReplyButton(action=MessageAction(label="戻る", text="戻る"))]))
    line_bot_api.reply_message(event.reply_token, template_message)

def showsubmenu(event):
    buttons_template = ButtonsTemplate(text='品種を選択してください。', actions=[
            MessageAction(label='生鮮食品', text='生鮮食品'),
            MessageAction(label='お潰物・サラダ他 ', text='お潰物・サラダ他-約一人前'),
            MessageAction(label='お惣菜', text='お惣菜1袋50ｇ-約一人前'),
            MessageAction(label='一品物', text='一品物')
        ])
    template_message = TemplateSendMessage(
        alt_text='Buttons alt text', template=buttons_template)
    line_bot_api.push_message(event.source.user_id, template_message)


def chonsoluong(event,name):
    row = None
    try:
        cell = tmpordersheet.find(str(event.source.user_id))
        row = cell.row
    except :
        tmpordersheet.insert_row([str(event.source.user_id)])
        cell = tmpordersheet.find(str(event.source.user_id))
        row = cell.row
    if not row == None:

        tmpordersheet.update_cell(row,2,name)
        buttons_template = ButtonsTemplate(title=name, text='数量を選択してください。', actions=[
            MessageAction(label='1', text='1'),
            MessageAction(label='2', text='2'),
            MessageAction(label='3', text='3'),
            PostbackAction(label='数量を入力', data='nhapsoluong')
        ])
        template_message = TemplateSendMessage(
            alt_text='Buttons alt text', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)
def showitemsincart(event):
    cell_listo = []
    tmp = tmpordersheet.find(str(event.source.user_id))
    cell_list = tmpordersheet.range('C' + str(tmp.row) + ':ZZ' + str(tmp.row))
    for cell in cell_list:
        if not cell.value == '':
            cell_listo.append(cell.value)
    line_bot_api.reply_message(event.reply_token,
                               TextSendMessage(text=getorderfromlist(cell_listo), quick_reply=QuickReply(
                                   items=[QuickReplyButton(action=MessageAction(label="完了", text="完了")), QuickReplyButton(action=MessageAction(label='戻る', text='戻る'))])))
#  カートに追加 and handle Post back event
@handler.add(PostbackEvent)
def handle_postback(event):
    # sub1
    if event.postback.data == 'サンマの開き':
        chonsoluong(event,'サンマの開き')
    if event.postback.data == 'nhapsoluong':
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='数量を入力してください。'))
        # addtocart(event, "サンマの開き")
        # showitemsincart(event)
    elif event.postback.data == '塩サバ切り身':
        chonsoluong(event,'塩サバ切り身')
    elif event.postback.data == 'サケ切り身':
        chonsoluong(event,'サケ切り身')
    elif event.postback.data == 'サワラの味噌漬け':
        chonsoluong(event,'サワラの味噌漬け')
    # sub2
    elif event.postback.data == '紅茶豚（スライス５枚）':
        chonsoluong(event,'紅茶豚（スライス５枚）')
    elif event.postback.data == '手作り-冷凍餃子':
        chonsoluong(event,'手作り-冷凍餃子')
    elif event.postback.data == '砂肝にんにく炒め':
        chonsoluong(event,'砂肝にんにく炒め')

    elif event.postback.data == 'ハンバーグ（ソース付）':
        chonsoluong(event,'ハンバーグ（ソース付）')
    elif event.postback.data == 'エビチリ':
        chonsoluong(event,'エビチリ')
    elif event.postback.data == 'サバの味噌煮':
        chonsoluong(event,'サバの味噌煮')

    elif event.postback.data == '豚生姜焼き':
        chonsoluong(event,'豚生姜焼き')
    elif event.postback.data == 'レバニラ炒め':
        chonsoluong(event,'レバニラ炒め')
    elif event.postback.data == '手羽醤油焼き':
        chonsoluong(event,'手羽醤油焼き')
    elif event.postback.data == '中華丼（ソースのみ）':
        chonsoluong(event,'中華丼（ソースのみ）')
    #     sub3
    elif event.postback.data == '野菜サラダ':
        chonsoluong(event,'野菜サラダ')
    #      sub4
    elif event.postback.data == 'れんこんキンピラ':
        chonsoluong(event,'れんこんキンピラ')
    elif event.postback.data == 'ひじきの炒め煮':
        chonsoluong(event,'ひじきの炒め煮')
    elif event.postback.data == '高菜のじゃこ炒め':
        chonsoluong(event,'高菜のじゃこ炒め')
    elif event.postback.data == 'datetime':
        datetime= str(event.postback.params['datetime'])
        row = str(tmpuserinfo.find(str(event.source.user_id)).row)
        tmpuserinfo.update_cell(row, 6, datetime)
        line_bot_api.reply_message(event.reply_token,[
                                   TextSendMessage(text='ご希望の配達日時は'+datetime +'ですね。'),
                                    TextSendMessage(text='その他特別な要求がありますか？')])
    elif getnums(event.postback.data) == '1':
        addtocart(event, getchars(event.postback.data),1)
        showitemsincart(event)
    elif getnums(event.postback.data) == '2':
        addtocart(event, getchars(event.postback.data),2)
        showitemsincart(event)
    elif getnums(event.postback.data) == '3':
        addtocart(event, getchars(event.postback.data),3)
        showitemsincart(event)
    elif getnums(event.postback.data) == '4':
        addtocart(event, getchars(event.postback.data),4)
        showitemsincart(event)
    elif getnums(event.postback.data) == '5':
        addtocart(event, getchars(event.postback.data),5)
        showitemsincart(event)
    elif getnums(event.postback.data) == '6':
        addtocart(event, getchars(event.postback.data),6)
        showitemsincart(event)
    elif getnums(event.postback.data) == '7':
        addtocart(event, getchars(event.postback.data),7)
        showitemsincart(event)
    elif getnums(event.postback.data) == '8':
        addtocart(event, getchars(event.postback.data),8)
        showitemsincart(event)
    elif getnums(event.postback.data) == '9':
        addtocart(event, getchars(event.postback.data),9)
        showitemsincart(event)
    elif getnums(event.postback.data) == '10':
        addtocart(event, getchars(event.postback.data),10)
        showitemsincart(event)

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    address = str(event.message.address)
    row = str(tmpuserinfo.find(str(event.source.user_id)).row)
    tmpuserinfo.update_cell(row, 4, address)
    line_bot_api.reply_message(event.reply_token, [
        TextSendMessage(text='住所は'+ address+'ですね。' ),
        TextSendMessage(text='マンション名を教えてください。')])
def addtocart(event,name,num):
    # tmp = None
    x = 0
    try:
        tmp = tmpordersheet.find(str(event.source.user_id))
    except:
        tmp = None
    if tmp is None:
        renew = [str(event.source.user_id), name]
        tmpordersheet.insert_row(renew)
    else:
        row = tmp.row
        listoftmporder = tmpordersheet.row_values(row)
        for i in range(num):
            listoftmporder.append(name)
        print(listoftmporder)
        tmpordersheet.delete_row(row)
        tmpordersheet.insert_row(listoftmporder)

def getsubmenubyname(name):
    if name == 'サンマの開き':
        return 1
    elif name == '塩サバ切り身':
        return 1
    elif name == 'サケ切り身':
        return 1
    elif name == 'サワラの味噌漬け':
        return 1
    elif name == '野菜サラダ':
        return 2
    elif name == 'れんこんキンピラ':
        return 3
    elif name == 'ひじきの炒め煮':
        return 3
    elif name == '高菜のじゃこ炒め':
        return 3
    elif name == '紅茶豚（スライス５枚）':
        return 4
    elif name == '手作り冷凍餃子（５個）':
        return 4
    elif name == '砂肝にんにく炒め':
        return 4
    elif name == 'ハンバーグ（ソース付）':
        return 4
    elif name == 'エビチリ':
        return 4
    elif name == 'サバの味噌煮':
        return 4
    elif name == '豚生姜焼き':
        return 4
    elif name == 'レバニラ炒め':
        return 4
    elif name == '手羽醤油焼き':
        return 4
    elif name == '中華丼（ソースのみ）':
        return 4

def isnumber(list):
    a = True
    for n in list:
        if not n.isdigit():
            a = False
    return a
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    if text== 'getid':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.source.user_id))

    elif text == 'レストラン予約':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="開発中のこの機能"))
    elif text == '食材・弁当デリバリー':
        clearorder(event)
        showsubmenu(event)
    elif text == '戻る':
        showsubmenu(event)
    elif text == '生鮮食品':
        submenu1(event)
    elif text=='一品物':
        submenu2(event)
    elif text == 'お潰物・サラダ他-約一人前':
        submenu3(event)
    elif text == 'お惣菜1袋50ｇ-約一人前':
        submenu4(event)
    elif text == 'お問合せ':
        clearorder(event)
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(
                    text='・居酒屋「くーろん」 \n・原田商店 \n \n 63 Pham Viet Chanh street.,District Binh Thanh,Ho Chi Minh \n \n TEL：0838409826 \n 携帯：0908295470')
            ]
        )
    elif text == 'メニュー':
        menu = request.url_root + '/static/menu.jpg'
        rszmenu = request.url_root + '/static/rsz_menu.jpg'
        line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(menu, rszmenu)
        )
    elif text == '営業時間':
        clearorder(event)
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text='【レストラン】 \n月曜日　17:30～23:00 \n火曜日　17:30～23:00 \n水曜日　17:30～23:00 \n木曜日　17:30～23:00 \n金曜日　17:30～23:00 \n土曜日　11:30～23:00 \n日曜日　定休日\n \n 【食材・弁当デリバリー】 \n配達希望日の前日午前3時までの受付になります。 \n食材のみのデリバリーは14時以降の配達です。' ),
            ]
        )
    elif text == '完了':
        try:
            tmp = tmpordersheet.find(str(event.source.user_id))
            tmpordersheet.update_cell(tmp.row,2,'')
        except:
            tmp = None
        if tmp is None:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='あなたのカートは空です'))
        else :
            try:
                tmp2 = tmpuserinfo.find(str(event.source.user_id))
                tmpuserinfo.delete_row(tmp2.row)
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='お名前を教えてください。?'))
                new = [str(event.source.user_id), ""]
                tmpuserinfo.insert_row(new)
            except:
                tmp2 = None
            if tmp2 is None :
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text='お名前を教えてください。?'))
                new = [str(event.source.user_id), ""]
                tmpuserinfo.insert_row(new)
    elif isnumber(text) == True and checker(event) == True:
        cell = tmpordersheet.find(str(event.source.user_id))
        row = cell.row
        if not tmpordersheet.cell(row,2).value == None:
            name = str(tmpordersheet.cell(row,2).value)
            addtocart(event,name,int(text))
            showitemsincart(event)
            if getsubmenubyname(name) == 1:
                submenu1(event)
            if getsubmenubyname(name) == 2:
                submenu3(event)
            if getsubmenubyname(name) == 3:
                submenu4(event)
            if getsubmenubyname(name) == 4:
                submenu2(event)
    elif 1==1:
        getUserinfo(event)
# check if user is typing info
def checker(event):
    t = None
    try:
        t = tmpuserinfo.find(str(event.source.user_id))
    except :
        print('')
    if t == None:
        return True
    return False


import os

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
