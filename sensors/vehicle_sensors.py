#agr sim eu vou desisti, pq terminar isso aqui vai consumir mais da minha mente doq o de velocidade (q nem foi tao ruim assim)

#combustivel
FUEL_CAPACITY_LITERS = 50.0
FUEL_CONSUMPTION_BASE = 0.0008 # consumo base por tick (medido em litros (se minha matematica nao falhar na hr))
FUEL_CONSUMPTION_RPM_FACTOR = 0.0000006 #consumo extra por RPM
FUEL_LOW_WARNING = 15.0
TANK_RANGE_KM = 500.0 #autonomia com tank cheio (slk, esse carro andakkkkkk pqp 500km)

#temperatua do oleo (sempre medido em graus celcius)
TEMP_AMBIENT = 20.0
TEMP_NORMAL_MIN = 80.0
TEMP_NORMAL_MAX = 100.0
TEMP_WARNING = 110.0
TEMP_CRITICAL = 130.0
TEMP_HEAT_RATE = 12.0
TEMP_COOL_RATE = 4.0
TEMP_IDLE_HEAT = 1.5

class VehicleSensors:
    """
    Simula os sensores do veiculo:
    - Nivel de combustivel e autonomia
    - Temperatura do oleo
    """
    def update(self, state, delta_time):
        self._update_fuel(state, delta_time)
        self._update_oil_temp(state, delta_time)
        self._update_autonomy(state)
        self._check_alerts(state)
        
    # -----------------
    # Combustivel
    # -----------------
    def _update_fuel(self, state, delta_time):
        """
        Consome combustivel baseado em:
        - RPM atual
        - Acelerador
        - Marcha
        """
        if state.gear == 'N' and state.throttle < 0.01:
            #motor em idle no neutro - consumo minimo
            consumption = FUEL_CONSUMPTION_BASE * 0.3 * delta_time
        else:
            #consumo base + fator de RPM + fator de acelerador
            rpm_factor = state.rpm * FUEL_CONSUMPTION_RPM_FACTOR
            throttle_factor = 1.0 * (state.throttle * 2.5)
            consumption = (
                FUEL_CONSUMPTION_BASE +
                rpm_factor * throttle_factor
            ) * delta_time
        state.fuel = max(0.0, state.fuel - consumption)
    # -------------------------------
    # Autnomia
    # -------------------------------
    def _update_autonomy(self, state):
        """
        Estima a autonomia restante baseada no nive de combustivel
        """
        state.autonomy = (state.fuel / 100.0) * TANK_RANGE_KM
    # --------------------
    # Temperatura do Oleo
    # --------------------
    def _update_oil_temp(self, state, delta_time):
        """
        Aquece com uso e esfria quando o motor esta em idle ou desligado.
        A temperatura alvo depende do RPM e da carga do motor
        """
        # Temperatura alvo baseada no uso
        target_temp = _calculate_target_temp(state)
        if state.oil_temp < target_temp:
            # aquecendo
            heat = _heat_rate(state) * delta_time
            state.oil_temp = min(state.oil_temp + heat, target_temp)
        elif state.oil_temp > target_temp:
            #esfriando
            cool = TEMP_COOL_RATE * delta_time
            state.oil_temp = max(state.oil_temp - cool, target_temp)
        #limita aos extremos fisicos
        state.oil_temp = max(TEMP_AMBIENT, min(state.oil_temp, 150.0))
    # --------------------
    # Alertas
    # --------------------
    def _check_alerts(self, state):
        """Verifica limites e ativa alertas no CarState."""
        #alerta de combustivel baixo
        if state.fuel <= FUEL_LOW_WARNING:
            if 'fuel_low' not in state.faults:
                state.faults.append('fuel_low')
                print(f"\n ALERTA: Combustivel baixo! ({state.fuel:.1f}%)")
        else:
            if 'fuel_low' in state.faults:
                state.faults.remove('fuel_low')
        #alerta de temperatura alta
        if state.oil_temp >= TEMP_WARNING:
            state.oil_alert = True
            if 'oil_temp_high' not in state.faults:
                state.faults.append('oil_temp_high')
                print(f"\n ALERTA: TEmperatura do oleo alta! ({state.oil_temp:.1f}c)")
        else:
            state.oil_alert = False
            if 'oil_temp_high' in state.faults:
                state.faults.remove('oil_temp_high')
        #temperatura citica - check engine
        if state.oil_temp >= TEMP_CRITICAL:
            state.check_engine = True
            if 'oil_temp_critical' not in state.faults:
                state.faults.append('oil_temp_critical')
                print(f"\n CRITICO: Superaquecimento! ({state.oil_temp:.1f}c)")
        else:
            if 'oil_temp_critical' in state.faults:
                state.faults.remove('oil_temp_critical')
                if not state.faults:
                    state.check_engine = False
        # sem combustivel
        if state.fuel <= 0.0:
            if 'no_fuel' not in state.faults:
                state.faults.append('no_fuel')
                print("\n SEM COMBUSTIVEL! Motor parando...")
                
                
# -----------------------------
# Funcoes auxiliares
# -----------------------------
def _calculate_target_temp(state):
   """
   Calcula a temperatura alvo do óleo baseada no uso do motor.
   """
   rpm_ratio = (state.rpm - 800) / (7000 - 800)
   rpm_ratio = max(0.0, min(rpm_ratio, 1.0))
   # Em idle, tende à temperatura normal mínima
   if state.throttle < 0.05:
       return TEMP_NORMAL_MIN + (rpm_ratio * 10.0)
   # Acelerando, temperatura sobe proporcionalmente
   return TEMP_NORMAL_MIN + (
       (TEMP_NORMAL_MAX - TEMP_NORMAL_MIN + 20.0) *
       rpm_ratio * state.throttle
   )

def _heat_rate(state):
   """
   Calcula a taxa de aquecimento do óleo baseada no uso.
   """
   if state.throttle < 0.05:
       return TEMP_IDLE_HEAT
   rpm_ratio = (state.rpm - 800) / (7000 - 800)
   rpm_ratio = max(0.0, min(rpm_ratio, 1.0))
   return TEMP_HEAT_RATE * rpm_ratio * state.throttle