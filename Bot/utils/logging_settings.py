import logging.config
import logging
import os.path

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
            'filename': os.path.abspath('./Logs/log.log'),
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
        'HANDLERS': {
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
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)

bot_logger = logging.getLogger('BOT')
database_logger = logging.getLogger('DATABASE')
handlers_logger = logging.getLogger('HANDLERS')
database_query_logger = logging.getLogger('DATABASE_QUERY')
scheduler_logger = logging.getLogger('SCHEDULER')
