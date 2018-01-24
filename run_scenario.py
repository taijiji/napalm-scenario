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


def print_validate_fail_detail(compare_object,key=''):
    """
    print invalid reason.
    @params:
        compare_object - Required : validation result object (result of compliace_report())
        key            - Optional : dict key of compliance_result
    """
    if isinstance(compare_object,dict):
        for key,dst in compare_object.items():
            if isinstance(dst,dict):
                # recursive
                reason,result = print_validate_fail_detail(dst,key)
                if not reason == None:
                    print(' '*9 , end='')
                    print(Fore.RED + 'INVALID! [type:{0}] {1} : {2}'.format(key,reason,result))
            elif isinstance(dst,list):
                for d in dst:
                    return key,d
            elif isinstance(dst,int):
                if not (isinstance(dst,bool)) or (key == 'actual_value'):
                    return key,dst
    return None,None


def input_judgment(message): 
    print(Fore.YELLOW + message, end = '(y/n): ')
    choice = input().lower()
    if choice == 'y':
        return True
    else:
        return False


def rollback_operation(device,config):
    try:
        device.discard_config()
        replace_result = device.replace(config)
        commit_result = device.commit()
        rollback = replace_result & commit_result
        print_bool_result(rollback,'Fore')
        print('Rollbacked config!')

    except Exception as err:
        print(Back.RED + 'Rollback Error!!')
        print(Back.RED + str(err))

    finally:
        device.close()
        sys.exit()


def load_senario(senario_filename):
    # Read senario file
    try:
        with open(senario_filename, 'r') as f:
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
    
    return param

def run_connect_to_router(router):
    if not router.open():
        print_bool_result(True,'Fore')
    else :
        print_bool_result(False,'Fore')


def run_get_config(router):
    config = router.get_config()
    if config:
        print_bool_result(True,'Fore')
    else:
        print_bool_result(False,'Fore')
    
    return config


def run_scenario(router, senario_filename, param):

    router_hostname     = param['hosts']['hostname']
    operator_name       = param['operator']
    operation_data      = param['operation_date']
    operation_purpus    = param['purpus']

    print('########## Run Senario : ' + senario_filename + ' ##########')

    print('operator         : %s'   % (operator_name))
    print('operation_date   : %d'   % (operation_data))
    print('hostname         : %s'   % (router_hostname))
    print('purpose          :\n%s'  % (operation_purpus))

 
    run_connect_to_router(router)
    print('Connect to ' + router_hostname)

    configu_before = run_get_config(router)
    print('Get config_before of ' + router_hostname)


    for scenario_param in param['scenario']:
        if isinstance(scenario_param, dict):
            operation_name  = next(iter(scenario_param))
            operation_param = scenario_param[operation_name]
        else:
            operation_name = scenario_param
            operation_param = None

        if 'validate' == operation_name:

            # Run Validation process
            if operation_param:
                complies_result = router.validate_operation(operation_param)
            else:
                complies_result = router.validate_operation({operation_name:None})

            pprint(complies_result)

            v_index = complies_result.keys()
            for v in v_index:
                if v.startswith('get_'):
                    print_bool_result(complies_result[v]['complies'],'Fore')
                    print('validate {0}'.format(v))
                    if not complies_result[v]['complies']:
                        print_validate_fail_detail(complies_result[v])
            if not complies_result['complies']:
                if not input_judgment('Validate is fail. Continue?'):
                    rollback_operation(router, config_before['running'])

        elif 'get_' in operation_name:
            print('Get and show command : {0}'.center(50,'=').format(param['hosts']['hostname']))
            print('GET <%s> : '%(operation_name))
            result = router.call_getters(operation_name,operation_param)
            pprint(result)

        elif 'set_' in operation_name:
            print('Set Config : {0}'.center(50,'=').format(param['hosts']['hostname']))  
            result, message =\
                router.load_config(operation_name, operation_param)
            print_bool_result(result,'Fore')
            print('Load config on < {0} > '.format(operation_name))
            if result:
                print('-'*30)
                print(Fore.YELLOW + message)
                print('-'*30)
            else:
                print(Back.RED + message)
                print(Back.RED + 'Config load error! Operation is Rollbacked...')
                rollback_operation(router, config_before['running'])

            print('Compare Config : {0}'.center(50,'=').format(param['hosts']['hostname']))
            print('Compare config on < {0} >'.format(operation_name))
            message = router.compare_config()
            if message != '':
                print('-'*50)
                print(Fore.YELLOW + message)
                print('-'*50)
                if input_judgment('Do you commit?'):
                    print_bool_result(router.commit(),'Fore')
                    print('Commit config')
                else:
                    rollback_operation(router, config_before['running'])
            else:
                print(Fore.YELLOW+'[INFO] No changes this router by {0} config'.format(operation_name))

        elif operation_name == 'sleep_10sec':
            print_bool_result(True,'Back')
            print('Sleep 10 sec',end='')
            for i in range(10):
                time.sleep(1)
                if i == 9:
                    print('.')
                else:
                    print('.',end='')

        elif operation_name == 'rollback':
            rollback_operation(router,config_before['running'])
            print_bool_result(True,'Back')
            print('Rollback Config!', end='')

        else:
            print('Cannnot run operation : '+Back.RED + operation_name)
    
    if not router.close():
        print_bool_result(True,'Back')
    else:
        print_bool_result(False,'Back')
    print('Close the connection to ' + param['hosts']['hostname'])

    print('########## End Senario : ' + args.file + ' ##########')


def main():
    """main function."""
    # Set color font
    colorama.init(autoreset=True)

    # Parse argment
    parser = ArgumentParser(description='run scenario_file')
    parser.add_argument('-f', '--file', type=str,
                        help='scenario file', required=True)
    args = parser.parse_args()

    scenario_filename = args.file
    param = load_senario(scenario_filename)

    router1 = Router(
        hostname    = param['hosts']['hostname'],
        os          = param['hosts']['os'],
        ipaddress   = param['hosts']['management_ipaddress'],
        username    = param['hosts']['username'],
        password    = param['hosts']['password'])

    run_scenario(router1, scenario_filename, param)


if __name__ == '__main__':
    main()