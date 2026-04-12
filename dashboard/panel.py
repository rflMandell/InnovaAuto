import tkinter as tk
import math

# ── Cores ────────────────────────────────────────────────────────────
BG         = "#0a0a0a"
BG_CARD    = "#111111"
ACCENT     = "#e8001e"
ACCENT2    = "#ff6600"
GREEN      = "#00e676"
YELLOW     = "#ffea00"
RED        = "#ff1744"
WHITE      = "#ffffff"
GRAY       = "#444444"
LIGHT_GRAY = "#888888"
BLUE       = "#2979ff"

# ── Dimensões da janela ──────────────────────────────────────────────
WIN_W, WIN_H = 1100, 620

# ── Conta-giros ──────────────────────────────────────────────────────
TACH_CX, TACH_CY = 380, 280
TACH_R           = 220

# ── Velocímetro ──────────────────────────────────────────────────────
SPEED_CX, SPEED_CY = 820, 240
SPEED_R            = 160

# ── Limites ──────────────────────────────────────────────────────────
RPM_MAX   = 7000
RPM_RED   = 6000
SPEED_MAX = 220

# ── Ângulos do arco ──────────────────────────────────────────────────
# O arco começa em 220° (esquerda/baixo) e termina em -40° (direita/baixo)
# Sentido anti-horário de 220° → -40°  (total = 260°)
ARC_START = 220   # ângulo da posição ZERO (mínimo)
ARC_SPAN  = 260   # quantos graus o arco ocupa no total


