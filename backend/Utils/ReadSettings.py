import json

SETTINGS_FILE = 'appsettings.json'

def load_settings():
    try:
        with open(SETTINGS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("Файл не найден")
        return None
    except json.JSONDecodeError:
        print("Ошибка парсинга JSON")
        return None

def get_environment():
    settings = load_settings()
    if isinstance(settings, dict) and 'Environment' in settings:
        return settings['Environment']
    return 'Environment'  # Значение по умолчанию

def load_environment_specific_settings():
    environment = get_environment()
    specific_settings_file = f'appsettings.{environment}.json'
    
    try:
        with open(specific_settings_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Файл настроек для окружения '{environment}' не найден")
        return None
    except json.JSONDecodeError:
        print("Ошибка парсинга JSON в файле окружения")
        return None

def get_setting(key):
    # Загружаем основные настройки
    settings = load_settings()
    # Загружаем специфические настройки для окружения
    env_settings = load_environment_specific_settings()
    
    # Объединяем настройки
    if isinstance(settings, dict):
        if env_settings and isinstance(env_settings, dict):
            settings.update(env_settings)

        if key in settings:
            return settings[key]
        else:
            for value in settings.values():
                if isinstance(value, dict):
                    result = get_setting(key)
                    if result is not None:
                        return result
    return None
