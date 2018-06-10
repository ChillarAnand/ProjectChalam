import functools
import os
import string
import sys

import internetarchive as ia
import pandas as pd
from jinja2 import Template
from indic_transliteration import sanscript
from indic_transliteration.sanscript import SchemeMap, SCHEMES, transliterate


scheme_map = SchemeMap(SCHEMES[sanscript.VELTHUIS], SCHEMES[sanscript.TELUGU])
te_trans = functools.partial(transliterate, scheme_map=scheme_map)

alphabets = string.ascii_lowercase

vowels = 'అఆఇఈఉఊఋఌఎఏఐఒఓఔ'
consonants = 'కఖగఘఙచఛజఝఞటఠడఢణతథదధనపఫబభమయరఱలళవశషసహ'
te_alphabets = vowels + consonants

content_directory = 'books'


template = """<!--
.. title:
.. slug: {}
.. link:
.. description:
.. type: text
-->

{}
"""


def update_archive_books():
    params = {'mediatype': 'texts'}
    fields = (
        'creator', 'contributor', 'date', 'description', 'genre', 'language',
        'name', 'publisher',
        'source', 'scanningcenter', 'title', 'subject', 'volume',
    )
    fields = ()
    query = 'language:Telugu and mediatype:texts'
    query = 'mediatype:texts and languageSorter:Telugu'
    query = 'languageSorter:Telugu'
    data = []

    try:
        df = pd.read_csv('data/ia.csv', index_col=['identifier'])
    except FileNotFoundError:
        print('Creating new file')
        df = pd.DataFrame()

    cdf = df

    for index, item in enumerate(ia.search_items(query=query)):
        print(index, item)
        pk = item['identifier']
        if pk in df.index:
            continue
        item = ia.get_item(pk)
        metadata = item.item_metadata.get('metadata', {'item_url': ''})
        metadata['item_url'] = item.urls.details
        print(metadata['item_url'])
        data.append(metadata)

        # import ipdb; ipdb.set_trace()

        if index % 5 == 0:
            dfo = pd.read_csv('data/ia.csv', index_col=['identifier'])
            df = pd.DataFrame(data)
            df.set_index('identifier', inplace=True)

            df = pd.concat([dfo, df])
            df.to_csv('data/ia.csv')

            df = pd.read_csv('data/ia.csv', index_col=['identifier'])
            df.drop_duplicates(inplace=True)
            df.to_csv('data/ia.csv')
            print(df.shape, len(df))
            print('file saved')

    # df = pd.DataFrame(data)
    # df.set_index('identifier', inplace=True)
    # df.to_csv('data/ia.csv')


def update_csv():
    update_archive_books()


def create_html_page(df, slug):
    # print(df.head())
    df.reset_index(drop=True, inplace=True)
    html_template = Template(open('scripts/book_data.html').read())
    content = html_template.render(df=df)
    content = template.format(slug, content)

    file_name = '{}/{}.html'.format(content_directory, slug)
    with open(file_name, 'w') as fh:
        fh.write(content)


def create_pages():
    filename = 'data/data.csv'

    df = pd.read_csv(filename, index_col=['identifier'])
    print(df.shape)
    df['title'] = df['title'].apply(str)
    df['title_ci'] = df['title'].apply(str.lower)
    df['title_te'] = df['title'].apply(te_trans)

    url = df['item_url']
    url = url + '/' + url.str.split('/').str[-1] + '.pdf'
    url = url.str.replace('details', 'download')
    df['item_url'] = url

    cdf = df

    try:
        os.makedirs(content_directory)
    except OSError:
        pass

    for alphabet in alphabets:

        if debug:
            print(alphabet)

        slug = alphabet

        fdf = df[df['title_ci'].str.startswith(alphabet)]
        fdf = fdf[['title', 'item_url']]
        create_html_page(fdf, slug)

    df = cdf

    for alphabet in te_alphabets:

        if debug:
            print(alphabet)

        slug = alphabet

        fdf = df[df['title_te'].str.startswith(alphabet)]
        fdf = fdf[['title_te', 'item_url']]
        fdf['title'] = fdf.pop('title_te')
        create_html_page(fdf, slug)


debug = True
# debug = False

if len(sys.argv) > 1:
    if 'ia' in sys.argv:
        update_csv()

create_pages()
