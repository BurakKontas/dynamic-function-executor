import builtins
import traceback
from typing import Callable, get_type_hints
from inspect import signature, isclass, isfunction
import os
import importlib

PRIMAL_TYPES = {int, str, float, bool, list, dict, tuple, set}

def constructor_parameter_analyzer(cls, level=1):
    """Analyzes the constructor (__init__) parameters of a class and checks nested classes as well."""
    ctor_sign = signature(cls.__init__)
    type_hints = get_type_hints(cls.__init__)

    constructor_parameters = []
    for param_name, param in ctor_sign.parameters.items():
        if param_name == "self":
            continue

        param_type = type_hints.get(param_name, "Unknown")
        type_name = getattr(param_type, '__name__', param_type)

        if hasattr(param_type, '__args__'):
            if hasattr(param_type, '__origin__') and param_type.__origin__ in [list, tuple, set, dict]:
                param_collection_type = param_type.__origin__
                param_inner_type = param_type.__args__[0] if param_collection_type in [list, tuple, set] else param_type.__args__
                inner_type_name = getattr(param_inner_type, '__name__', str(param_inner_type))

                if isinstance(param_inner_type, type) and not param_inner_type in PRIMAL_TYPES:
                    inner_class_details = constructor_parameter_analyzer(param_inner_type, level + 1)
                    constructor_parameters.append(f"{param_name}: {param_collection_type.__name__}[{inner_class_details}]")
                else:
                    constructor_parameters.append(f"{param_name}: {param_collection_type.__name__}[{inner_type_name}]")
            else:
                constructor_parameters.append(f"{param_name}: {type_name}")
        elif isclass(param_type) and param_type not in PRIMAL_TYPES:
            nested_parameters = constructor_parameter_analyzer(param_type, level + 1)
            constructor_parameters.append(f"{param_name}: {type_name} ({nested_parameters})")
        else:
            constructor_parameters.append(f"{param_name}: {type_name}")

    return ", ".join(constructor_parameters) if constructor_parameters else "None"


def print_function_parameters(funk: Callable) -> None:
    """Prints the parameters of a function and the constructor parameters of any nested classes."""
    sign = signature(funk)
    type_hints = get_type_hints(funk)

    print(f"Function name: {funk.__name__}")
    for param_name, param in sign.parameters.items():
        param_type = type_hints.get(param_name, "Unknown")

        if isclass(param_type) and param_type not in PRIMAL_TYPES:
            constructor_parameters = constructor_parameter_analyzer(param_type)
            print(f"Parameter: {param_name}, Class: {param_type.__name__}, Constructor Parameters: {constructor_parameters}")
        else:
            print(f"Parameter: {param_name}, Type: {getattr(param_type, '__name__', param_type)}")


def get_all_functions(functions_folder='functions'):
    all_functions = []

    for filename in os.listdir(functions_folder):
        if filename.endswith('.py'):
            module_name = filename[:-3]

            module = importlib.import_module(f'{functions_folder}.{module_name}')

            if hasattr(module, module_name):
                func = getattr(module, module_name)
                if isfunction(func):
                    all_functions.append(func)
                    print(f"Found function: {module_name} in module {module_name}")

    return all_functions


def print(*args, **kwargs):
    stack = traceback.extract_stack()
    filename, lineno, _, _ = stack[-2]
    
    builtins.print(f"Print called from {filename}, line {lineno}: ", *args, **kwargs)


import inspect
from typing import get_origin, get_args

def convert_to_class_instance(cls, data):
    # Sınıfın __annotations__ özelliğini kullanarak alanları ve tiplerini al
    annotations = cls.__annotations__

    # Sınıfın parametrelerini hazırla
    kwargs = {}
    for field, field_type in annotations.items():
        if field in data:
            # Eğer alanın tipi bir sınıfsa ve veri bir sözlükse, recursive olarak dönüştür
            if inspect.isclass(field_type) and isinstance(data[field], dict):
                kwargs[field] = convert_to_class_instance(field_type, data[field])
            # Eğer alanın tipi bir liste ise ve elemanlar sınıf tipindeyse, liste elemanlarını dönüştür
            elif get_origin(field_type) == list:  # typing.List gibi türler için
                item_type = get_args(field_type)[0]  # Listenin içindeki türü al
                if inspect.isclass(item_type) and isinstance(data[field], list):
                    kwargs[field] = [convert_to_class_instance(item_type, item) for item in data[field]]
            else:
                # Diğer durumlarda doğrudan ata
                kwargs[field] = data[field]
    
    # Sınıfın bir örneğini oluştur ve döndür
    return cls(**kwargs)