import json
import requests
from bs4 import BeautifulSoup
from models.contributor import Contributor
from util.util import get_img, solve_captcha_simple

url = 'https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/'
headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 '
                      'Safari/537.36 '
    }


def get_contributor(ruc):
    return make_request(ruc)


def make_request(ruc):
    s = requests.session()
    captcha_url = url + 'captcha?accion=image'
    get_img(s, captcha_url)
    txt_captcha = solve_captcha_simple()
    return petition(s, txt_captcha, ruc)


def petition(s, txt_captcha, ruc):
    contributor = {}
    response = {
        'data': contributor,
        'message': 'No encontrado'
    }
    post_data = {
        'accion': 'consPorRuc',
        'nroRuc': '%s' % ruc,
        'contexto': 'ti-it',
        'tQuery': 'on',
        'search1': '%s' % ruc,
        'tipdoc': '1',
        'codigo': '%s' % txt_captcha[:-2]
    }
    post_url = url + 'jcrS00Alias'
    r = s.post(post_url, data=post_data, headers=headers)
    if 'El codigo ingresado es incorrecto' not in r.text and txt_captcha.strip():
        print('Data obtenida:')
        contributor = scrapping_data(r, s, post_url)
        response['data'] = contributor.__dict__
        response['message'] = 'Encontrado'
    else:
        print('Volviendo a intentar...')
        return make_request(ruc)
    return response


def scrapping_data(page, s, url_legal_represent):
    soup = BeautifulSoup(page.content, 'html.parser')
    td = soup.find_all('td')
    option = soup.find_all('option')
    ruc_name: str = td[1].get_text()
    rn = ruc_name.split('-')

    name = rn[1].strip()
    ruc = rn[0].strip()
    main_activity = option[0].get_text()
    legal_represent = get_legal_represent(s, url_legal_represent, ruc, name)
    address_fiscal = del_blank(td[16].get_text().strip())
    if 'HABIDO' in address_fiscal:
        address_fiscal = td[20].get_text()
    contributor = Contributor(name, main_activity, legal_represent, address_fiscal, ruc)
    return contributor


def scrapping_data_r(page, s, url_legal_represent):
    # este codigo hace scarpping al nuevo sistema de consultas de la sunat
    soup = BeautifulSoup(page.content, 'html.parser')
    h4 = soup.find_all('h4')
    p = soup.find_all('p')
    table = soup.find_all('table')

    ruc_name: str = h4[1].get_text()
    rn = ruc_name.split('-')

    name = rn[1].strip()
    ruc = rn[0].strip()
    main_activity = get_main_activity(table[0])
    legal_represent = get_legal_represent(s, url_legal_represent, ruc, name)
    address_fiscal = del_blank(p[5].get_text().strip())
    if 'HABIDO' in address_fiscal:
        address_fiscal = p[6].get_text().strip()

    contributor = Contributor(name, main_activity, legal_represent, address_fiscal, ruc)
    return contributor


def del_blank(data: str):
    dat = data.split(' ')
    resp = ''
    for e in dat:
        resp = resp.strip() + ' ' + e.strip()
    return resp


def get_legal_represent(s, url_legal_represent, ruc, name):
    post_data = {
        'accion': 'getRepLeg',
        'desRuc': '%s' % name,
        'nroRuc': '%s' % ruc
    }
    r = s.post(url_legal_represent, data=post_data, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    if 'Pagina de Error' not in r.text:
        data = soup.find_all('td')
        represent: str = data[5].get_text()
        return represent.strip()
    return 'No se encontro.'


def get_main_activity(template):
    soup = BeautifulSoup(str(template), 'html.parser')
    data = soup.find_all('td')
    return data[0].get_text()
