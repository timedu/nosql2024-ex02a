
import traceback
try: import readline
except: pass 
from dotenv import load_dotenv # pyright: ignore
from os import environ
from neo4j import GraphDatabase # pyright: ignore
from neo4j.exceptions import CypherSyntaxError, ConfigurationError # pyright: ignore
from supp import helpers, config

def repl():
    
    driver = None

    while True:

        try:
            user_input = input(config.todo['prompt'])

        except EOFError:
            if driver: driver.close()
            print('')
            break        

        if not user_input.strip(): continue
        input_strings = user_input.lower().split()
        command = input_strings[0]

        try:

            if len(input_strings) != 1: raise AssertionError

            if command in ('exit', 'quit'):
                if driver: driver.close()
                break

            if not driver: 
                # driver = GraphDatabase.driver(environ['NEO4J_URI'])
                auth = (environ.get('NEO4J_USER'), environ.get('NEO4J_PWD')) \
                       if environ.get('NEO4J_USER') else ()
                driver = GraphDatabase.driver(
                    environ.get('NEO4J_URI'),
                    auth=auth
                )

            if command == 'merge_movie_data':
                helpers.merge_movie_data(driver)
                continue

            if command == 'delete_all_data':
                result = driver.execute_query('MATCH (n) DETACH DELETE n')
                helpers.print_crud_result(result)
                continue

            if command == 'all_qry':
                helpers.execute_all_qry(driver)
                continue
            
            if command == 'all_crud':
                helpers.execute_all_crud(driver)
                continue

            if command.startswith('qry'):
                result = helpers.execute_query(driver, command)
                helpers.print_qry_result(result, command)
                continue

            if command.startswith('crud'):
                result = helpers.execute_query(driver, command)
                helpers.print_crud_result(result, command, driver)
                continue

            raise AssertionError

        except KeyError:
            print('Unkwown query:', command)

        except AssertionError:
            print('Usage:{{qry|crud}_<int>|all_{qry|crud}|merge_movie_data|delete_all_data|exit|quit}')

        except (CypherSyntaxError, FileNotFoundError, ConfigurationError) as err:
            print(err)

        except Exception as err:
            print(err)
            # traceback.print_exc()

if __name__ == '__main__':

    load_dotenv()
    print(f'Using Neo4j in {environ.get("NEO4J_URI")}')

    config.set_config()
    repl()
