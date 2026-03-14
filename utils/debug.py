import configs.config as config

def dprint(msg):
    if config.DEBUG:
        print(msg)