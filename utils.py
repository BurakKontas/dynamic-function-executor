import builtins
import datetime
import inspect
import json
import traceback
from typing import Callable, List, Literal, get_args, get_origin, get_type_hints
from inspect import signature, isclass, isfunction
import os
import importlib
import sys

from entities import DynamicFunction, DynamicSettings

PRIMAL_TYPES = {int, str, float, bool, list, dict, tuple, set}

def constructor_parameter_analyzer(cls, level=1):
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


def get_all_functions(functions_folder='functions') -> List[DynamicFunction]:
    all_functions = []

    # Eğer tam bir yol verilmişse, dizini sys.path'a ekle
    if not os.path.exists(functions_folder):
        print(f"Folder {functions_folder} does not exist.", severity="WARNING")
        return all_functions

    # Eğer 'functions_folder' bir tam dosya yolu ise, uygun şekilde işle
    if os.path.isdir(functions_folder):
        folder_path = functions_folder
    else:
        print(f"{functions_folder} is not a valid directory.", severity="WARNING")
        return all_functions

    sys.path.append(folder_path)

    for filename in os.listdir(folder_path):
        if filename.endswith('.py'):
            module_name = filename[:-3]

            # Modülü temizleyip yeniden yükleyelim
            if module_name in sys.modules:
                del sys.modules[module_name]

            try:
                module = importlib.import_module(module_name)
                importlib.reload(module)

                for attribute_name in dir(module):
                    attribute = getattr(module, attribute_name)
                    if isfunction(attribute):
                        # Varsayılan settings oluştur
                        settings = DynamicSettings(
                            name=attribute.__name__,
                            enabled=True,
                            description=None
                        )

                        # Modülde bir settings dict var mı kontrol et
                        if hasattr(module, "settings") and isinstance(module.settings, dict):
                            module_settings = module.settings
                            settings.name = module_settings.get("name", attribute.__name__)
                            settings.enabled = module_settings.get("enabled", True)
                            settings.description = module_settings.get("description", None)

                        # DynamicFunction nesnesi ekle
                        dynamic_function = DynamicFunction(
                            func=attribute,
                            settings=settings
                        )
                        all_functions.append(dynamic_function)
                        print(f"Function {attribute.__name__} imported successfully.", severity="INFO")
                        print(f"Function {attribute.__name__} settings: {settings}", severity="INFO")

            except Exception as e:
                print(f"Error importing module {module_name}: {e}", severity="ERROR")

    return all_functions


# Severity seviyeleri için renkler
severity_colors = {
    'INFO': '\033[34m',  # Mavi
    'WARNING': '\033[33m',  # Sarı
    'ERROR': '\033[31m',  # Kırmızı
    'DEBUG': '\033[32m',  # Yeşil
    'RESET': '\033[0m',  # Renk sıfırlama
    'CRITICAL': '\033[41m'  # Kırmızı arka plan
}


def print(*args, severity: str = "INFO", **kwargs):
    stack = traceback.extract_stack()
    filename, lineno, _, _ = stack[-2]

    # Log folder from settings, default is "logs"
    log_folder = "logs"
    log_folder = load_settings(key="logs", default_value=log_folder)

    # Create the log folder if it doesn't exist
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    # Prepare the timestamp and log file name
    timestamp = datetime.datetime.now().strftime("%d-%m-%Y_%H")
    log_filename = os.path.join(log_folder, f"logs_{timestamp}.txt")

    # Get relative filename
    relative_filename = os.path.relpath(filename)

    # Construct the log message
    message = f"[{severity}] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] " \
        f"{relative_filename} -> line {lineno}: " + " ".join(map(str, args))

    # Print the message in the console with color based on severity
    # Default to INFO color if not found
    color = severity_colors.get(severity, severity_colors['INFO'])
    builtins.print(f"{color}{message}{severity_colors['RESET']}", **kwargs)

    # Write the message to the log file
    with open(log_filename, "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")
        log_file.flush()

def convert_to_class_instance(cls, data):
    if not hasattr(cls, '__annotations__'):  
        return data  # Eğer cls bir sınıf değilse (örneğin dict ise) direkt geri döndür
    
    annotations = cls.__annotations__
    kwargs = {}

    for field, field_type in annotations.items():
        origin_type = get_origin(field_type)
        
        # Varsayılan değer belirleme
        if origin_type == list:
            default_value = []
        elif origin_type == dict:
            default_value = {}
        elif origin_type == tuple:
            default_value = tuple()
        elif origin_type == set:
            default_value = set()
        else:
            default_value = None  # Diğer türler için

        field_value = data.get(field, default_value)  # UI’den değer gelmezse varsayılanı kullan
        
        # Eğer iç içe geçmiş bir sınıf varsa
        if inspect.isclass(field_type) and isinstance(field_value, dict):
            kwargs[field] = convert_to_class_instance(field_type, field_value)

        # Eğer liste (List[T]) ise
        elif origin_type == list:
            item_type = get_args(field_type)[0]
            if inspect.isclass(item_type) and isinstance(field_value, list):
                kwargs[field] = [convert_to_class_instance(item_type, item) for item in field_value]
            else:
                kwargs[field] = field_value  # Doğrudan ata

        # Eğer tuple (Tuple[T1, T2, ...]) ise
        elif origin_type == tuple:
            item_types = get_args(field_type)
            if all(inspect.isclass(item_type) for item_type in item_types) and isinstance(field_value, tuple):
                kwargs[field] = tuple(
                    convert_to_class_instance(item_type, item) for item_type, item in zip(item_types, field_value)
                )
            else:
                kwargs[field] = field_value  # Doğrudan ata

        # Eğer dict (Dict[K, V]) ise
        elif origin_type == dict:
            key_type, value_type = get_args(field_type)
            if inspect.isclass(value_type) and isinstance(field_value, dict):
                kwargs[field] = {k: convert_to_class_instance(value_type, v) for k, v in field_value.items()}
            else:
                kwargs[field] = field_value  # Doğrudan ata
        
        else:
            kwargs[field] = field_value  # Diğer durumlarda doğrudan ata
    
    return cls(**kwargs)

def convert_to_serializable(obj):
    if isinstance(obj, (dict, list, tuple, set)):
        return type(obj)(convert_to_serializable(item) for item in obj)
    elif hasattr(obj, 'to_dict'):
        return obj.to_dict()
    else:
        return obj
    

def load_settings(key=None, default_value=None, path="settings.json", ):
    if not os.path.exists(path):
        default_settings = {
            "functions_path": "examples",  # Default value
            "css_path": "style.css",      # Default value
            "log_folder": "logs"          # Default value
        }
        with open(path, "w") as file:
            json.dump(default_settings, file, indent=4)
        print("Settings file created with default values.")

    # Load the settings from the file
    with open(path, "r") as file:
        settings = json.load(file)

    # Return the entire settings dictionary or a specific key if provided
    return settings.get(key, default_value) if key else settings
