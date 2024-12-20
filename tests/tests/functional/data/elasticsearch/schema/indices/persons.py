from ..settings import settings_data

index_data = {
    'settings': settings_data,
    'mappings': {
        'dynamic': 'strict',
        'properties': {
            'id': {
                'type': 'keyword',
            },
            'full_name': {
                'type': 'text',
                'analyzer': 'ru_en',
            },
            'films': {
                'type': 'nested',
                'dynamic': 'strict',
                'properties': {
                    'id': {
                        'type': 'keyword',
                    },
                    'roles': {
                        'type': 'keyword',
                    },
                },
            },
        },
    },
}
