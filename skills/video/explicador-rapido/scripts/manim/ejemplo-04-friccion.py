from _auto import *


class Escena(m.Scene):
    def construct(self):
        r = Reloj(self, 4)
        Y_PISO = -0.6
        piso = m.Line([-3.6, Y_PISO, 0], [3.6, Y_PISO, 0], color=LINEA, stroke_width=6)
        a = auto(ancho=4.6)
        a.shift(m.UP * Y_PISO)  # las llantas apoyadas en el piso
        llanta = a[2]
        cont = contacto(a)  # punto de contacto de la llanta delantera con el piso

        # Diagrama de cuerpo libre: el auto y el piso
        r.hasta("piso")
        r.play(m.Create(piso), m.FadeIn(a, shift=m.DOWN * 0.3), run_time=0.7)
        r.hasta("llanta")
        r.play(m.Indicate(llanta, color=CIAN, scale_factor=1.3), run_time=0.5)
        # La fuerza que empuja sale del contacto de la llanta con el piso
        r.hasta("empuja")
        f = flecha(cont, cont + m.RIGHT * 1.9, CIAN, 8)
        fl = mono("F", 40, CIAN, "BOLD").next_to(f, m.DOWN, buff=0.2)
        r.play(m.GrowArrow(f), m.FadeIn(fl), run_time=0.6)
        # La regla de la fricción: F ≤ μ·N
        r.hasta("fricción")
        eq = m.MathTex(r"F \le \mu \, N", color=FG, font_size=110).move_to([0, 3.5, 0])
        r.play(m.Write(eq), run_time=0.9)
        # Normal hacia arriba desde el contacto de la llanta; peso hacia abajo desde el centro de masa
        r.hasta("normal")
        cm = centro_masa(a)
        n = flecha(cont, [cont[0], 2.3, 0], MENTA, 8)
        w = flecha(cm, [cm[0], -2.0, 0], ROSA, 8)
        nl = mono("N", 40, MENTA, "BOLD").next_to(n.get_end(), m.LEFT, buff=0.2)
        wl = mono("m·g", 36, ROSA, "BOLD").next_to(w.get_end(), m.RIGHT, buff=0.2)
        r.play(m.GrowArrow(n), m.FadeIn(nl), m.GrowArrow(w), m.FadeIn(wl), run_time=0.6)
        # El dato de Tesla
        r.hasta("tesla")
        eq2 = m.MathTex(r"a_{\max} = \mu \, g = 1\mathord{,}26\, g", color=FG, font_size=76).move_to([0, 3.5, 0])
        r.play(m.TransformMatchingTex(eq, eq2), run_time=0.9)
        r.hasta("veintiséis")
        caja = m.Rectangle(width=eq2.width + 0.4, height=eq2.height + 0.4, color=MENTA, stroke_width=4).move_to(eq2)
        r.play(m.Create(caja), m.Indicate(eq2[0][-5:], color=MENTA, scale_factor=1.08), run_time=0.45)
        r.fin()
