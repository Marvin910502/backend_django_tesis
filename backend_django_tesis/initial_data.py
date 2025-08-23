from backend_django_tesis.settings import BASE_DIR

admin_user = {
    'username': 'admin@cfa.cu',
    'password': '123456789',
    'is_admin': True,
    'is_guess': False,
    'is_manager': False,
    'department': 'Informática'
}

initial_content = {
    'site_title': 'CFA - Gestor de Archivos WRFout',
    'server_space': 50,
    'icon': f'{BASE_DIR}/static/default/cfa_logo_dark.png',
    'icon_name': 'cfa_logo_dark.png',
    'favicon': f'{BASE_DIR}/static/default/cfa_logo_dark.png',
    'favicon_name': 'cfa_logo_dark.png',
    'home_top_image': f'{BASE_DIR}/static/default/text-image.png',
    'home_top_image_name': 'text-image.png',
    'card_diagnostics_image': f'{BASE_DIR}/static/default/corte-vertical.png',
    'card_diagnostics_image_name': 'corte-vertical.png',
    'card_my_diagnostics_image': f'{BASE_DIR}/static/default/corte-vertical-3d.png',
    'card_my_diagnostics_image_name': 'corte-vertical-3d.png',
    'home_content': '<p>El Modelo WRF (Weather Research and Forecasting) ha emergido como una herramienta fundamental en la investigación atmosférica, brindando nuevas perspectivas en la comprensión de los fenómenos meteorológicos y climáticos. Desarrollado por el Centro Nacional de Investigación Atmosférica (NCAR) y colaboradores, el WRF ha transformado la manera en que abordamos la predicción del tiempo y los estudios climáticos.</p><p>&nbsp;</p><h4><strong>¿Qué es el Modelo WRF?:</strong>&nbsp;</h4><p>&nbsp;</p><p>El Modelo WRF es un sistema avanzado de modelado atmosférico que utiliza ecuaciones físicas y matemáticas para simular la dinámica de la atmósfera terrestre. Su capacidad para adaptarse a diferentes escalas, desde regiones locales hasta globales, y su enfoque de alta resolución espacial y temporal lo distinguen como una herramienta versátil y poderosa.</p><p>&nbsp;</p><h4><strong>Resolviendo Desafíos Atmosféricos:</strong>&nbsp;</h4><p>&nbsp;</p><p>El WRF aborda una amplia gama de desafíos atmosféricos, desde la predicción del tiempo a corto plazo hasta la investigación climática a largo plazo. Su capacidad para modelar fenómenos locales, como tormentas y vientos, con una precisión excepcional, ha mejorado significativamente la capacidad de los meteorólogos para anticipar eventos extremos.</p><p>&nbsp;</p><h4><strong>Aplicaciones y Utilidad:</strong></h4><p>&nbsp;</p><p><i><strong>Pronóstico Meteorológico Avanzado:</strong></i> El WRF proporciona pronósticos meteorológicos precisos y detallados, siendo utilizado por agencias meteorológicas para emitir alertas tempranas y mejorar la gestión de situaciones de emergencia.</p><p><i><strong>Investigación Climática:</strong></i> En la investigación climática, el WRF permite simular cambios climáticos a escalas regionales, proporcionando información crucial para comprender patrones climáticos y evaluar posibles escenarios futuros.</p><p><i><strong>Energías Renovables:</strong></i> La energía eólica y solar se benefician de simulaciones precisas de condiciones atmosféricas locales, permitiendo una planificación más efectiva de proyectos energéticos sostenibles.</p><p><i><strong>Agricultura:</strong></i> Los agricultores utilizan el WRF para obtener pronósticos climáticos detallados que influyen en las prácticas agrícolas, desde la siembra hasta la cosecha.</p>',
    'card_diagnostics': '<p>En esta sección se podrán obtener diferentes tipos de diagnósticos en forma de mapas y gráficas en 3d</p>',
    'card_my_diagnostics': '<p>Aquí puedes consultar los diagnósticos que hayas guardado directo de la base de datos sin necesidad de un archivo WRFout</p>',
    'help_content': '<h3>¿Cómo usar nuestra herramienta?</h3><p>&nbsp;</p><h4>Obtener diagnóstico a partir archivo(s) WRFout:</h4><p>&nbsp;</p><ol><li>Acceder a la pestaña de <strong>Diagnosticos</strong> &nbsp;a la izquierda.</li><li>En esta pestaña encontrará dos tipos de salidas de diagnósticos en la parte superior, mapas y gráficas en 3D.</li><li>Para optener estas salidas se necesita primero hacer click en la sección de <strong>Opciones</strong> en el botón de <strong>Seleccionar Archivo(s).</strong></li><li>Del listado de archivos que aparece seleccionar uno o más marcando los checkboxs y luego hacer click en el botón <strong>Cargar Archivo(s)</strong>.</li><li>Automaticamente se mostrarán las salidas del diagnóstico con la configuración por defecto.</li></ol><p>&nbsp;</p><h4>Obtener diferentes diagnósticos:</h4><h4>&nbsp;</h4><p>Para obtener diferentes diagnósticos solo necesita utilizar el <strong>Selector de Diagnósticos </strong>en la sección de <strong>Opciones</strong>, en este momento contamos con 9 diagnósticos diferentes.</p><p>&nbsp;</p><h4>Variar la unidad de medida del diagnóstico:</h4><p>&nbsp;</p><p>Justo debajo del Selector de Diagnósticos se encuentra el <strong>Selector de Unidades</strong>, este selector cambia sus opciones en base al diagnóstico seleccionado, algunos diagnósticos solo contienen solo un tipo de unidad.</p><p>&nbsp;</p><h4>Variar número de polígonos:</h4><p>&nbsp;</p><p>En la sección de <strong>Opciones</strong> por ultimo encontraremos un deslizador con un rango que va del 5 al 15, este nos permitirá indicar la cantidad de polígonos que seran dibujados sobre el mapa.&nbsp;</p><p>&nbsp;</p>'
}

