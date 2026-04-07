# engine/car_state.py
class CarState:
   """
   Representa o estado atual do veículo.
   Todos os módulos do sistema leem e escrevem aqui.
   """
   def __init__(self):
       # --- Movimento ---
       self.speed = 0.0           # Velocidade em km/h
       self.rpm = 0.0             # Rotações por minuto
       self.gear = 'N'            # Marcha atual: R, N, 1, 2, 3, 4, 5
       # --- Entradas do controle ---
       self.throttle = 0.0        # Acelerador: 0.0 a 1.0
       self.brake = 0.0           # Freio: 0.0 a 1.0
       # --- Sensores ---
       self.fuel = 100.0          # Combustível: 0.0 a 100.0 (%)
       self.oil_temp = 20.0       # Temperatura do óleo em °C
       self.autonomy = 500.0      # Autonomia estimada em km
       # --- Falhas e alertas ---
       self.faults = []           # Lista de falhas ativas
       self.check_engine = False  # Luz de check engine
       self.oil_alert = False     # Alerta de óleo
       # --- Sistema ---
       self.running = True        # O loop principal continua rodando?
   def __repr__(self):
       return (
           f"[CarState] "
           f"Marcha: {self.gear} | "
           f"RPM: {self.rpm:.0f} | "
           f"Vel: {self.speed:.1f} km/h | "
           f"Combustível: {self.fuel:.1f}% | "
           f"Temp Óleo: {self.oil_temp:.1f}°C"
       )