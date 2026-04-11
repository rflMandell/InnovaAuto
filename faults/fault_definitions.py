"""
Catálogo de todas as falhas possíveis do InnovaAuto.
Cada falha tem:
  - id:          identificador único
  - name:        nome amigável
  - description: o que representa
  - severity:    'low', 'medium', 'critical'
  - affects:     quais sistemas impacta
"""

FAULT_CATALOG = {

    # --- Sensor ---
    'sensor_rpm': {
        'id':          'sensor_rpm',
        'name':        'Falha no Sensor de RPM',
        'description': 'Leitura de RPM incorreta ou zerada',
        'severity':    'medium',
        'affects':     ['rpm'],
    },

    'sensor_speed': {
        'id':          'sensor_speed',
        'name':        'Falha no Sensor de Velocidade',
        'description': 'Velocímetro apresenta leitura incorreta',
        'severity':    'medium',
        'affects':     ['speed'],
    },

    'sensor_fuel': {
        'id':          'sensor_fuel',
        'name':        'Falha no Sensor de Combustível',
        'description': 'Nível de combustível não confiável',
        'severity':    'low',
        'affects':     ['fuel'],
    },

    # --- Motor ---
    'engine_overheat': {
        'id':          'engine_overheat',
        'name':        'Superaquecimento do Motor',
        'description': 'Temperatura crítica — risco de dano ao motor',
        'severity':    'critical',
        'affects':     ['oil_temp', 'rpm', 'speed'],
    },

    'engine_misfire': {
        'id':          'engine_misfire',
        'name':        'Falha de Ignição',
        'description': 'Motor falhando — perda de potência intermitente',
        'severity':    'medium',
        'affects':     ['rpm', 'speed'],
    },

    # --- Freio ---
    'brake_failure': {
        'id':          'brake_failure',
        'name':        'Falha no Sistema de Freio',
        'description': 'Freios com eficiência reduzida',
        'severity':    'critical',
        'affects':     ['brake'],
    },

    # --- Combustível ---
    'fuel_leak': {
        'id':          'fuel_leak',
        'name':        'Vazamento de Combustível',
        'description': 'Consumo de combustível muito acima do normal',
        'severity':    'critical',
        'affects':     ['fuel'],
    },

    # --- Transmissão ---
    'transmission_fault': {
        'id':          'transmission_fault',
        'name':        'Falha na Transmissão',
        'description': 'Câmbio travado na marcha atual',
        'severity':    'medium',
        'affects':     ['gear'],
    },
}