palettes  = [
    {
        'label': 'RdYlBu',
        'type': 'map'
    },
    {
        'label': 'viridis',
        'type': 'map'
    },
    {
        'label': 'plasma',
        'type': 'map'
    },
    {
        'label': 'inferno',
        'type': 'map'
    },
    {
        'label': 'magma',
        'type': 'map'
    },
    {
        'label': 'cividis',
        'type': 'map'
    },
    {
        'label': 'Greys',
        'type': 'map'
    },
    {
        'label': 'Purples',
        'type': 'map'
    },
    {
        'label': 'Blues',
        'type': 'map'
    },
    {
        'label': 'Greens',
        'type': 'map'
    },
    {
        'label': 'Oranges',
        'type': 'map'
    },
    {
        'label': 'Reds',
        'type': 'map'
    },
    {
        'label': 'YlOrBr',
        'type': 'map'
    },
    {
        'label': 'YlOrRd',
        'type': 'map'
    },
    {
        'label': 'OrRd',
        'type': 'map'
    },
    {
        'label': 'PuRd',
        'type': 'map'
    },
    {
        'label': 'RdPu',
        'type': 'map'
    },
    {
        'label': 'BuPu',
        'type': 'map'
    },
    {
        'label': 'GnBu',
        'type': 'map'
    },
    {
        'label': 'PuBu',
        'type': 'map'
    },
    {
        'label': 'YlGnBu',
        'type': 'map'
    },
    {
        'label': 'PuBuGn',
        'type': 'map'
    },
    {
        'label': 'YlGn',
        'type': 'map'
    },
    {
        'label': 'PiYG',
        'type': 'map'
    },
    {
        'label': 'PRGn',
        'type': 'map'
    },
    {
        'label': 'BrBG',
        'type': 'map'
    },
    {
        'label': 'PuOr',
        'type': 'map'
    },
    {
        'label': 'RdGy',
        'type': 'map'
    },
    {
        'label': 'RdBu',
        'type': 'map'
    },
    {
        'label': 'RdYlGn',
        'type': 'map'
    },
    {
        'label': 'Spectral',
        'type': 'map'
    },
    {
        'label': 'coolwarm',
        'type': 'map'
    },
    {
        'label': 'bwr',
        'type': 'map'
    },
    {
        'label': 'seismic',
        'type': 'map'
    },
    {
        'label': 'twilight_shifted',
        'type': 'map'
    },
    {
        'label': 'hsv',
        'type': 'map'
    },
    {
        'label': 'Pastel1',
        'type': 'map'
    },
    {
        'label': 'Paired',
        'type': 'map'
    },
    {
        'label': 'Accent',
        'type': 'map'
    },
    {
        'label': 'Dark2',
        'type': 'map'
    },
    {
        'label': 'Set1',
        'type': 'map'
    },
    {
        'label': 'tab10',
        'type': 'map'
    },
    {
        'label': 'Blackbody',
        'type': '3d_graphic'
    },
    {
        'label': 'Bluered',
        'type': '3d_graphic'
    },
    {
        'label': 'Blues',
        'type': '3d_graphic'
    },
    {
        'label': 'Earth',
        'type': '3d_graphic'
    },
    {
        'label': 'Electric',
        'type': '3d_graphic'
    },
    {
        'label': 'Greens',
        'type': '3d_graphic'
    },
    {
        'label': 'Greys',
        'type': '3d_graphic'
    },
    {
        'label': 'Hot',
        'type': '3d_graphic'
    },
    {
        'label': 'Jet',
        'type': '3d_graphic'
    },
    {
        'label': 'Picnic',
        'type': '3d_graphic'
    },
    {
        'label': 'Portland',
        'type': '3d_graphic'
    },
    {
        'label': 'Rainbow',
        'type': '3d_graphic'
    },
    {
        'label': 'RdBu',
        'type': '3d_graphic'
    },
    {
        'label': 'Reds',
        'type': '3d_graphic'
    },
    {
        'label': 'Viridis',
        'type': '3d_graphic'
    },
    {
        'label': 'YlGnBu',
        'type': '3d_graphic'
    },
    {
        'label': 'YlOrRd',
        'type': '3d_graphic'
    },
    {
        'label': 'Plasma',
        'type': '3d_graphic'
    },
    {
        'label': 'Cividis',
        'type': '3d_graphic'
    }
]

