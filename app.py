# -*- coding: utf-8 -*-
import unidecode
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.logic import LogicAdapter
from chatterbot.response_selection import get_first_response
from chatterbot.comparisons import levenshtein_distance
from chatterbot.response_selection import *  # get_first_response
from chatterbot.comparisons import *  # levenshtein_distance
from chatterbot import *
import csv
import json
import sys
import os
from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import re
import nltk
from newspaper import Article
from newspaper import news_pool
from googlesearch import search
import wikipedia
from logging import *
import logging
import urllib3
import sys
from chatterbot.adapters import Adapter
from chatterbot.storage import StorageAdapter
from chatterbot.search import IndexedTextSearch
from chatterbot.conversation import Statement



logging.basicConfig(filename="Log_Test_File.txt", level=logging.INFO, filemode='a')

app = Flask(__name__)

searchbot = ChatBot(
    "Chatterbot",
    input_adapter="chatterbot.input.VariableInputTypeAdapter",
    output_adapter="chatterbot.output.OutputAdapter",
    #storage_adapter="chatterbot.storage.MongoDatabaseAdapter",
    # filters=[get_recent_repeated_responses],
    preprocessors=[
        'chatterbot.preprocessors.clean_whitespace',
        'chatterbot.preprocessors.convert_to_ascii'
        #'custom_preprocessors.PreprocessorCustom1'
    ],
    logic_adapters=[
        {
            'import_path': "chatterbot.logic.BestMatch",
            'statement_comparison_function': JaccardSimilarity,
            'response_selection_method': get_first_response,
        },
        {
            'import_path': 'chatterbot.logic.SpecificResponseAdapter',
            'input_text': 'teste especial',
            'output_text': 'Ok, here is a link: http://chatterbot.rtfd.org'
        },
        {
            'import_path': "chatterbot.logic.BestMatch",
            'statement_comparison_function': "chatterbot.comparisons.Comparator",
            'response_selection_method': get_first_response,

        },
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'response_selection_method': get_first_response,
            'statement_comparison_function': levenshtein_distance,
            # 'statement_comparison_function': "ChatBot.comparisons.Comparator",
            # 'statement_comparison_function': "chatterbot.comparisons.SynsetDistance",
            #'statement_comparison_function': SentimentComparison,
            # 'statement_comparison_function': "chatterbot.comparisons.JaccardSimilarity",
            #'default_response': 'Desculpe, não compreendi a pergunta! Poderia informar o assunto desejado?',
            #'maximum_similarity_threshold': 0.5
        },
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'response_selection_method': get_first_response,
            #'statement_comparison_function': "ChatBot.comparisons.levenshtein_distance",
            # 'statement_comparison_function': "ChatBot.comparisons.Comparator",
            'statement_comparison_function': SynsetDistance,
            # 'statement_comparison_function': SentimentComparison,
            # 'statement_comparison_function': "chatterbot.comparisons.JaccardSimilarity",
            #'default_response': 'Desculpe, não compreendi a pergunta! Poderia informar o assunto desejado?',
            #'maximum_similarity_threshold': 0.5
        },
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'response_selection_method': get_most_frequent_response,
            # 'statement_comparison_function': "ChatBot.comparisons.levenshtein_distance",
            # 'statement_comparison_function': "ChatBot.comparisons.Comparator",
            # 'statement_comparison_function': "chatterbot.comparisons.SynsetDistance",
            'statement_comparison_function': SentimentComparison,
            #'statement_comparison_function': JaccardSimilarity,
            #'default_response': 'Desculpe, não compreendi a pergunta! Poderia informar o assunto desejado?',
            #'maximum_similarity_threshold': 0.5,
            # 'search_algorithm_name': jaccard_similarity,
        },
        'chatterbot.logic.BestMatch'
        #JaccardSimilarity,
        #'chatterbot.get_most_frequent_response',
        #'chatterbot.logic.TimeLogicAdapter',
        #'chatterbot.logic.MathematicalEvaluation'
        #

    ],
    storage_adapter="chatterbot.storage.MongoDatabaseAdapter",
    #database='heroku_t1jjs2t8',
    database_uri="mongodb://heroku_t1jjs2t8:hkvs6ok11go5kam96evri3p22a@ds041536.mlab.com:41536/heroku_t1jjs2t8?retryWrites=false&w=majority"
    #database_uri="mongodb+srv://P15l4r4b2rt4:<password>@botheroku.j2haj.gcp.mongodb.net/<dbname>?retryWrites=false&w=majority"
    #database_uri='sqlite:///database.db',
    # statement_comparison_function=levenshtein_distance,
    # response_selection_method=get_first_response
    read_only=True
)


