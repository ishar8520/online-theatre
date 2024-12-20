from ..settings import settings_data

index_data = {
    'settings': settings_data,
    'mappings': {
        'dynamic': 'strict',
        'properties': {
            'id': {
                'type': 'keyword',
            },
            'name': {
                'type': 'keyword',
            },
        },
    },
}
