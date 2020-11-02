import requests
import json
from datetime import date, datetime
from bs4 import BeautifulSoup
from models.person import Person
from util.util import get_img, solve_captcha

url = 'http://ww4.essalud.gob.pe:7777/acredita/'
headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 '
                      'Safari/537.36 '
    }


def get_person(dni):
    return first_intent(dni)


def first_intent(dni):
    return make_request(dni)


def make_request(dni):
    s = requests.session()
    captcha_url = url + 'captcha.jpg'
    get_img(s, captcha_url)
    txt_captcha = solve_captcha()
    return petition(s, txt_captcha, dni)


def petition(s, txt_captcha, dni):
    person = {}
    response = {
        'data': person,
        'message': 'No encontrado'
    }
    post_data = {
        'pg': '1',
        'll': 'Libreta Electoral/DNI',
        'td': '1',
        'modo': '1',
        'nd': '%s' % dni,
        'submit': 'Consultar',
        'captchafield_doc': '%s' % txt_captcha[:-2]
    }
    post_url = url + 'servlet/Ctrlwacre'
    r = s.post(post_url, data=post_data, headers=headers)
    if 'Tiene que ingresar el Apellido Paterno, Apellido Materno' in r.text:
        return response
    if 'El codigo es incorrecto' not in r.text and txt_captcha.strip():
        if 'No se encontraron registros' in r.text:
            return end_intent(dni)
        print('Data obtenida:')
        person = scrapping_data(r)
        response['data'] = person.__dict__
        response['message'] = 'Encontrado'
    else:
        print('Volviendo a intentar...')
        return make_request(dni)

    print(response)
    return response


def scrapping_data(page):
    soup = BeautifulSoup(page.content, 'html.parser')
    td = soup.find_all('td')
    names: str = td[5].get_text()
    data_names = names.split(',')
    name = data_names[1].strip()
    lastname, mother_last_name = lastnames_cases(data_names[0].strip())
    dni = td[7].get_text()
    birthday = get_fn(td[11].get_text())
    age = get_age(birthday)
    sex = td[11].get_text()[6:7]
    if '0' in sex:
        sex = '2'
    person = Person(name, lastname, mother_last_name, age, birthday, dni, 'none', '01', sex)
    return person


def get_fn(fn: str):
    nfn = fn[:6]
    y = nfn[:-4]
    # aqui cambiar si esto sigue funcionando con el paso de los años
    if int(y) > 30:
        y = '19' + y
    else:
        y = '20' + y
    m = nfn[2:-2]
    d = nfn[4:]
    return y + '-' + m + '-' + d


def lastnames_cases(lastname: str):
    data_last = lastname.split(' ')
    lastname = data_last[0].strip()
    mother_lastname = data_last[1].strip()
    if len(data_last) == 3:
        if 'del' in data_last[0].lower() or 'de' in data_last[1].lower():
            lastname = data_last[0] + ' ' + data_last[1]
            mother_lastname = data_last[2]
        if 'del' in data_last[1].lower() or 'de' in data_last[1].lower():
            lastname = data_last[0]
            mother_lastname = data_last[1] + ' ' + data_last[2]
    if len(data_last) == 4:
        if 'de' in data_last[0].lower():
            lastname = data_last[0] + ' ' + data_last[1] + ' ' + data_last[2]
            mother_lastname = data_last[3]
        if 'de' in data_last[1].lower():
            lastname = data_last[0]
            mother_lastname = data_last[1] + ' ' + data_last[2] + ' ' + data_last[3]
    return lastname, mother_lastname


def end_intent(dni):
    route = 'https://siscovid.minsa.gob.pe/ficha/api/buscar-documento/01/%s/' % dni
    r = requests.get(route)
    j = json.loads(r.text)
    data = j['datos']['data']
    person = {}
    response = {
        'data': person,
        'message': 'No encontrado'
    }

    if 'Documento de Identidad no encontrado' not in j['datos']['resultado']:
        birthday = format_birthday(data['fecha_nacimiento'])
        photo_url = 'data:image/png;base64,' + data['foto']
        age = get_age(birthday)
        person = Person(
            data['nombres'], data['apellido_paterno'], data['apellido_materno'], age, birthday,
            data['numero_documento'],
            'none', data['tipo_documento'], data['sexo']
        )
        response['data'] = person.__dict__
        response['message'] = 'Encontrado'

    return response


def get_age(birthday):
    bd = datetime.fromisoformat(birthday)
    age = date.today().year - bd.date().year
    return age


def format_birthday(in_birthday: str):
    birthday = in_birthday.replace('-', '')
    y = birthday[:-4]
    m = birthday[4:-2]
    d = birthday[6:]
    return y + '-' + m + '-' + d