class Dashboard:
    def __init__(self, root, state, update_interval_ms=33):
        self.root     = root
        self.state    = state
        self.interval = update_interval_ms

        self.root.title("InnovaAuto — Painel Digital")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)
        self.root.geometry(f"{WIN_W}x{WIN_H}")

        self.canvas = tk.Canvas(
            root, width=WIN_W, height=WIN_H,
            bg=BG, highlightthickness=0
        )
        self.canvas.pack()

        self._draw_static()
        self._schedule_update()

    # ─────────────────────────────────────────────────────────────────
    # Estático
    # ─────────────────────────────────────────────────────────────────

    def _draw_static(self):
        c = self.canvas

        # Título
        c.create_text(
            WIN_W // 2, 22,
            text="INNOVAAUTO",
            font=("Helvetica", 13, "bold"),
            fill=ACCENT, anchor="center"
        )

        # ── Trilho conta-giros ──
        _draw_arc_track(c, TACH_CX, TACH_CY, TACH_R, GRAY, width=18)

        # Marcações de RPM
        for rpm in range(0, RPM_MAX + 1, 1000):
            angle = _value_to_angle(rpm, 0, RPM_MAX)
            x1, y1 = _polar(TACH_CX, TACH_CY, TACH_R - 30, angle)
            x2, y2 = _polar(TACH_CX, TACH_CY, TACH_R - 8,  angle)
            color  = RED if rpm >= RPM_RED else LIGHT_GRAY
            c.create_line(x1, y1, x2, y2, fill=color, width=2)
            tx, ty = _polar(TACH_CX, TACH_CY, TACH_R - 52, angle)
            c.create_text(
                tx, ty,
                text=str(rpm // 1000),
                font=("Helvetica", 11, "bold"),
                fill=RED if rpm >= RPM_RED else LIGHT_GRAY,
                anchor="center"
            )

        c.create_text(
            TACH_CX, TACH_CY + TACH_R - 55,
            text="RPM  ×1000",
            font=("Helvetica", 10),
            fill=LIGHT_GRAY, anchor="center"
        )

        # ── Trilho velocímetro ──
        _draw_arc_track(c, SPEED_CX, SPEED_CY, SPEED_R, GRAY, width=12)

        for spd in range(0, SPEED_MAX + 1, 20):
            angle  = _value_to_angle(spd, 0, SPEED_MAX)
            x1, y1 = _polar(SPEED_CX, SPEED_CY, SPEED_R - 20, angle)
            x2, y2 = _polar(SPEED_CX, SPEED_CY, SPEED_R - 6,  angle)
            c.create_line(x1, y1, x2, y2, fill=LIGHT_GRAY, width=1)
            if spd % 40 == 0:
                tx, ty = _polar(SPEED_CX, SPEED_CY, SPEED_R - 36, angle)
                c.create_text(
                    tx, ty, text=str(spd),
                    font=("Helvetica", 8),
                    fill=LIGHT_GRAY, anchor="center"
                )

        c.create_text(
            SPEED_CX, SPEED_CY + SPEED_R - 35,
            text="km/h",
            font=("Helvetica", 9),
            fill=LIGHT_GRAY, anchor="center"
        )

        # ── Separador ──
        c.create_line(40, 430, WIN_W - 40, 430, fill=GRAY, width=1)

        # ── Labels fixos das barras ──
        c.create_text(60, 455, text="COMB.", font=("Helvetica", 9), fill=LIGHT_GRAY, anchor="w")
        c.create_text(60, 495, text="TEMP.", font=("Helvetica", 9), fill=LIGHT_GRAY, anchor="w")
        c.create_text(60, 535, text="AUTO.", font=("Helvetica", 9), fill=LIGHT_GRAY, anchor="w")

        # ── Barras de pedal — lado esquerdo, abaixo do conta-giros ──
        c.create_text(
            95, 390,
            text="ACEL",
            font=("Helvetica", 8), fill=LIGHT_GRAY, anchor="center"
        )
        c.create_text(
            140, 390,
            text="FREIO",
            font=("Helvetica", 8), fill=LIGHT_GRAY, anchor="center"
        )

    # ─────────────────────────────────────────────────────────────────
    # Dinâmico
    # ─────────────────────────────────────────────────────────────────

    def _schedule_update(self):
        self._update()
        self.root.after(self.interval, self._schedule_update)

    def _update(self):
        c = self.canvas
        s = self.state
        c.delete("dynamic")

        # ── Conta-giros ──────────────────────────────────────────────
        rpm_clamped = max(0, min(s.rpm, RPM_MAX))
        rpm_ratio   = rpm_clamped / RPM_MAX
        rpm_color   = _rpm_color(s.rpm)

        _draw_arc_fill(c, TACH_CX, TACH_CY, TACH_R, rpm_ratio, rpm_color, width=18)

        # Agulha
        needle_angle = _value_to_angle(rpm_clamped, 0, RPM_MAX)
        nx, ny = _polar(TACH_CX, TACH_CY, TACH_R - 38, needle_angle)
        c.create_line(TACH_CX, TACH_CY, nx, ny, fill=WHITE, width=3, tags="dynamic")
        c.create_oval(
            TACH_CX-8, TACH_CY-8, TACH_CX+8, TACH_CY+8,
            fill=ACCENT, outline="", tags="dynamic"
        )

        # Valor numérico
        c.create_text(
            TACH_CX, TACH_CY - 35,
            text=f"{s.rpm:,.0f}",
            font=("Helvetica", 38, "bold"),
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
            TACH_CX, TACH_CY + 112,
            text="MARCHA",
            font=("Helvetica", 10),
            fill=LIGHT_GRAY, anchor="center", tags="dynamic"
        )

        # ── Velocímetro ──────────────────────────────────────────────
        spd_clamped = max(0, min(s.speed, SPEED_MAX))
        spd_ratio   = spd_clamped / SPEED_MAX
        spd_color   = RED if s.speed > 180 else (YELLOW if s.speed > 120 else GREEN)

        _draw_arc_fill(c, SPEED_CX, SPEED_CY, SPEED_R, spd_ratio, spd_color, width=12)

        # Agulha
        spd_angle   = _value_to_angle(spd_clamped, 0, SPEED_MAX)
        snx, sny    = _polar(SPEED_CX, SPEED_CY, SPEED_R - 24, spd_angle)
        c.create_line(SPEED_CX, SPEED_CY, snx, sny, fill=WHITE, width=2, tags="dynamic")
        c.create_oval(
            SPEED_CX-5, SPEED_CY-5, SPEED_CX+5, SPEED_CY+5,
            fill=ACCENT, outline="", tags="dynamic"
        )

        # Valor numérico
        c.create_text(
            SPEED_CX, SPEED_CY + 15,
            text=f"{s.speed:.0f}",
            font=("Helvetica", 30, "bold"),
            fill=spd_color, anchor="center", tags="dynamic"
        )

        # ── Barras de pedal ──────────────────────────────────────────
        # Lado esquerdo do painel, abaixo do conta-giros
        _draw_pedal_bar(c, 80,  380, s.throttle, GREEN, tag="dynamic")
        _draw_pedal_bar(c, 125, 380, s.brake,    RED,   tag="dynamic")

        # ── Barra de Combustível ─────────────────────────────────────
        fuel_color = RED if s.fuel <= 15 else (YELLOW if s.fuel <= 30 else GREEN)
        _draw_sensor_bar(c, 160, 455, s.fuel, 100, fuel_color)
        c.create_text(
            880, 455,
            text=f"{s.fuel:.1f}%",
            font=("Helvetica", 10, "bold"),
            fill=fuel_color, anchor="e", tags="dynamic"
        )

        # ── Barra de Temperatura ─────────────────────────────────────
        temp_norm  = (s.oil_temp - 20) / (150 - 20)
        temp_color = RED if s.oil_temp >= 110 else (YELLOW if s.oil_temp >= 90 else GREEN)
        _draw_sensor_bar(c, 160, 495, temp_norm * 100, 100, temp_color)
        c.create_text(
            880, 495,
            text=f"{s.oil_temp:.1f}°C",
            font=("Helvetica", 10, "bold"),
            fill=temp_color, anchor="e", tags="dynamic"
        )

        # ── Autonomia ────────────────────────────────────────────────
        c.create_text(
            880, 535,
            text=f"{s.autonomy:.0f} km",
            font=("Helvetica", 10, "bold"),
            fill=LIGHT_GRAY, anchor="e", tags="dynamic"
        )

        # ── Alertas ──────────────────────────────────────────────────
        _draw_alerts(c, s)

    def start(self):
        self.root.mainloop()


# ─────────────────────────────────────────────────────────────────────
# Funções auxiliares
# ─────────────────────────────────────────────────────────────────────

def _polar(cx, cy, r, angle_deg):
    """Converte polar → cartesiano. 0° = direita, cresce anti-horário."""
    rad = math.radians(angle_deg)
    return cx + r * math.cos(rad), cy - r * math.sin(rad)


def _value_to_angle(value, min_val, max_val):
    """
    Mapeia um valor para um ângulo no arco.

    Arco:  ARC_START (220°) → ARC_START - ARC_SPAN (-40°)
           valor mínimo = lado esquerdo/baixo (220°)
           valor máximo = lado direito/baixo  (-40° = 320°)

    Com _polar usando  cy - r*sin(θ):
      220° → esquerda/baixo  ✓
      -40° → direita/baixo   ✓
    """
    ratio = (value - min_val) / (max_val - min_val)
    ratio = max(0.0, min(ratio, 1.0))
    return ARC_START - ratio * ARC_SPAN


def _draw_arc_track(canvas, cx, cy, r, color, width=12):
    """Trilho cinza de fundo."""
    x0, y0 = cx - r, cy - r
    x1, y1 = cx + r, cy + r
    # start=-40 (posição máxima), extent=260 (varre até 220°)
    canvas.create_arc(
        x0, y0, x1, y1,
        start=-40, extent=260,
        style="arc", outline=color, width=width
    )


def _draw_arc_fill(canvas, cx, cy, r, ratio, color, width=12, tag="dynamic"):
    """Arco colorido proporcional ao valor (começa em 220°, cresce horário)."""
    if ratio <= 0:
        return
    extent = ratio * ARC_SPAN
    x0, y0 = cx - r, cy - r
    x1, y1 = cx + r, cy + r
    # start=220° (mínimo), extent negativo = sentido horário no Tkinter
    canvas.create_arc(
        x0, y0, x1, y1,
        start=220, extent=-extent,
        style="arc", outline=color,
        width=width, tags=tag
    )


def _draw_sensor_bar(canvas, x, y, value, max_val, color,
                     bar_w=700, bar_h=10, tag="dynamic"):
    """Barra horizontal de sensor."""
    canvas.create_rectangle(
        x, y - bar_h // 2, x + bar_w, y + bar_h // 2,
        fill=GRAY, outline="", tags=tag
    )
    ratio  = max(0.0, min(value / max_val, 1.0))
    fill_w = int(bar_w * ratio)
    if fill_w > 0:
        canvas.create_rectangle(
            x, y - bar_h // 2, x + fill_w, y + bar_h // 2,
            fill=color, outline="", tags=tag
        )


def _draw_pedal_bar(canvas, x, y, value, color,
                    bar_w=22, max_h=75, tag="dynamic"):
    """Barra vertical de pedal (acelerador / freio)."""
    # Fundo
    canvas.create_rectangle(
        x, y - max_h, x + bar_w, y,
        fill=GRAY, outline="", tags=tag
    )
    # Preenchimento
    fill_h = int(max_h * max(0.0, min(value, 1.0)))
    if fill_h > 0:
        canvas.create_rectangle(
            x, y - fill_h, x + bar_w, y,
            fill=color, outline="", tags=tag
        )


def _draw_alerts(canvas, state, tag="dynamic"):
    """Ícones de alerta na faixa central."""
    alerts = []
    if state.check_engine:
        alerts.append(("CHECK ENGINE", RED))
    if state.oil_alert:
        alerts.append(("TEMP ALTA",    YELLOW))
    if state.fuel <= 15:
        alerts.append(("COMB. BAIXO",  YELLOW))
    if 'engine_misfire'     in state.faults:
        alerts.append(("IGNIÇÃO",       ACCENT2))
    if 'brake_failure'      in state.faults:
        alerts.append(("FREIO",         RED))
    if 'transmission_fault' in state.faults:
        alerts.append(("CÂMBIO",        ACCENT2))

    for i, (text, color) in enumerate(alerts):
        canvas.create_text(
            100 + i * 170, 408,
            text=text,
            font=("Helvetica", 10, "bold"),
            fill=color, anchor="center", tags=tag
        )


def _rpm_color(rpm):
    if rpm >= RPM_RED:
        return RED
    elif rpm >= RPM_MAX * 0.65:
        return YELLOW
    return GREEN