import logging.config
import logging
import os

path = os.path.abspath('../Logs/log.log')

try:
    os.mkdir('../Logs/')
    open(path, 'a').close()
except FileExistsError:
    pass

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'default_formatter': {
            'format': '[%(levelname)s:%(asctime)s][%(name)s] %(message)s'
        },
    },

    'handlers': {
        'stream_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'default_formatter',
            'level': 'DEBUG'
        },
        'rotating_files_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default_formatter',
            'filename': path,
            'encoding': 'UTF-8',
            'maxBytes': 1000000,
            'backupCount': 3,
            'level': 'INFO',
            'mode': 'w'
        },
    },

    'loggers': {
        'BOT': {
            'handlers': ['stream_handler', 'rotating_files_handler'],
            'propagate': True,
            'level': 'DEBUG'
        },
        'DATABASE': {
            'handlers': ['stream_handler', 'rotating_files_handler'],
            'propagate': True,
            'level': 'DEBUG'
        },
        'USER_HANDLERS': {
            'handlers': ['stream_handler', 'rotating_files_handler'],
            'propagate': True,
            'level': 'DEBUG'
        },
        'ADMIN_HANDLERS': {
            'handlers': ['stream_handler', 'rotating_files_handler'],
            'propagate': True,
            'level': 'DEBUG'
        },
        'DATABASE_QUERY': {
            'handlers': ['stream_handler', 'rotating_files_handler'],
            'propagate': True,
            'level': 'DEBUG'
        },
        'SCHEDULER': {
            'handlers': ['stream_handler', 'rotating_files_handler'],
            'propagate': True,
            'level': 'DEBUG'
        },
        'FACEBOOK_API': {
            'handlers': ['stream_handler', 'rotating_files_handler'],
            'propagate': True,
            'level': 'DEBUG'
        },
        'EWEBINAR_API': {
            'handlers': ['stream_handler', 'rotating_files_handler'],
            'propagate': True,
            'level': 'DEBUG'
        },
        'GETCOURSE_API': {
            'handlers': ['stream_handler', 'rotating_files_handler'],
            'propagate': True,
            'level': 'DEBUG'
        },

    }
}

logging.config.dictConfig(LOGGING_CONFIG)

bot_logger = logging.getLogger('BOT')
database_logger = logging.getLogger('DATABASE')
user_handlers_logger = logging.getLogger('USER_HANDLERS')
admin_handlers_logger = logging.getLogger('ADMIN_HANDLERS')
database_query_logger = logging.getLogger('DATABASE_QUERY')
scheduler_logger = logging.getLogger('SCHEDULER')
facebook_logger = logging.getLogger('FACEBOOK_API')
ewebinar_logger = logging.getLogger('EWEBINAR_API')
getcourse_logger = logging.getLogger('GETCOURSE_API')
