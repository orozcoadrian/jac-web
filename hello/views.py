import requests
from django.shortcuts import render
from django.http import HttpResponse
import pprint
from .models import Greeting

from bs4 import BeautifulSoup
import re

head_str = '''
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
    <meta name="Author" content="mypage">
    <style type="text/css">
    BODY {
    text-align: Left;
    background-color: #FFFFFF;
    }
    TH {
    text-align: Center;
    background-color: #8282FF;
    color: #FFFFFF;
    }
    .oddrows {
    text-align: Left;
    background-color: #FFFFFF;
    color: #0;
    }
    .evenrows {
    text-align: Left;
    background-color: #FFFFBF;
    color: #0;
    }
    
    </style>
    <title></title>
    </head>
    <body>
    '''

orig_mtg_cache = {}

def get_display_html_for_cn(cn_str, fetch_if_not_cache=False):
    print('get_display_html_for_cn:'+'cn_str='+str(cn_str)+'; fetch_if_not_cache='+str(fetch_if_not_cache))
    if fetch_if_not_cache:
        print('get_display_html_for_cn#1')
        orig_mrg_str = str(get_orig_mortgage_url_by_cn(cn_str))
        orig_mtg_cache[cn_str] = orig_mrg_str
        return '<a href="'+orig_mrg_str+'"  target="_blank">'+cn_str+'</a>'
    elif cn_str in orig_mtg_cache:
        print('get_display_html_for_cn#2')
        if 'None' not in orig_mtg_cache[cn_str]:
            return '<a href="'+orig_mtg_cache[cn_str]+'"  target="_blank">'+'open'+'</a>'
        else:
            return 'error'

    else:
        print('get_display_html_for_cn#3')
        return '<form action="." method="post"><div><button name="fetch_field" type="submit" value="'+cn_str+'">fetch</button></div></form>'

def get_rows(the_html):
    rows = []
    soup = BeautifulSoup(the_html)
    # print(soup.prettify())
    trs = soup.find_all("tr")
    for tr in trs:
        # print(tr)
        current_row = {}
        tds = tr.find_all('td')
        if len(tds) == 0:
            continue
        # print(tds)
        current_row['case_number'] = tds[0].string
        current_row['case_title'] = tds[1].string
        current_row['comment'] = tds[2].string.replace(u'\xa0', u'').encode('utf-8')
        current_row['foreclosure_sale_date'] = tds[3].string
        current_row['count'] = len(rows) + 1
        rows.append(current_row)
    #   if len(rows) > 4:
    #break
    # pprint.pprint(rows)
    return rows

def get_items():
    r = requests.get('http://vweb2.brevardclerk.us/Foreclosures/foreclosure_sales.html')
    return get_rows(r.content)

def get_case_number_url(cn):
    return 'http://web1.brevardclerk.us/oncoreweb/search.aspx?bd=1%2F1%2F1981&ed=5%2F31%2F2015&n=&bt=OR&d=5%2F31%2F2014&pt=-1&cn='+cn+'&dt=ALL%20DOCUMENT%20TYPES&st=casenumber&ss=ALL%20DOCUMENT%20TYPES'

