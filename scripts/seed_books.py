import os
import uuid

import internetarchive as ia
import pandas as pd
from django.utils.crypto import get_random_string

template = """
<!--
.. title:
.. slug: {}
.. tags: {}
.. category:
.. link:
.. description:
.. type: text
.. date: {}
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
    data = []

    df = pd.read_csv('data/ia.csv', index_col=['identifier'])

    for index, item in enumerate(ia.search_items(query=query)):
        print(index, item)
        pk = item['identifier']
        if pk in df.index:
            continue
        item = ia.get_item(pk)
        metadata = item.item_metadata['metadata']
        metadata['item_url'] = item.urls.details
        data.append(metadata)

        # import ipdb; ipdb.set_trace()

        if index % 10 == 0:
            df = pd.DataFrame(data)
            df.set_index('identifier', inplace=True)
            df.to_csv('data/ia.csv')

    df = pd.DataFrame(data)
    df.set_index('identifier', inplace=True)
    df.to_csv('data/ia.csv')


def update_csv():
    update_archive_books()


from random import randrange
import time


def randomize_time():
    start_timestamp = time.mktime(time.strptime('Jun 1 2010  01:33:00', '%b %d %Y %I:%M:%S'))
    end_timestamp = time.mktime(time.strptime('Jun 1 2017  12:33:00', '%b %d %Y %I:%M:%S'))
    return time.strftime('%Y-%b-%d %I:%M:%S', time.localtime(randrange(start_timestamp, end_timestamp)))


def create_books():
    df = pd.read_csv('data/ia.csv', index_col=['identifier'])

    # for index, row in df.iterrows():
    #     print(row['title'], row['item_url'])

    directory = 'posts'
    try:
        os.makedirs(directory)
    except:
        pass
    for i in range(30000):
        file_name = 'posts/{}.html'.format(get_random_string(length=10))
        slug = str(uuid.uuid4())
        content = '{}.md'.format(get_random_string(length=700))

        categories = 'author_{}, title_{}'.format(slug[0], slug[1])
        tags = categories

        date = randomize_time()
        # print(date)
        data = template.format(slug, tags, date, content)


        # print(file_name)
        with open(file_name, 'w') as fh:
            fh.write(data)

        if(i % 100 == 0):
            print(i)
        # print(row)
        # e


# update_csv()
create_books()
