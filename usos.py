from rauth import OAuth1Service
from datetime import datetime

usos = OAuth1Service(
    name='USOS',
    consumer_key='SSXmASZf6MaXSP5DPRn7',
    consumer_secret='pVJjERsgYBv2mNteV9TBkbVapJjVh3L59ZBHcLSL',
    request_token_url='https://usosapps.prz.edu.pl/services/oauth/request_token',
    access_token_url='https://usosapps.prz.edu.pl/services/oauth/access_token',
    authorize_url='https://usosapps.prz.edu.pl/services/oauth/authorize',
    base_url='https://usosapps.prz.edu.pl/services/'
)

request_token, request_token_secret = usos.get_request_token(params={'oauth_callback': 'https://callback/', 'scopes': 'studies|grades'})
authorize_url = usos.get_authorize_url(request_token)
print(f'Otwórz link w przeglądarce: {authorize_url}')
pin = input('oauth_verifier znajdujący się w linku: ')

session = usos.get_auth_session(request_token,
                                request_token_secret,
                                method='POST',
                                data={'oauth_verifier': pin})

articles = session.get('news/search', params={'fields': 'items[article[author|title]]'}).json()

print('Ostatnie wiadomości: ')
for _, article in enumerate(articles['items']):
    print(f'{article["article"]["author"]}: {article["article"]["title"]["pl"]}')

timetable = session.get('tt/user').json()
time_format = '%Y-%m-%d %H:%M:%S'

print('Zbliżające się zajęcia: ')
for _, classgroup in enumerate(timetable):
    start_time = datetime.strptime(classgroup["start_time"], time_format).time()
    end_time = datetime.strptime(classgroup["end_time"], time_format).time()
    print(f'{start_time} - {end_time}: {classgroup["name"]["pl"]}')

terms = session.get('terms/search', params={'min_finish_date': '2018-10-01'}).json()
terms_ids = []
for _, term in enumerate(terms):
    terms_ids.append(term['id'])

grades = session.get('grades/terms2', params={'term_ids': '|'.join(terms_ids)}).json()

print('Oceny podzielone semestrami od dnia 2018-10-01: ')
for _, (term_id, term) in enumerate(grades.items()):
    print(f'{term_id}: ')
    for _, (course_id, course_grades) in enumerate(term.items()):
        grades = []
        for _, grade in enumerate(course_grades['course_grades']):
            if grade['1'] is not None:
                grades.append(grade['1']['value_symbol'])
        print(f'{course_id}: {", ".join(grades)}')