from debug_toolbar.panels.logging import collector

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
      'simple': {
          'format': '{levelname} | {asctime} | {message}',
          'style': '{',
      }
    },
    'handlers': {
        'debug_handler': {
            'level': 'DEBUG',
            'class': 'debug_toolbar.panels.logging.ThreadTrackingHandler',
            'collector': collector
        },
        'info_handler': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'log/info.log',
            'formatter': 'simple'
        },
        'error_handler': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'log/errors.log',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'debug': {
            'handlers': ['debug_handler'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'info': {
            'handlers': ['info_handler'],
            'level': 'INFO',
            'propagate': True,
        },
        'error': {
            'handlers': ['error_handler'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