trainer = ListTrainer(searchbot)

conv = open('chats.csv', encoding='utf-8').readlines()
#convex = open('export.json').readlines()

trainer.train(conv)
#trainer.train(convex)
# trainer.train(convirpf)
# trainer.train(convcpf)

trainer.export_for_training('./export.json')


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/get")
# function for the bot response
def get_bot_response():
    while True:
        userText = request.args.get('msg')
        msg = str(userText)
        entrada = msg.lower()
        f = csv.writer(open('inputs.csv', 'a', encoding='utf-8'))
        f.writerow([msg])
        response = searchbot.get_response(userText)
        if float(response.confidence) >= 0.6:
            return str(searchbot.get_response(userText))
        elif float(response.confidence) == 0.0:
            entrada = msg
            # print(entrada)
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
            headers = {'User-Agent': 'Mozilla/5.0'}
            page = requests.get(html, headers=headers, verify=False, stream=False, timeout=7)
            soup = BeautifulSoup(page.content, 'lxml')
            cla = soup.find(class_='searchResults')
            links = cla.find_all('a')
            # namess = soup.find_all('a')
            # ra = (lista_palavras)
            # CRIAR A LISTA DE LINKS SITE RFB
            listr = []
            for link in links:
                texto = str(link.get_text()).lower().replace('ã', 'a').replace('-', ' ').replace('ç', 'c').split()
                # print(len(texto))
                url = str(link.get('href'))
                # print(len(url))
                urls = str(link.get('href')).lower().replace('/', ' ').replace('-', ' ').replace('.', ' ').split()
                # print(len(urls))
                if entrada in texto:
                    listr.append(url)
                for i in range(0, ar):
                    if lista_palavras[i] in texto:
                        listr.append(url)
                    elif lista_palavras[i] in urls:
                        listr.append(url)

            listag = []
            rec = 'site:receita.economia.gov.br intitle:' + msg + " -filetype:pdf -.pdf"
            for urla in search(rec, tld='com.br', lang='pt-br', stop=4, pause=7):
                listag.append(urla)

            g = int(len(listag))
            # print(g)

            listago = []
            for z in range(0, g):
                ur = str(listag[z])
                listago.append(ur)

            # print(listago)
            # print(len(listago))
            qo = int(len(listago))
            # print(listr)
            # print(len(listr))
            listaunida = listago #+ listr
            conj = list(set(listaunida))
            # print(conj)
            # print(len(conj))
            # print(type(conj))

            # print(p)
            # print(len(p))
            j = len(conj)

            reports2 = []
            # news_pool.set(reports2)#, threads_per_source=2)
            # news_pool.join()
            for r in range(0, j):

                try:
                    ia = str(conj[r])
                    article = Article(ia, language="pt")
                    article.download()
                    article.parse()
                    article.text
                    article.nlp()
                    article.summary
                except:
                    pass
                reports2.append(str(article.summary).replace('\n', ' '))
            # print(len(reports2))

            resposta_finalc = set(reports2)
            print(resposta_finalc)

            if resposta_finalc == set():
                wikipedia.set_lang("pt")
                a = msg
                result = wikipedia.search(a, results=1)
                page = wikipedia.summary(result, sentences=5)
                content = page
                return str(content)
            else:
                resposta_final = (str(resposta_finalc).replace('\n', ' ').replace('[', ' ').replace(']', ' ').replace(',', ' ').replace("'", ' ').replace('{', ' ').replace("}", ' '))

                f = csv.writer(open('chats.csv', 'a', encoding='utf-8'))
                f.writerow([msg + '\n' + resposta_final])
                return str(resposta_final + '\n' + 'Ficou satisfeito com a resposta?')




            # return str(resposta_final)


if __name__ == '__main__':
    app.run()