def get_items_html(request):
    #r = requests.get('http://vweb2.brevardclerk.us/Foreclosures/foreclosure_sales.html')
    #return get_rows(r.content)
    to_fetch = []
    for k,v in request.POST.items():
        #field_item = request.GET.get(field.key)
        #print(field_item)
        # file_data = field_item.file.read()
        print(str(k) + ' -> ' + str(v))
        if 'fetch_field' in str(k):
            cn_str = str(v)
            #html+=get_display_html_for_cn(cn_str, fetch_if_not_cache=True)
        if 'XXXX' in str(v):
            to_fetch.append(str(v))
    print(to_fetch)
    for cn_str in to_fetch:
        get_display_html_for_cn(cn_str, fetch_if_not_cache=True) # todo: refactor so that only a fill_cache() function is called here.



    f_items = get_items()
    html='''
    <html>
    hi ''' + str(len(f_items))+ ''' ''' + str(f_items) + '''
        </html>
        '''
    html='<html>'
    html=head_str
    html+='brevardclerk.us:<br><a href="http://vweb2.brevardclerk.us/Foreclosures/foreclosure_sales.html">Foreclosure Sale List</a>'
    html+='<br>'
    html+='items num: ' + str(len(f_items))
    html+='<tr>'
    html+='<table border=2 cellpadding=2 cellspacing=1>'
    html+='<tr>'
    html+='<th>select</th>'
    html+='<th>case_number</th>'
    html+='<th>case_title</th>'
    html+='<th>comment</th>'
    html+='<th>foreclosure_sale_date</th>'
    html+='<th>orig mtg</th>'#<th><form action="." method="post"><div><input type="submit" value="orig mtg"></div></form</th>'
    html+='</tr>'
    for i,fi in enumerate(f_items):
        class_str = 'evenrows' if i % 2 != 0 else 'oddrows'
        html+='<tr>'
        html+='<td class="'+class_str+' '+'center'+'"><input type="checkbox"></td>'
        html+='<td class='+class_str+'><a href="'+get_case_number_url(fi['case_number'])+'">'+fi['case_number']+'</a></td>'
        html+='<td class='+class_str+'>'+fi['case_title']+'</td>'
        html+='<td class='+class_str+'>'+fi['comment']+'</td>'
        html+='<td class='+class_str+'>'+fi['foreclosure_sale_date']+'</td>'
        html+='<td class="'+class_str+'">'+get_display_html_for_cn(fi['case_number'])+' </td>'
        html+='</tr>'
    html+='</table>'
    html+='</body>'
    html+='</html>'
    print(html)
    return html

# Create your views here.
def index(request):
    # return HttpResponse('Hello from Python!')
    #return render(request, 'index.html')
    r = requests.get('http://httpbin.org/status/418')
    print r.text
    return HttpResponse('<pre>' + r.text + '</pre>')

def adrian(request):
    # return HttpResponse('Hello from Python!')
    #return render(request, 'index.html')
    
    #print(get_items())
    
    #r = requests.get('http://vweb2.brevardclerk.us/Foreclosures/foreclosure_sales.html')
    #print r.text
    print('hi')
    print(request.method)
    if request.method == 'GET':
        print(request.GET)
    if request.method == 'POST':
        print(request.POST)
    return HttpResponse(get_items_html(request))

def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})










def get_orig_mortgage_url_by_cn(cn):
    ######## try to get both latest amount due as well as orig mtg from a single fetch of reg of actions
    g = reg_actions_grid_by_cn(cn)
    #     print('='*80)
    ret = get_orig_mortgage_url_from_grid(g)
    return ret

def get_orig_mortgage_url_from_grid(g):
    ret = None
    valid_patterns_for_original_mortgage = ['OR MTG', 'MTG & ORIG', 'COPY OF MTG', 'ORIGINAL NOTE & MORTGAGE DEED', 'ER: F/J FCL']
    #     for i in g['items']:
    # #         pprint.pprint(i)
    # #         if 'Description' in i and ('OR MTG' in i['Description'] or 'MTG & ORIG' in i['Description'] or 'COPY OF MTG' in i['Description']):
    #         if 'Description' in i and any(x in i['Description'] for x in valid_patterns_for_original_mortgage):
    #             if i['Img']:
    #                 ret = i['Img']
    for x in valid_patterns_for_original_mortgage:
        ret = get_orig_mortgage_url_from_grid2(g, x)
        if ret:
            break

    return ret

def get_orig_mortgage_url_from_grid2(g, a_pattern):
    ret = None
    for i in g['items']:
        #         pprint.pprint(i)
        #         if 'Description' in i and ('OR MTG' in i['Description'] or 'MTG & ORIG' in i['Description'] or 'COPY OF MTG' in i['Description']):
        if 'Description' in i and a_pattern in i['Description']:
            if i['Img']:
                ret = i['Img']
                break
    return ret

def reg_actions_grid_by_cn(cn):
    cn_fields = get_case_number_fields(cn)
    return reg_actions_grid(cn_fields['year'], cn_fields['court_type'], cn_fields['seq_number'])

