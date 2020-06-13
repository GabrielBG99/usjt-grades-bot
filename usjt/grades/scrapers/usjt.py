import requests, json, re, os
from bs4 import BeautifulSoup

from . import exceptions
from .. import models


BASE_URL = 'https://aluno.usjt.br'
LOGIN_SCREEN_ENDPOINT = '/SOL/aluno/index.php/index/seguranca/dev/instituicao/8'
LOGIN_ENDPOINT = '/SOL/aluno/index.php/index/seguranca/login'
GRADES_ENDPOINT = '/SOL/aluno/index.php/disciplinas/dev/mod/notas'
GRADES_DETAIL_ENDPOINT = '/SOL/aluno/index.php/disciplinas/index/buscar'


def _verify_year(year):
    return models.Class.objects.filter(
        semester=year
    ).exists()

def _verify_request(request):
    if not request.ok:
        raise exceptions.RequestError(
            html=request.text,
            code=request.status_code
        )
    else:
        try:
            if '__error' in request.json():
                raise exceptions.RequestError(
                    html=request.text,
                    code=request.status_code
                )
        except:
            return

def _do_login(s):
    r = s.get(BASE_URL + LOGIN_SCREEN_ENDPOINT, timeout=10)
    r = s.post(
        url=BASE_URL + LOGIN_ENDPOINT,
        data={
            'loginEx[]': '1',
            'autologin': '',
            'combo': '2',
            'matricula': os.getenv('USJT_RA'),
            'senha': os.getenv('USJT_PASSWORD'),
            'num_cpf': '',
            'dat_nascimento': '',
            'instituicao': '8',
            'codigo_marca': '3',
            'logar': 'Entrar',
            '__ajax': '1',
            'opcao_acesso': '1'
        }, 
        timeout=10
    )
    _verify_request(request=r)
    data = r.json()['data']['identity']
    return data['access_token'], data['token_type']

def _parse_single_grade(s, class_):
    r = s.post(
        url=BASE_URL + GRADES_DETAIL_ENDPOINT,
        data={
            '__ajax': '1',
            'CODPERIODOLETIVO': class_['CODPERIODOLETIVO'],
            'CODDISCIPLINA': class_['CODDISCIPLINA'],
            'CODDIARIOCLASSE': class_['CODDIARIOCLASSE'],
            'EXIBIRCONCEITO': 'N',
            'INDBUSCARMATERIAL': 'N',
            'INDBUSCACALENDARIO': 'N',
            'INDBUSCARNOTAS': 'S',
            'INDDETALHESNOTAS': 'S'
        }, 
        timeout=10
    )
    _verify_request(request=r)
    r = r.json()
    grades_detail = BeautifulSoup(
        r['detalheNotas']['HTML'], 
        'html.parser'
    ).find('tbody')
    if grades_detail:
        grades_detail = grades_detail.find_all('tr', recursive=False)
    else:
        grades_detail = []
    
    detail = {
        'A1': None,
        'A2': None,
        'D1': None,
        'D2': None,
        'D3': None,
    }
    for g in grades_detail:
        if not g.text.strip():
            continue
        grade = g.find_all('td')
        rating = grade[1].text.strip().split(' - ')[0]
        rating = re.sub(r'(\w) (\d)', r'\1 \2', rating)
        rating = rating.split()[-2][0].upper() + rating.split()[-1].upper()
        detail[rating] = float(
            re.sub(',', '.', grade[-2].text.strip())
        )

    grades = r['notas'][0]
    
    try:
        grade = float(re.sub(',', '.', grades['VALTOTAL']))
    except:
        grade = 100 if grades['VALTOTAL'].lower() == 'habilitado' else 0
    
    grade = {
        'Professor': class_['NOMPROFESSOR'],
        'Total': grade,
        'Absences': int(grades['NUMFALTAS']),
    }
    grade.update(detail)
    return grades['NOMDISCIPLINA'], grade

def _get_year_info(s, year):
    resp = s.post(
        url=BASE_URL + GRADES_DETAIL_ENDPOINT,
        data={
            '__ajax': '1',
            'CODPERIODOLETIVO': year['CODPERIODOLETIVO'],
            'INDBUSCARDISCIPLINAS': 'S'
        }, 
        timeout=10
    )
    _verify_request(request=resp)
    resp = resp.json()['DADOS']
    classes = {}
    for r in resp:
        classes[r['NOMTURMADISCIPLINA']] = {
            'CODDISCIPLINA': r['CODDISCIPLINA'],
            'CODDIARIOCLASSE': r['CODDIARIOCLASSE'],
            'CODPERIODOLETIVO': year['CODPERIODOLETIVO'],
            'NOMPROFESSOR': r['NOMPROFESSOR'],
        }
    return classes

def _parse_year_grade(grades):
    parsed = {}
    for course, grade in grades.items():
        if len(grade) == 1:
            _grade = grade[0].copy()
            _grade['Professors'] = [_grade.pop('Professor')]
            parsed[course] = _grade
        else:
            joined = {}
            for g in grade:
                for k, v in g.items():
                    if k not in joined:
                        if k == 'Professor':
                            joined[k] = [v]
                        else:
                            joined[k] = v
                    elif k == 'Professor':
                        joined[k].append(v)
                    else:
                        joined[k] = joined[k] or v
            joined['Professors'] = list(set(joined.pop('Professor')))
            parsed[course] = joined
    return parsed

def _get_grades(s):
    r = s.get(BASE_URL + GRADES_ENDPOINT, timeout=10)
    _verify_request(request=r)
    soup = BeautifulSoup(r.content, 'html.parser')
    soup = soup.find('form', id='form-filter')

    year_option = soup.find('select', id='cmbCodPeriodoLetivo')
    year_option = [
        y for y in year_option.find_all('option') if y['value'].strip()
    ]
    latest_year = [
        max(
            year_option, 
            key=lambda y: int(y.text.split('/')[0]) + int(y.text.split('/')[1])
        )
    ]
    year_option = [
        y for y in year_option if not _verify_year(year=y.text.strip())
    ]
    if not year_option:
        year_option = latest_year
    classes_per_year = {
        y.text.strip(): _get_year_info(
            s,
            json.loads(y['value'])
        ) for y in year_option
    }

    grades = {}
    for y, classes in classes_per_year.items():
        year_data = {}
        for _, c in classes.items():
            course, data = _parse_single_grade(
                s=s, 
                class_=c
            )
            if course not in year_data:
                year_data[course] = []
            year_data[course].append(data)
        grades[y] = _parse_year_grade(year_data)

    return grades

def scrape():
    with requests.Session() as s:
        token, type_ = _do_login(s)
        s.headers.update({'Authorization': f'{type_} {token}'})
        return _get_grades(s)


if __name__ == '__main__':
    scrape()
