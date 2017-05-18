import sys
import yaml
from pprint import pprint, pformat
from argparse import ArgumentParser
import time

# clolor font
import colorama
from colorama import Fore, Back, Style

from router import Router

def print_bool_result(binary_result,color_spec):
    """ 
    print boolean result.
    @params:
        binary_result - Required : Ture or False boolean 
        color_spec    - Required : specifid colorama option. e.g. 'Back','Fore'
    """
    if binary_result:
        print(eval(color_spec).GREEN + '[OK]' , end=' ')
    else:
        print(eval(color_spec).RED + '[NG]' , end=' ')

def print_validate_error(compare_dict):
    pass
    

def main():
    """main function."""

    # Parse argment
    parser = ArgumentParser(description='run scenario_file')
    parser.add_argument('-f', '--file',
                        type=str,
                        help='scenario file',
                        required=True)
    args = parser.parse_args()

    # Set color font
    colorama.init(autoreset=True)

    # Read router infomation file
    try:
        with open(args.file, 'r') as f:
            param_yaml = f.read()
    except (IOError, IndexError):
        sys.stderr.write('Cannot open file : ' + args.file + '\n')
        sys.exit(1)

    # Convert yaml format to python_type
    try:
        param = yaml.load(param_yaml)
    except ValueError as error:
        sys.stderr.write('YAML format error : \n')
        sys.stderr.write(param_yaml)
        sys.stderr.write(str(error))
        sys.exit(1)

    router1 = Router(
        hostname    = param['hosts']['hostname'],
        os          = param['hosts']['os'],
        ipaddress   = param['hosts']['management_ipaddress'],
        username    = param['hosts']['username'],
        password    = param['hosts']['password'])

    print('########## Run Senario : ' + args.file + ' ##########')

    print('operator : %s'       % (param['operator']))
    print('operation_date : %d' % (param['operation_date']))
    print('hostname : %s'       % (param['hosts']['hostname']))
    print('purpose :')
    print(param['purpus'])
    
    print('Connect to ' + param['hosts']['hostname'] + ' : ', end='')
    router1.open()
    print(Fore.GREEN + 'OK')

    for scenario_param in param['scenario']:
        if isinstance(scenario_param, dict):
            operation_name  = next(iter(scenario_param))
            operation_param = scenario_param[operation_name]
        else:
            operation_name = scenario_param
            operation_param = None

        if 'validate' == operation_name:
            print(Back.BLUE+'Pre-Validation Start : {0}'.center(50,'-').format(param['hosts']['hostname']))
            complies_result = router1.validate_operation(operation_name)
            #pprint(result)
            v_index = complies_result.keys()
            for v in v_index:
                if v.startswith('get_'):
                    print_bool_result(complies_result[v]['complies'],'Fore')
                    print('validate {0}'.format(v))
            print('-'*20)
            print_bool_result(complies_result['complies'],'Fore')
            print('validation total result')

        elif 'get_' in operation_name:
            print(Back.BLUE+'Get and show command : {0}'.center(50,'-').format(param['hosts']['hostname']))
            print('GET <%s> : '%(operation_name))
            result = router1.call_getters(operation_name)
            pprint(result)

        elif 'set_' in operation_name:
            print(Back.BLUE+'Set Config : {0}'.center(50,'-').format(param['hosts']['hostname']))  
            result, message =\
                router1.load_config(operation_name, operation_param)
            print_bool_result(result,'Fore')
            print('Load config on < {0} > '.format(operation_name))
            if result:
                print('-'*30)
                print(Fore.YELLOW + message)
                print('-'*30)
            else:
                print(Back.RED + message)
                print(Back.RED + 'Config load error! system exit.')
                router1.discard_config()
                router1.close()
                sys.exit()
            
            print(Back.BLUE+'Compare Config : {0}'.center(50,'-').format(param['hosts']['hostname']))
            print('Compare config on < {0} >'.format(operation_name))
            message = router1.compare_config()
            if message != '':
                print('-'*30)
                print(Fore.YELLOW + message)
                print('-'*30)
                print(Fore.YELLOW + "Do you commit? (y/n) : ", end = '')
                choice = input().lower()
                if choice == 'y':
                    print_bool_result(router1.commit(),'Fore')
                    print('Commit config')
                else:
                    print_bool_result(router1.discard_config(),'Fore')
                    print('Discard config : ')
            else:
                print(Fore.YELLOW+'[INFO]',end='')
                print(' No changes this router by {0} config'.format(operation_name))

        elif operation_name == 'sleep_10sec':
            print('Sleep 10 sec : ', end='')
            time.sleep(10)
            print(Fore.GREEN + 'OK')

        else:
            print('Cannnot run operation : '+Back.RED + operation_name)

    print('Close the connection to ' + param['hosts']['hostname'])
    router1.close()
    

    print('########## End Senario : ' + args.file + ' ##########')

if __name__ == '__main__':
    main()