units = [
    {
        'id': 1,
        'name': 'Grados por Celsius',
        'symbol': 'degC'
    },
    {
        'id': 2,
        'name': 'Grados por Fahrenheit',
        'symbol': 'degF'
    },
    {
        'id': 3,
        'name': 'Kelvin',
        'symbol': 'K'
    },
    {
        'id': 4,
        'name': 'Metros',
        'symbol': 'm'
    },
    {
        'id': 5,
        'name': 'Kilometros',
        'symbol': 'km'
    },
    {
        'id': 6,
        'name': 'Decímetros',
        'symbol': 'dm'
    },
    {
        'id': 7,
        'name': 'Pies',
        'symbol': 'ft'
    },
    {
        'id': 8,
        'name': 'Millas',
        'symbol': 'mi'
    },
    {
        'id': 9,
        'name': 'Metros Cuadrados',
        'symbol': 'm2'
    },
    {
        'id': 10,
        'name': 'Kilogramos',
        'symbol': 'kg'
    },
    {
        'id': 11,
        'name': 'Porcentaje',
        'symbol': '%'
    },
    {
        'id': 12,
        'name': 'Pascales',
        'symbol': 'Pa'
    },
    {
        'id': 13,
        'name': 'Hectopascales',
        'symbol': 'hPa'
    },
    {
        'id': 14,
        'name': 'Milibares',
        'symbol': 'mb'
    },
    {
        'id': 15,
        'name': 'Centímetros de Mercurio',
        'symbol': 'torr'
    },
    {
        'id': 16,
        'name': 'Milímetros de Mercurio',
        'symbol': 'mmhg'
    },
    {
        'id': 17,
        'name': 'Atmosferas',
        'symbol': 'atm'
    }
]

diagnostic_types = [
    {
        'name': 'Punto de Condensación',
        'value': 'td2',
        'unit_ids': [1, 2, 3]
    },
    {
        'name': 'Humedad Relativa',
        'value': 'rh2',
        'unit_ids': [10]
    },
    {
        'name': 'Altura del Terreno',
        'value': 'ter',
        'unit_ids': [4, 5, 6, 7, 8]
    },
    {
        'name': 'Temperatura Superior de las Nubes',
        'value': 'ctt',
        'unit_ids': [1, 2, 3]
    },
    {
        'name': 'Temperatura',
        'value': 'T2',
        'unit_ids': [3]
    },
    {
        'name': 'Helicidad Relativa de Tormenta',
        'value': 'helicity',
        'unit_ids': [9]
    },
    {
        'name': 'Agua Precipitable',
        'value': 'pw',
        'unit_ids': [10]
    },
    {
        'name': 'Presión a Nivel del Mar',
        'value': 'slp',
        'unit_ids': [12, 13, 14, 15, 16, 17]
    },
    {
        'name': 'Helicidad de Corriente Ascendente',
        'value': 'updraft_helicity',
        'unit_ids': [9]
    }
]
