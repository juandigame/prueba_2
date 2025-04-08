{
    'name': 'Rábanos Recomendaciones',
    'version': '1.0',
    'summary': 'Sistema de recomendaciones para cultivos de rábanos.',
    'author': 'Jaime Andres Villaneda Uribe',
    'website': 'https://jagesoft.com',
    'category': 'Agriculture',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/rabano_views.xml',
        'views/recomendacion_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}