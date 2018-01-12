import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from lxml import html
import requests

import pretty

tree_elibrary = ET.parse('elibrary.xml')
root_elib = tree_elibrary.getroot()

tree_doaj = ET.parse('doaj.xml')
root_doaj = tree_doaj.getroot()

ici_import = ET.Element('ici-import')
ici_import.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')

journal = ET.SubElement(ici_import, 'journal')
issn = root_elib.find('issn').text
journal.set('issn', issn)

xml_issue = ET.SubElement(ici_import, 'issue')
issue = root_elib.find('issue')
number = issue.find('number').text
xml_issue.set('number', number)
volume = issue.find('volume').text
xml_issue.set('volume', volume)
year = issue.find('dateUni').text.split('/')[1]
xml_issue.set('year', year)
coverDate = root_doaj[0].find('publicationDate').text
xml_issue.set('coverDate', coverDate)
publicationDate = coverDate + 'T23:24:59'
xml_issue.set('publicationDate', publicationDate)
coverURL = ''  # for_ref
xml_issue.set('coverUrl', coverURL)
fullPdfURL = ''
xml_issue.set('electronicContentPdfUrl', fullPdfURL)
numberOfArticles = root_elib[0].find('cntArticle').text
xml_issue.set('numberOfArticles', numberOfArticles)

type_of_article = 'ORIGINAL_ARTICLE'

# # parse ojs page with files
# page = requests.get('http://journals.uran.ua/swonaft/issue/view/2374/showToc')
# ojs_tree = html.fromstring(page.content)
#
# # file = BeautifulSoup(page.content, 'html.parser')
# file = ojs_tree.xpath("//table")
# print(file)

articles = []
for i, article in enumerate(issue.find('articles').iter('article')):
    articles.append({})
    articles[i]['type'] = type_of_article
    articles[i]['languageVersion'] = {'language': article.find('text').attrib['lang'].lower()[:-1]}
    title = article.find('artTitles')[0].text
    articles[i]['languageVersion']['title'] = title
    articles[i]['languageVersion']['abstract'] = article.find('abstracts')[0].text
    articles[i]['languageVersion']['publicationDate'] = publicationDate
    articles[i]['languageVersion']['registrationDate'] = publicationDate
    pages = article.find('pages').text.split('-')
    articles[i]['languageVersion']['pageFrom'] = pages[0]
    articles[i]['languageVersion']['pageTo'] = pages[1]
    authors = []
    for author in article.find('authors'):
        au = {}
        for a in author:
            au['order'] = author.attrib['num'][-1:]
            au['surname'] = a.find('surname').text
            name = a.find('initials')
            au['name'] = '' if name is None else name.text
            au['institute'] = a.find('orgName').text
            email = a.find('email')
            au['email'] = '' if email is None else email.text
        authors.append(au)
    articles[i]['authors'] = authors
    ref = []
    references = article.find('references')
    if references is not None:
        for reference in references:
            ref.append(reference.text[3:].lstrip())
    articles[i]['references'] = ref
    # select keywords
    keywords = []
    keyword = article.find('keywords')
    if keyword is not None:
        for key in keyword[0]:
            keywords.append(key.text)
    articles[i]['languageVersion']['keywords'] = keywords
    pdfFileUrl = None
    doi = None
    for record in root_doaj:
        if record.find('title').text == title:
            pdfFileUrl = record.find('fullTextUrl').text
            doi = record.find('doi').text
    articles[i]['languageVersion']['pdfFileURL'] = '' if pdfFileUrl is None else pdfFileUrl
    articles[i]['languageVersion']['doi'] = '' if doi is None else doi

