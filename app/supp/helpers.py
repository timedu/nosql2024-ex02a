
import yaml # pyright: ignore
from neo4j.exceptions import CypherSyntaxError # pyright: ignore
from prettytable import PrettyTable # pyright: ignore
from os import path
from supp.config import todo

_QRY_TITLES = {
    'qry_0a': '(0a) Number of persons',
    'qry_0b': '(0b) Number of movies',
    'qry_1':  '(1) In what years have films been released in this millennium?',
    'qry_2':  '(2) Who work as directors?',
    'qry_3':  '(3) Who has followers?',
    'qry_4':  '(4) How do people with followers relate to movies?',
    'qry_5':  '(5) What movies have been reviewed?',
    'qry_6':  '(6) Which of the films has received the best review?',
    'qry_7':  '(7) Which of the actors also work as directors?',
    'qry_8':  '(8) Who have acted in the films they have directed?',
    'qry_9':  '(9) Show Jack Nicholson movie taglines.',
    'qry_10': '(10) Who are the actors named Bill?'
}

_CRUD_TITLES = {
    'crud_1': '(1) Add a course',
    'crud_2': '(2) Add two teachers',
    'crud_3': '(3) Set a person as responsible teacher of the course',
    'crud_4': '(4) Add another course and make it a prerequisite for the first',
    'crud_5': '(5) Remove teachers who are not responsible for courses'
}

_CRUD_FB_QRY = {
    'crud_1': 'MATCH (c:Course) RETURN c.code, c.name',
    'crud_2': 'MATCH (t:Teacher) RETURN t.name',
    'crud_3': 'MATCH (t:Teacher)-[r]->(c:Course) RETURN t.name, type(r), c.code ',
    'crud_4': 'MATCH (c2:Course)-[r]->(c1:Course) RETURN c2.code, c2.name, type(r), c1.code ',
    'crud_5': 'MATCH (t:Teacher) RETURN t.name',
}

_TODOS_PATH = path.join(
    path.dirname(path.abspath(__file__)), '..', 'todos'
)

def load_queries():
    '''
    Loads queries from file to dict
    '''    
    qry_path = path.join(_TODOS_PATH, todo['folder'], 'queries.yml')
    with open(qry_path, 'r') as file:
        queries_dict = yaml.safe_load(file)
    return queries_dict

def execute_query(driver, command):
    '''
    Loads queries and executes one
    '''
    query = load_queries()[command]
    return driver.execute_query(query)

def print_qry_result(result, command=None):
    '''
    Print feedback for query that returns data
    '''
    table = PrettyTable()
    table.align = 'l'
    table.field_names = result.keys
    table.add_rows ([record.values() for record in result.records ])
    if command: 
        print(_QRY_TITLES[command])
        print()
        print(result.summary.query)
    print(table)
    print(f'{len(result.records)} record(s)')

def execute_all_qry(driver):
    '''
    Loads queries and executes all that return data
    '''
    queries = load_queries()
    print()
    for i in range(1,11):
        command = f'qry_{i}'
        try:
            result = driver.execute_query(queries[command])
            print_qry_result(result, command)
        except CypherSyntaxError as err:
            print(_QRY_TITLES[command])
            print()
            print(err)
        except KeyError:
            print('Unkwown query:', command)
        finally:
            print()
            continue

def print_crud_result(result, command=None, driver=None):
    '''
    Print feedback for query not returning data
    '''
    ctr_obj = result.summary.counters
    ctr_list = [
        attr for attr in dir(ctr_obj)\
        if not callable(getattr(ctr_obj, attr))\
        and not attr.startswith("_")\
        and not attr.startswith("contains_")\
        and getattr(ctr_obj, attr) > 0
    ]
    if command:
        print(_CRUD_TITLES[command])
        print()
        print(result.summary.query)
    for ctr in ctr_list: 
        print(f'- {ctr}: {getattr(ctr_obj, ctr)}')
    if command:
        print_qry_result(driver.execute_query(_CRUD_FB_QRY[command]))

def execute_all_crud(driver):
    '''
    Loads queries and executes all not returning data
    '''
    queries = load_queries()
    print()
    for i in range(1,6):
        command = f'crud_{i}'
        try:
            result = driver.execute_query(queries[command])
            print_crud_result(result, command, driver)
        except CypherSyntaxError as err:
            print(_CRUD_TITLES[command])
            print()
            print(err)
        except KeyError:
            print('Unkwown query:', command)
        finally:
            print()
            continue

def merge_movie_data(driver):    
    '''
    Stores movie data if not already exist; 
    expected feedback
    - labels_added: 171
    - nodes_created: 171
    - properties_set: 564
    - relationships_created: 253
    '''    
    qry_path = path.join(
        path.dirname(path.abspath(__file__)), 
        'merge_movie_data.cypher'
    )
    with open(qry_path, 'r') as file:
         query = file.read()
    result = driver.execute_query(query)
    print_crud_result(result)
