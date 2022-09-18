import typing
import numpy as np
def np_generate(dimension:typing.Tuple[int,...]=None):
    if dimension == None:
        return np.random.rand(5)
    if type(dimension) != tuple:
        raise RuntimeError('Numpy dimension require int tuple')
    for i in dimension:
        if type(i) != int:
            raise RuntimeError('Numpy dimension require int tuple')
    return np.random.rand(*dimension)

def str_generate() -> str:
    return 'This string is generated.'

def int_generate() -> str:
    return 12

def float_generate() -> float:
    return 1.234

def list_generate(args) -> typing.List[typing.Any]:
    res = [input_type_generator(i) for i in args]
    return res

def tuple_generate(args) -> typing.Tuple[typing.Any]:
    res = tuple([input_type_generator(i) for i in args])
    return res

def dict_generate(args) -> typing.Dict[typing.Any,typing.Any]:
    k = input_type_generator(args[0])
    v = input_type_generator(args[1])
    return {k:v}

def input_type_generator(itype) -> typing.Any:
    type_gen_method = {
        str: str_generate,
        int: int_generate,
        float: float_generate,
        np.ndarray: np_generate
    }
    if itype in type_gen_method:
        return type_gen_method[itype]()
    if hasattr(itype, '__origin__'):
        meta_type_gen_method = {
            list: list_generate,
            tuple: tuple_generate,
            dict: dict_generate,
            typing.List: list_generate,
            typing.Tuple: tuple_generate,
            typing.Dict: dict_generate
        }
        if itype.__origin__ in meta_type_gen_method:
            return meta_type_gen_method[itype.__origin__](itype.__args__)
    return object

def var_type_check(var, check_type):
    if check_type == typing.Any:
        return True
    if type(var) not in [list, tuple, dict]:
        return type(var) == check_type
    if type(var) in [list, tuple, dict]:
        if len(var) == 0:
            return True
        if not hasattr(check_type, '__origin__'):
            return False
    if type(var) == list:
        return all([var_type_check(i, check_type.__args__[0]) for i in var])
    if type(var) == tuple:
        return all([var_type_check(i,itype) for i, itype in zip(var, check_type.__args__)])
    if type(var) == dict:
        key_check = all([var_type_check(i, check_type.__args__[0]) for i in var.keys()])
        value_check = all([var_type_check(i, check_type.__args__[1]) for i in var.values()])
        return key_check and value_check
    return False

def function_type_test(func):
    anno_map = func.__annotations__.copy()
    if 'return' in anno_map:
        del anno_map['return']
    kwargs = {k: input_type_generator(v) for k,v in anno_map.items()}
    res = func(**kwargs)
    return result_type_test(func, res)

def result_type_test(func, res):
    if 'return' in func.__annotations__:
        return var_type_check(res, func.__annotations__['return'])
    return True