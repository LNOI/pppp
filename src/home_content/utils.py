from src.const.global_map import HOME_COMPONENT_MAP
def register_home_component(component_name):
    def register(cls):
        HOME_COMPONENT_MAP[component_name] = cls
        return cls
    return register