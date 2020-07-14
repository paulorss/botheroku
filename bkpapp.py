from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import re
import nltk
from newspaper import Article
from googlesearch import search

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    msg = userText
    entrada = str(msg).lower()
    p1 = 'http://receita.economia.gov.br/@@busca?advanced_search=False&sort_on=&SearchableText='
    p2 = '&portal_type%3Alist=Document&created.query%3Arecord%3Alist%3Adate=1970-01-02&created.range%3Arecord=min'
    html = str(p1 + entrada + p2)
    stop2 = nltk.corpus.stopwords.words('portuguese')
    stop2.append('faço')
    stop2.append('um')
    stop2.append('gostaria')
    stop2.append('fazer')
    stop2.append('saber')
    stop2.append('posso')
    stop2.append('como')
    splitter = re.compile('\\W+')
    lista_palavras = []
    lista = [p for p in splitter.split(entrada) if p != '']
    for p in lista:
        if p not in stop2:
            if len(p) > 1:
                lista_palavras.append(p)
    ar = len(lista_palavras)
    ax = str(lista_palavras[0:ar])
    e = str(ax).replace(',', ' ').strip('[]')
    e.strip("'")
    page = requests.get(html)
    soup = BeautifulSoup(page.content, 'lxml')
    cla = soup.find(class_='searchResults')
    links = cla.find_all('a')
    namess = soup.find_all('a')
    ra = (lista_palavras)
    # CRIAR A LISTA DE LINKS SITE RFB
    list = []
    for link in links:
        texto = str(link.get_text()).lower().replace('ã', 'a').replace('-', ' ').replace('ç', 'c').split()
        #print(len(texto))
        url = str(link.get('href'))
        #print(len(url))
        urls = str(link.get('href')).lower().replace('/', ' ').replace('-', ' ').replace('.', ' ').split()
        #print(len(urls))
        if entrada in texto:
            list.append(url)
        for i in range(0, ar):
            if lista_palavras[i] in texto:
                list.append(url)
            elif lista_palavras[i] in urls:
                list.append(url)

    listag = []
    rec = 'site:receita.economia.gov.br intitle:' + msg
    for urla in search(rec, tld='com.br', lang='pt-br', stop=3, pause=2):
        listag.append(urla)
    
    g = int(len(listag))
    #print(g)

    listago = []
    for z in range(0, g):
        ur = str(listag[z])
        listago.append(ur)
    
    #print(listago)
    #print(len(listago))
    qo = int(len(listago))
    #print(list)
    #print(len(list))
    conj=set(list + listago)
    #print(conj)
    #print(len(conj))
    #print(type(conj))

    s = conj
    p = []
    for m in s:
        p.append(m)

    #print(p)
    #print(len(p))
    j = len(p)

    reports2 = []
    for r in range(0, j):
        ia = str(p[r])
        article = Article(ia, language="pt")
        article.download()
        article.parse()
        article.text
        article.nlp()
        reports2.append(str(article.text).replace('\n', ' '))
    #print(len(reports2))

    resposta_final = (str(reports2).replace('\n', ' ').replace('[', ' ').replace(']', ' ').replace(',', ' ').replace("'", '').replace('"', ' ').replace('{', ' ').replace("}", ' '))

    return str(resposta_final)

if __name__ == "__main__":
    app.run()
