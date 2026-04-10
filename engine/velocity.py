#aqui e onde o filho chora, a mae v e chora junto
#velocidade maxima por marcha (km/h)
MAX_SPEED_PER_GEAR = {
    'R': 30.0,
    'N': 0,
    '1': 40.0,
    '2': 80.0,
    '3': 120.0,
    '4': 160.0,
    '5': 220.0,
}

#fator de aceleracao por marcha (quanto a marcha empurra o carro)
ACCELERATION_FACTOR = {
    'R': 0.4,
    'N': 0.0,
    '1': 1.0,
    '2': 0.85,
    '3': 0.70,
    '4': 0.55,
    '5': 0.40,
}

#forca de frenagem
BRAKE_FORCE = 80.0
# resistencia natural do carro (atrito/arrasto) em km/h por segundo
DRAG_FORCE = 8.0
#forca de frenagem do motor (ao soltar o acelerador em marcha)
ENGINE_BRAKE_FORCE = 15.0


class Velocity:
    """
    Simula a velocidade do veiculo baseado em RPM, marcha, acelerador, freio e resistencia fisicas.
    """
    def update(self, state, delta_time):
        """
        Atualiza a velocidade no CarState a cada tick
        """
        gear = state.gear
        # neutro: so desacelera, nao propulsiona
        if gear == 'N':
            state.speed = _apply_drag(state.speed, DRAG_FORCE, delta_time)
            state.speed = _apply_brake(state.speed, state.brake, delta_time)
            return
        #durante troca de marcha: sem propulsao
        if state.shifting:
            state.speed = _apply_drag(state.speed, DRAG_FORCE, delta_time)
            state.speed = _apply_brake(state.speed, state.brake, delta_time)
            return
        max_speed = MAX_SPEED_PER_GEAR.get(gear, 0.0)
        accel_factor = ACCELERATION_FACTOR.get(gear, 0.0)
        #re: velocidade negativa representada como positiva
        if gear == 'R':
            _update_reverse(state, delta_time, max_speed, accel_factor)
            return
        #marchas 1 a 5
        _update_forward(state, delta_time, max_speed, accel_factor)
        
def _update_forward(state, delta_time, max_speed, accel_factor):
    """Logica de aceleracao para marchas 1 a 5"""
    throttle = state.throttle
    if throttle > 0.01:
        #calcula velocidade alvo baseada no RPM e marcha
        rpm_ratio = (state.rpm - 800) / (7000 - 800) # 0.0 a 1.0
        rpm_ratio = max(0.0, min(rpm_ratio, 1.0))
        target_speed = max_speed * rpm_ratio * throttle * accel_factor
        # so acelera se ainda nao chegou no alvo
        if state.speed < target_speed:
            accel = accel_factor * 40.0 * throttle * delta_time
            state.speed = min(state.speed + accel, max_speed)
    else:
        #sem acelerador: freio de motor + arrasto
        state.speed = _apply_drag(
            state.speed,
            ENGINE_BRAKE_FORCE + DRAG_FORCE,
            delta_time
        )
    #aplca freio por cima de tudo
    state.speed = _apply_brake(state.speed, state.brake, delta_time)
    #garante limites
    state.speed = max(0.0, min(state.speed, max_speed))
    
def _update_reverse(state, delta_time, max_speed, accel_factor):
    """Logica de aceleracao para re"""
    if state.throttle > 0.01:
        accel = accel_factor * 20.0 * state.throttle * delta_time
        state.speed = min(state.speed + accel, max_speed)
    else:
        state.speed = _apply_drag(state.speed, DRAG_FORCE, delta_time)
    state.speed = _apply_brake(state.speed, state.brake, delta_time)
    state.speed = max(0.0, min(state.speed, max_speed))
    
def _apply_drag(speed, drag, delta_time):
    """aplica resistencia natual, desacelera o carro gradualmente"""
    redution = drag * delta_time
    return max(0.0, speed - redution)

def _apply_brake(speed, brake_input, delta_time):
    """Aplica forca de frenagem proporcional ao pedal."""
    if brake_input > 0.01:
        redution = BRAKE_FORCE * brake_input * delta_time
        return max(0.0, speed - redution)
    return speed
            