def get_case_number_fields(case_number):
    m = re.search('(.*)-(.*)-(.*)-(.*)', case_number.replace('-XXXX-XX',''))
    if m:
        # print(m.group(1)+','+m.group(2))
        print(m.groups())
        ret = {}
        ret['year'] = m.group(2)
        ret['court_type'] = m.group(3)
        ret['seq_number'] = m.group(4)
        return ret

def reg_actions_grid(year, court_type, seq_number):
    
    case_info_grid(year, court_type, seq_number) # have only been able to make reg work after case_info
    
    r_text = get_reg_actions_text(year, court_type, seq_number)
    ret = get_reg_actions_dataset(r_text)
    return ret

def case_info_grid(year, court_type, seq_number):
    cfid = '1550556'
    cftoken = '74317641'
    id2 = year+'_'+court_type+'_'+seq_number
    # print('case_info('+id+')')
    url = get_url()
    headers=get_headers(cfid, cftoken)
    data=get_data(year, court_type, seq_number)
    #     r = requests.post(url, data, headers=headers, stream=True)
    r = requests.post(url, data, headers=headers, stream=True)
    soup = BeautifulSoup(r.text.encode('utf-8'), 'html.parser')
#     print(soup.prettify())

def get_url():
    return 'https://vweb1.brevardclerk.us/facts/d_caseno.cfm'

def get_reg_actions_text(year, court_type, seq_number):
    url = 'https://vweb1.brevardclerk.us/facts/d_reg_actions.cfm'
    cfid = '1550556'
    cftoken = '74317641'
    headers = get_headers(cfid, cftoken)
    data = get_data(year, court_type, seq_number)
    #     r = requests.post(url, data, headers=headers, stream=True)
    r = requests.post(url, data, headers=headers, stream=True)
    r_text = r.text
    return r_text

def get_reg_actions_dataset(r_text):
    #     print(r_text[0:len(r_text)/2])
    #     soup = BeautifulSoup(r_text)
    #     soup = BeautifulSoup(r_text.encode('utf-8'), 'html.parser')
    soup = BeautifulSoup(r_text.encode('utf-8'))
    # print soup.prettify()
    #     print('case number: ' + soup.title.text)
    #     print('case title: ' + soup.find_all('font', color='Blue')[0].text)
    ret = {}
    ret['case number'] = soup.title.text
    ret['case title'] = soup.find_all('font', color='Blue')[0].text
    #     print(soup.find_all('table')[1].find_all('tr'))
    items = []
    col_names = []
    trs = soup.find_all('table')[1].findAll("tr")
    for row, a in enumerate(trs):
        #print 'r' + str(row) + '===' + str(a).replace("\n", "").replace("\r", "").replace("\t", "")
        current_item = {}
        for h_index, h_text in enumerate(a.findAll("th")):
            #             print ' h_index' + str(h_index) + '===' + str(h_text).replace("\n", "").replace("\r", "").replace("\t", "")
            col_names.append(h_text.text)
    
        for c, d in enumerate(a.findAll("td")):
            #             print ' c' + str(c) + '===' + str(d).replace("\n", "").replace("\r", "").replace("\t", "")
            the_a = None
            try:
                current_item[col_names[c]] = d.text
                the_a = d.find('a')
                if the_a:
                    current_item[col_names[c]] = the_a['href']
            except (IndexError, KeyError) as error:
                logging.debug(' '.join(['********exception******', str(error), str(sys.exc_info()[0]), str(col_names), str(d)]))
#                 logging.exception(error)

        if row >= 1:
            items.append(current_item)

    #     pprint.pprint(items)
    ret['items'] = items
    return ret

def get_data(year, court_type, seq_number):
    return 'CaseNumber1=05&CaseNumber2=' + year + '&CaseNumber3=' + court_type + '&CaseNumber4=' + seq_number + '&CaseNumber5=&CaseNumber6=&submit=Submit'

def get_headers(cfid, cftoken):
    return {
        'Cookie':'CFID=' + cfid + '; CFTOKEN=' + cftoken,
        'Content-Type':'application/x-www-form-urlencoded'}
