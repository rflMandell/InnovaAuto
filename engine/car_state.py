class CarState:
    """
    Representa o estado atual do veiculo.
    Todos os modulos do sistema leem e escrevem
    """
    
    def __init__(self):
        #Movimento
        self.speed = 0.0 
        self.rpm = 800.0
        self.gear = 'N' # N, 1, 2, 3, 4, 5
        self.shifting = False
        
        # Entrada do controle
        self.throttle = 0.0 # 0.0 -> 1.0
        self.brake = 0.0 # 0.0 -> 1.0
        
        # sensores
        self.fuel = 100.0 # 0 -> 100%
        self.oil_temp = 20.0
        self.autonomy = 500.0 # 0 -> inf.
        
        # falhas
        self.faults = [] #flahas ativas
        self.check_engine = False
        self.oil_alert = False
        
        # sistema
        self.running = True
        
    def __repr__(self):
        shifting_tag = " [Trocando]" if self.shifting else ""
        return(
            f"[CarState] | "
            f"Marcha: {self.gear} {shifting_tag} | "
            f"RPM: {self.rpm:.0f} | "
            f"Vel: {self.speed:.1f} km/h | "
            f"Combustivel: {self.fuel:.1f}% | "
            f"Temp Oleo: {self.oil_temp:.1f}C | "
        )