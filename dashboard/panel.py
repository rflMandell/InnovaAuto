# hoje q minhas habilidades de criador de interface serao provadas

import tkinter as tk
import math

#Cores do tema escuro -----------------------
BG          = "#0a0a0a"   # fundo principal
BG_CARD     = "#111111"   # fundo dos cards
ACCENT      = "#e8001e"   # vermelho esportivo
ACCENT2     = "#ff6600"   # laranja (zona de perigo)
GREEN       = "#00e676"   # verde (normal)
YELLOW      = "#ffea00"   # amarelo (atenção)
RED         = "#ff1744"   # vermelho (crítico)
WHITE       = "#ffffff"
GRAY        = "#444444"
LIGHT_GRAY  = "#888888"
BLUE        = "#2979ff"

# Dimensoes ---------------------------------
WIN_W, WIN_H     = 1100, 600
TACH_CX, TACH_CY = 420, 270   # centro do conta-giros
TACH_R           = 220          # raio externo
SPEED_CX         = 850          # centro do velocímetro (X)
SPEED_CY         = 230
SPEED_R          = 150

# Limites -----------------------------------
RPM_MAX = 7000
RPM_RED = 6000
SPEED_MAX = 220


class Dashboaard:
    """
    Painel digital do InnovaAuto 
    """

    def __init__(self, root, state, update_interval_ms=33):
        self.root  = root
        self.state = state
        self.interval = update_interval_ms

        self.root.title("InnovaAuto — Painel Digital")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self.root.geometry(f"{WIN_W}x{WIN_H}")

        self.canvas = tk.Canvas(
            root, width=WIN_W, height=WIN_H,
            bg=BG, highlightthickness=0
        )
        self.canvas.pack()

        self._draw_static()
        self._schedule_update()

    # --------------------------------------------
    # Elementos estáticos (desenhados uma só vez)
    # --------------------------------------------

    def _draw_static(self):
        """Desenha elementos que não mudam: título, trilhos dos arcos."""
        c = self.canvas

        # Título
        c.create_text(
            WIN_W // 2, 22,
            text="INNOVAAUTO", font=("Helvetica", 13, "bold"),
            fill=ACCENT, anchor="center"
        )

        # Trilho do conta-giros
        _draw_arc_track(c, TACH_CX, TACH_CY, TACH_R, GRAY, width=18)

        # Marcações de RPM (0 a 7000, a cada 1000)
        for rpm in range(0, RPM_MAX + 1, 1000):
            angle = _rpm_to_angle(rpm, RPM_MAX)
            # Linha de marcação
            x1, y1 = _polar(TACH_CX, TACH_CY, TACH_R - 28, angle)
            x2, y2 = _polar(TACH_CX, TACH_CY, TACH_R - 8,  angle)
            color = RED if rpm >= RPM_RED else LIGHT_GRAY
            c.create_line(x1, y1, x2, y2, fill=color, width=2)
            # Número
            tx, ty = _polar(TACH_CX, TACH_CY, TACH_R - 48, angle)
            label = str(rpm // 1000)
            c.create_text(
                tx, ty, text=label,
                font=("Helvetica", 11, "bold"),
                fill=RED if rpm >= RPM_RED else LIGHT_GRAY,
                anchor="center"
            )

        # Label RPM
        c.create_text(
            TACH_CX, TACH_CY + TACH_R - 60,
            text="RPM  x1000", font=("Helvetica", 10),
            fill=LIGHT_GRAY, anchor="center"
        )

        # Trilho do velocímetro
        _draw_arc_track(c, SPEED_CX, SPEED_CY, SPEED_R, GRAY, width=12)

        # Marcações de velocidade (0 a 220, a cada 20)
        for spd in range(0, SPEED_MAX + 1, 20):
            angle = _speed_to_angle(spd, SPEED_MAX)
            x1, y1 = _polar(SPEED_CX, SPEED_CY, SPEED_R - 20, angle)
            x2, y2 = _polar(SPEED_CX, SPEED_CY, SPEED_R - 6,  angle)
            c.create_line(x1, y1, x2, y2, fill=LIGHT_GRAY, width=1)
            if spd % 40 == 0:
                tx, ty = _polar(SPEED_CX, SPEED_CY, SPEED_R - 34, angle)
                c.create_text(
                    tx, ty, text=str(spd),
                    font=("Helvetica", 8),
                    fill=LIGHT_GRAY, anchor="center"
                )

        # Label km/h
        c.create_text(
            SPEED_CX, SPEED_CY + SPEED_R - 38,
            text="km/h", font=("Helvetica", 9),
            fill=LIGHT_GRAY, anchor="center"
        )

        # ── Barras de sensores — labels fixos ──
        c.create_text( 60, 430, text="COMB.",  font=("Helvetica", 9), fill=LIGHT_GRAY, anchor="w")
        c.create_text( 60, 470, text="TEMP.",  font=("Helvetica", 9), fill=LIGHT_GRAY, anchor="w")
        c.create_text( 60, 510, text="AUTO.",   font=("Helvetica", 9), fill=LIGHT_GRAY, anchor="w")

        # Separador horizontal
        c.create_line(40, 415, WIN_W - 40, 415, fill=GRAY, width=1)

    # ─────────────────────────────────────────────────────────────────
    # Loop de atualização
    # ─────────────────────────────────────────────────────────────────

    def _schedule_update(self):
        self._update()
        self.root.after(self.interval, self._schedule_update)

    def _update(self):
        c = self.canvas
        s = self.state

        c.delete("dynamic")   # Apaga só os elementos dinâmicos

        # ── Conta-giros ──────────────────────────────────────────────
        rpm_ratio = min(s.rpm / RPM_MAX, 1.0)
        rpm_color = _rpm_color(s.rpm)
        _draw_arc_fill(
            c, TACH_CX, TACH_CY, TACH_R,
            rpm_ratio, rpm_color, width=18, tag="dynamic"
        )

        # Agulha do conta-giros
        needle_angle = _rpm_to_angle(min(s.rpm, RPM_MAX), RPM_MAX)
        nx, ny = _polar(TACH_CX, TACH_CY, TACH_R - 35, needle_angle)
        c.create_line(
            TACH_CX, TACH_CY, nx, ny,
            fill=WHITE, width=3, tags="dynamic"
        )
        # Centro da agulha
        c.create_oval(
            TACH_CX-8, TACH_CY-8, TACH_CX+8, TACH_CY+8,
            fill=ACCENT, outline="", tags="dynamic"
        )

        # Valor numérico de RPM
        c.create_text(
            TACH_CX, TACH_CY - 30,
            text=f"{s.rpm:,.0f}",
            font=("Helvetica", 36, "bold"),
            fill=rpm_color, anchor="center", tags="dynamic"
        )

        # ── Marcha ───────────────────────────────────────────────────
        gear_color = YELLOW if s.shifting else WHITE
        c.create_text(
            TACH_CX, TACH_CY + 55,
            text=s.gear,
            font=("Helvetica", 72, "bold"),
            fill=gear_color, anchor="center", tags="dynamic"
        )
        c.create_text(
            TACH_CX, TACH_CY + 110,
            text="MARCHA",
            font=("Helvetica", 10),
            fill=LIGHT_GRAY, anchor="center", tags="dynamic"
        )

        # ── Velocímetro ──────────────────────────────────────────────
        spd_ratio = min(s.speed / SPEED_MAX, 1.0)
        spd_color = RED if s.speed > 180 else (YELLOW if s.speed > 120 else GREEN)
        _draw_arc_fill(
            c, SPEED_CX, SPEED_CY, SPEED_R,
            spd_ratio, spd_color, width=12, tag="dynamic"
        )

        # Agulha do velocímetro
        spd_angle = _speed_to_angle(min(s.speed, SPEED_MAX), SPEED_MAX)
        snx, sny = _polar(SPEED_CX, SPEED_CY, SPEED_R - 22, spd_angle)
        c.create_line(
            SPEED_CX, SPEED_CY, snx, sny,
            fill=WHITE, width=2, tags="dynamic"
        )
        c.create_oval(
            SPEED_CX-5, SPEED_CY-5, SPEED_CX+5, SPEED_CY+5,
            fill=ACCENT, outline="", tags="dynamic"
        )

        # Valor numérico de velocidade
        c.create_text(
            SPEED_CX, SPEED_CY + 10,
            text=f"{s.speed:.0f}",
            font=("Helvetica", 28, "bold"),
            fill=spd_color, anchor="center", tags="dynamic"
        )

        # ── Acelerador e Freio ───────────────────────────────────────
        _draw_pedal_bar(
            c, 700, 360, s.throttle, GREEN, "ACEL", tag="dynamic"
        )
        _draw_pedal_bar(
            c, 790, 360, s.brake, RED, "FREIO", tag="dynamic"
        )

        # ── Barra de Combustível ─────────────────────────────────────
        fuel_color = RED if s.fuel <= 15 else (YELLOW if s.fuel <= 30 else GREEN)
        _draw_sensor_bar(c, 160, 430, s.fuel, 100, fuel_color, tag="dynamic")
        c.create_text(
            860, 430,
            text=f"{s.fuel:.1f}%",
            font=("Helvetica", 10, "bold"),
            fill=fuel_color, anchor="e", tags="dynamic"
        )

        # ── Barra de Temperatura ─────────────────────────────────────
        temp_norm = (s.oil_temp - 20) / (150 - 20)
        temp_color = RED if s.oil_temp >= 110 else (YELLOW if s.oil_temp >= 90 else GREEN)
        _draw_sensor_bar(c, 160, 470, temp_norm * 100, 100, temp_color, tag="dynamic")
        c.create_text(
            860, 470,
            text=f"{s.oil_temp:.1f}°C",
            font=("Helvetica", 10, "bold"),
            fill=temp_color, anchor="e", tags="dynamic"
        )

        # ── Autonomia ────────────────────────────────────────────────
        c.create_text(
            860, 510,
            text=f"{s.autonomy:.0f} km",
            font=("Helvetica", 10, "bold"),
            fill=LIGHT_GRAY, anchor="e", tags="dynamic"
        )

        # ── Alertas ──────────────────────────────────────────────────
        _draw_alerts(c, s, tag="dynamic")

    # ─────────────────────────────────────────────────────────────────
    # Método público para fechar
    # ─────────────────────────────────────────────────────────────────

    def start(self):
        self.root.mainloop()


# ─────────────────────────────────────────────────────────────────────
# Funções auxiliares de desenho
# ─────────────────────────────────────────────────────────────────────

def _polar(cx, cy, r, angle_deg):
    """Converte coordenadas polares para cartesianas."""
    rad = math.radians(angle_deg)
    return cx + r * math.cos(rad), cy + r * math.sin(rad)


def _rpm_to_angle(rpm, rpm_max):
    """
    Mapeia RPM para ângulo do arco.
    O arco vai de 210° (0 RPM) até -30° (RPM max) — sentido horário.
    """
    ratio = rpm / rpm_max
    return 210 - ratio * 240


def _speed_to_angle(speed, speed_max):
    """Mesmo mapeamento para velocidade."""
    ratio = speed / speed_max
    return 210 - ratio * 240


def _draw_arc_track(canvas, cx, cy, r, color, width=12):
    """Desenha o trilho cinza de fundo do arco."""
    x0, y0 = cx - r, cy - r
    x1, y1 = cx + r, cy + r
    canvas.create_arc(
        x0, y0, x1, y1,
        start=-30, extent=240,
        style="arc", outline=color, width=width
    )


def _draw_arc_fill(canvas, cx, cy, r, ratio, color, width=12, tag="dynamic"):
    """Desenha o arco colorido proporcional ao valor."""
    if ratio <= 0:
        return
    extent = ratio * 240
    x0, y0 = cx - r, cy - r
    x1, y1 = cx + r, cy + r
    canvas.create_arc(
        x0, y0, x1, y1,
        start=210, extent=-extent,
        style="arc", outline=color,
        width=width, tags=tag
    )


def _draw_sensor_bar(canvas, x, y, value, max_val, color, width=680, height=10, tag="dynamic"):
    """Desenha uma barra horizontal de sensor."""
    # Fundo
    canvas.create_rectangle(
        x, y - height // 2,
        x + width, y + height // 2,
        fill=GRAY, outline="", tags=tag
    )
    # Preenchimento
    ratio = max(0.0, min(value / max_val, 1.0))
    fill_w = int(width * ratio)
    if fill_w > 0:
        canvas.create_rectangle(
            x, y - height // 2,
            x + fill_w, y + height // 2,
            fill=color, outline="", tags=tag
        )


def _draw_pedal_bar(canvas, x, y, value, color, label, width=20, max_height=80, tag="dynamic"):
    """Desenha uma barra vertical para acelerador/freio."""
    # Fundo
    canvas.create_rectangle(
        x, y - max_height, x + width, y,
        fill=GRAY, outline="", tags=tag
    )
    # Preenchimento
    fill_h = int(max_height * max(0.0, min(value, 1.0)))
    if fill_h > 0:
        canvas.create_rectangle(
            x, y - fill_h, x + width, y,
            fill=color, outline="", tags=tag
        )
    # Label
    canvas.create_text(
        x + width // 2, y + 12,
        text=label, font=("Helvetica", 7),
        fill=LIGHT_GRAY, anchor="center", tags=tag
    )


def _draw_alerts(canvas, state, tag="dynamic"):
    """Desenha ícones de alerta ativos."""
    alerts = []

    if state.check_engine:
        alerts.append(("CHECK ENGINE", RED))
    if state.oil_alert:
        alerts.append(("TEMP ALTA", YELLOW))
    if state.fuel <= 15:
        alerts.append(("COMB. BAIXO", YELLOW))
    if 'engine_misfire' in state.faults:
        alerts.append(("IGNIÇÃO", ACCENT2))
    if 'brake_failure' in state.faults:
        alerts.append(("FREIO", RED))
    if 'transmission_fault' in state.faults:
        alerts.append(("CÂMBIO", ACCENT2))

    for i, (text, color) in enumerate(alerts):
        canvas.create_text(
            100 + i * 160, 385,
            text=text,
            font=("Helvetica", 10, "bold"),
            fill=color, anchor="center", tags=tag
        )


def _rpm_color(rpm):
    """Retorna a cor do conta-giros baseada no RPM."""
    if rpm >= RPM_RED:
        return RED
    elif rpm >= RPM_MAX * 0.65:
        return YELLOW
    else:
        return GREEN