for ar in articles:
    xml_article = ET.SubElement(xml_issue, 'article')
    xml_type = ET.SubElement(xml_article, 'type')
    xml_type.text = ar['type']
    xml_languageVersion = ET.SubElement(xml_article, 'languageVersion')
    xml_languageVersion.set('language', ar['languageVersion']['language'])
    xml_title = ET.SubElement(xml_languageVersion, 'title')
    xml_title.text = ar['languageVersion']['title']
    xml_abstract = ET.SubElement(xml_languageVersion, 'abstract')
    xml_abstract.text = ar['languageVersion']['abstract']
    xml_pdfFileUrl = ET.SubElement(xml_languageVersion, 'pdfFileUrl')
    xml_pdfFileUrl.text = ar['languageVersion']['pdfFileURL']
    xml_publicationDate = ET.SubElement(xml_languageVersion, 'publicationDate')
    xml_publicationDate.text = ar['languageVersion']['publicationDate']
    xml_registrationDate = ET.SubElement(xml_languageVersion, 'registrationDate')
    xml_registrationDate.text = ar['languageVersion']['registrationDate']
    xml_pageFrom = ET.SubElement(xml_languageVersion, 'pageFrom')
    xml_pageFrom.text = ar['languageVersion']['pageFrom']
    xml_pageTo = ET.SubElement(xml_languageVersion, 'pageTo')
    xml_pageTo.text = ar['languageVersion']['pageTo']
    xml_doi = ET.SubElement(xml_languageVersion, 'doi')
    xml_doi.text = ar['languageVersion']['doi']
    xml_keywords = ET.SubElement(xml_languageVersion, 'keywords')
    if not ar['languageVersion']['keywords']:
        xml_keyword = ET.SubElement(xml_keywords, 'keyword')
    for k in ar['languageVersion']['keywords']:
        xml_keyword = ET.SubElement(xml_keywords, 'keyword')
        xml_keyword.text = k
    xml_authors = ET.SubElement(xml_article, 'authors')
    for i, a in enumerate(ar['authors']):
        xml_author = ET.SubElement(xml_authors, 'author')
        xml_name = ET.SubElement(xml_author, 'name')
        xml_name.text = a['name']
        xml_name2 = ET.SubElement(xml_author, 'name2')
        xml_surname = ET.SubElement(xml_author, 'surname')
        xml_surname.text = a['surname']
        xml_email = ET.SubElement(xml_author, 'email')
        xml_email.text = a['email']
        xml_polishAffiliation = ET.SubElement(xml_author, 'polishAffiliation')
        xml_polishAffiliation.text = 'false'
        xml_order = ET.SubElement(xml_author, 'order')
        xml_order.text = str(i + 1)
        xml_instituteAffiliation = ET.SubElement(xml_author, 'instituteAffiliation')
        xml_instituteAffiliation.text = a['institute']
        xml_departmentAffiliation = ET.SubElement(xml_author, 'departmentAffiliation')
        xml_subjectAffiliation = ET.SubElement(xml_author, 'subjectAffiliation')
        xml_role = ET.SubElement(xml_author, 'role')
        xml_role.text = 'AUTHOR'
    xml_references = ET.SubElement(xml_article, 'references')
    if not ar['references']:
        xml_reference = ET.SubElement(xml_references, 'reference')
        xml_unparsedContent = ET.SubElement(xml_reference, 'unparsedContent')
        xml_unparsedContent = 'none'
        xml_order = ET.SubElement(xml_reference, 'order')
        xml_order.text = str(1)
    for i, r in enumerate(ar['references']):
        xml_reference = ET.SubElement(xml_references, 'reference')
        xml_unparsedContent = ET.SubElement(xml_reference, 'unparsedContent')
        xml_unparsedContent.text = r
        xml_order = ET.SubElement(xml_reference, 'order')
        xml_order.text = str(i + 1)
    xml_disciplineSciences = ET.SubElement(xml_article, 'disciplineSciences')
    xml_areaScience = ET.SubElement(xml_disciplineSciences, 'areaScience')
    xml_areaScience.text = str(5)
    xml_fieldScience = ET.SubElement(xml_disciplineSciences, 'fieldScience')
    xml_fieldScience.text = str(2)
    xml_disciplineScience = ET.SubElement(xml_disciplineSciences, 'disciplineScience')
    xml_disciplineScience.text = str(59)

# print(pretty.prettify(ici_import))
# ET.dump(ici_import)

outFile = open('ic-ref.xml', 'w')
outFile.write(pretty.prettify(ici_import))
