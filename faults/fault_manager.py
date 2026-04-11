import random
from faults.fault_definitions import FAULT_CATALOG

# Chance de uma falha aleatória surgir por minuto (0.0 = desligado)
RANDOM_FAULT_CHANCE = 0.0   # Desligado por padrão, ativado via painel

# Multiplicador de consumo de combustível durante vazamento
FUEL_LEAK_MULTIPLIER = 5.0

# Redução de eficiência do freio durante falha (0.0 a 1.0)
BRAKE_FAILURE_FACTOR = 0.3

# Redução de RPM durante falha de ignição
MISFIRE_RPM_DROP = 800.0

# Temperatura forçada durante superaquecimento
OVERHEAT_TEMP_RISE = 25.0 


class FaultManager:
    """
    Gerencia todas as falhas do veículo.
    - Ativa e desativa falhas manualmente
    - Aplica impacto de cada falha no CarState
    - Suporta falhas aleatórias opcionais
    """

    def __init__(self):
        self.active_faults = {}     # {fault_id: fault_definition}
        self._random_timer = 0.0   # Acumulador para falhas aleatórias

    # -----------------------
    # Ativação e desativação
    # -----------------------
    
    def activate(self, fault_id):
        """Ativa uma falha pelo seu ID."""
        if fault_id not in FAULT_CATALOG:
            print(f"\n Falha desconhecida: {fault_id}")
            return False

        if fault_id in self.active_faults:
            return False

        fault = FAULT_CATALOG[fault_id]
        self.active_faults[fault_id] = fault
        print(f"\n FALHA ATIVADA: {fault['name']} [{fault['severity'].upper()}]")
        return True

    def deactivate(self, fault_id):
        """Desativa uma falha pelo seu ID."""
        if fault_id in self.active_faults:
            fault = self.active_faults.pop(fault_id)
            print(f"\n FALHA RESOLVIDA: {fault['name']}")
            return True
        return False

    def deactivate_all(self):
        """Remove todas as falhas ativas."""
        self.active_faults.clear()
        print("\n Todas as falhas foram resolvidas.")

    def is_active(self, fault_id):
        return fault_id in self.active_faults

    def list_active(self):
        return list(self.active_faults.values())

    # ----------------------
    # Atualização principal
    # ----------------------

    def update(self, state, delta_time):
        """
        Chamado a cada tick.
        Aplica os efeitos das falhas ativas no CarState.
        """
        
        # Sincroniza lista de falhas no CarState
        state.faults = list(self.active_faults.keys())

        # Aplica impacto de cada falha ativa
        for fault_id in list(self.active_faults.keys()):
            self._apply_fault(fault_id, state, delta_time)

        # Check engine ativo se há falha crítica
        critical = any(
            f['severity'] == 'critical'
            for f in self.active_faults.values()
        )
        state.check_engine = critical

        # Falhas aleatórias (se habilitadas)
        if RANDOM_FAULT_CHANCE > 0:
            self._try_random_fault(delta_time)

    # ----------------------
    # Impacto das falhas
    # ----------------------

    def _apply_fault(self, fault_id, state, delta_time):
        """Aplica o efeito específico de cada falha."""

        if fault_id == 'sensor_rpm':
            # RPM exibido como zero (leitura falha)
            state.rpm = 0.0

        elif fault_id == 'sensor_speed':
            # Velocímetro congela em valor aleatório
            state.speed = state.speed * random.uniform(0.0, 1.5)

        elif fault_id == 'sensor_fuel':
            # Combustível exibido errado (flutua)
            state.fuel = max(0.0, state.fuel + random.uniform(-5.0, 5.0))

        elif fault_id == 'engine_overheat':
            # Temperatura sobe rapidamente, RPM e velocidade caem
            state.oil_temp = min(150.0, state.oil_temp + OVERHEAT_TEMP_RISE * delta_time)
            state.rpm = max(800.0, state.rpm * 0.95)
            state.speed = max(0.0, state.speed * 0.98)
            state.oil_alert = True

        elif fault_id == 'engine_misfire':
            # RPM cai intermitentemente (falha de ignição)
            if random.random() < 0.3:   # 30% de chance por tick
                state.rpm = max(800.0, state.rpm - MISFIRE_RPM_DROP)
                state.speed = max(0.0, state.speed - 2.0)

        elif fault_id == 'brake_failure':
            # Freio com eficiência reduzida
            state.brake = state.brake * BRAKE_FAILURE_FACTOR

        elif fault_id == 'fuel_leak':
            # Consume combustível muito mais rápido
            extra = 0.05 * FUEL_LEAK_MULTIPLIER * delta_time
            state.fuel = max(0.0, state.fuel - extra)

        elif fault_id == 'transmission_fault':
            # Câmbio travado — não deixa trocar marcha
            # O bloqueio real é feito no Gearbox via is_active()
            pass

    # ------------------------------------------------------------------
    # Falhas aleatórias
    # ------------------------------------------------------------------

    def _try_random_fault(self, delta_time):
        """Tenta ativar uma falha aleatória baseado na chance configurada."""
        self._random_timer += delta_time

        # Verifica a cada 60 segundos
        if self._random_timer >= 60.0:
            self._random_timer = 0.0
            if random.random() < RANDOM_FAULT_CHANCE:
                available = [
                    fid for fid in FAULT_CATALOG
                    if fid not in self.active_faults
                ]
                if available:
                    chosen = random.choice(available)
                    self.activate(chosen)