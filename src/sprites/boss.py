##########################################################
#  Boss KRONOS — Entidade Biomecânica Suprema
#
#  VISUAL:
#   Anel externo giratório com 8 espinhos
#   Corpo: anel de costelas biomecânicas (12 segmentos)
#   4 braços-tentáculo com garras
#   Núcleo pulsante animado por frame
#   Olho central que rastreia o jogador suavemente
#
#  ESTADOS:
#   FASE1 (HP > 50%): patrulha + rajadas de 8 balas
#   FASE2 (HP < 50%): Bullet Hell — espirais + dash
##########################################################

import pygame
import random
import math
from src.config import *
from src.sprites.bullets import BalaBoss


class Boss(pygame.sprite.Sprite):
    FASE1 = "fase1"
    FASE2 = "fase2"

    COR_FASE1 = (200, 0,  50)
    COR_FASE2 = (255, 80, 200)

    # Nomes e paletas por nível de boss
    _NOMES   = {1: "KRONOS",   2: "EREBUS",     3: "NEMESIS"}
    _CORES_1 = {1: (200, 0, 50), 2: (0, 60, 220), 3: (180, 120, 0)}
    _CORES_2 = {1: (255, 80, 200), 2: (0, 200, 255), 3: (255, 200, 0)}

    def __init__(self, pos_jogador, nivel_boss: int = 1):
        super().__init__()

        # Escalonamento por nível: cada boss é visivelmente mais difícil
        # Nível 1 (fase 5): padrão  |  Nível 2 (fase 10): +60% HP, mais rápido
        # Nível 3 (fase 15): +150% HP, bullet hell intenso
        self.nivel_boss = max(1, min(3, nivel_boss))
        mult_hp  = 1.0 + (self.nivel_boss - 1) * 0.75   # 1.0 / 1.75 / 2.5
        mult_vel = 1.0 + (self.nivel_boss - 1) * 0.35   # 1.0 / 1.35 / 1.7

        self.hp       = int(BOSS_HP * mult_hp)
        self.hp_max   = self.hp
        self.estado   = self.FASE1
        self.xp_valor = 200 * self.nivel_boss
        self.nome     = self._NOMES.get(self.nivel_boss, "KRONOS")

        self.COR_FASE1 = self._CORES_1.get(self.nivel_boss, (200, 0, 50))
        self.COR_FASE2 = self._CORES_2.get(self.nivel_boss, (255, 80, 200))

        self._tick        = 0
        self._angulo_anel = 0.0
        self._angulo_olho = 0.0
        self._pulso       = 0.0
        self._fase_cor    = self.COR_FASE1

        self._construir_imagem()

        angulo   = random.uniform(0, math.tau)
        self.pos = pos_jogador + pygame.math.Vector2(
            math.cos(angulo), math.sin(angulo)) * 800
        self.rect = self.image.get_rect(center=self.pos)

        self.velocidade          = 1.8 * mult_vel
        self.ultimo_tiro_rajada  = 0
        # Boss nível 3 dispara rajadas mais rápidas
        self.cadencia_rajada     = max(700, 1500 - (self.nivel_boss - 1) * 300)
        self.angulo_espiral      = 0.0
        self.vel_espiral         = 4 + (self.nivel_boss - 1) * 2   # espiral mais rápida
        self.ultimo_tiro_espiral = 0
        self.cadencia_espiral    = max(60, 120 - (self.nivel_boss - 1) * 25)
        self.vel_dash            = 0.0
        self.dir_dash            = pygame.math.Vector2(0, 0)
        self.dash_duracao        = 0

        self._flash_timer = 0
        self._fonte_barra = pygame.font.SysFont("Arial", 16, bold=True)
        self._fonte_nome  = pygame.font.SysFont("Arial", 20, bold=True)

    def _construir_imagem(self):
        W  = BOSS_TAMANHO[0] + 30
        self._W = W
        cx = cy = W // 2
        cor       = self._fase_cor
        cor_dark  = tuple(max(0, c - 80) for c in cor)
        cor_brilho = tuple(min(255, c + 80) for c in cor)
        surf = pygame.Surface((W, W), pygame.SRCALPHA)

        # Anel externo giratório com espinhos
        r_ext = W // 2 - 3
        for i in range(8):
            a = math.radians(i * 45 + self._angulo_anel)
            px0 = cx + math.cos(a) * (r_ext - 10)
            py0 = cy + math.sin(a) * (r_ext - 10)
            px1 = cx + math.cos(a) * r_ext
            py1 = cy + math.sin(a) * r_ext
            pygame.draw.line(surf, cor_brilho,
                             (int(px0), int(py0)), (int(px1), int(py1)), 2)
            perp = math.radians(i * 45 + self._angulo_anel + 90)
            tp1 = (cx + math.cos(a) * (r_ext + 5),
                   cy + math.sin(a) * (r_ext + 5))
            tp2 = (int(px1 + math.cos(perp) * 3),
                   int(py1 + math.sin(perp) * 3))
            tp3 = (int(px1 - math.cos(perp) * 3),
                   int(py1 - math.sin(perp) * 3))
            pygame.draw.polygon(surf, cor, [tp1, tp2, tp3])
        pygame.draw.circle(surf, cor_dark, (cx, cy), r_ext - 10, width=2)

        # Corpo — 12 costelas biomecânicas
        r_body = W // 2 - 18
        for i in range(12):
            a0  = math.radians(i * 30 - 10)
            a1  = math.radians(i * 30 + 10)
            pts = [(cx, cy)]
            for t in range(8):
                a = a0 + (a1 - a0) * t / 7
                pts.append((cx + math.cos(a) * r_body,
                             cy + math.sin(a) * r_body))
            cor_seg = cor if i % 2 == 0 else cor_dark
            pygame.draw.polygon(surf, cor_seg, pts)
            a_mid = math.radians(i * 30)
            pygame.draw.line(surf, (0,0,0),
                             (int(cx + math.cos(a_mid)*12),
                              int(cy + math.sin(a_mid)*12)),
                             (int(cx + math.cos(a_mid)*r_body),
                              int(cy + math.sin(a_mid)*r_body)), 1)
        pygame.draw.circle(surf, cor_dark,  (cx, cy), r_body, width=3)
        pygame.draw.circle(surf, cor_brilho,(cx, cy), r_body, width=1)

        # 4 braços-tentáculo com garras
        for i in range(4):
            a_base = math.radians(i * 90 + 45)
            x0 = cx + math.cos(a_base) * 14
            y0 = cy + math.sin(a_base) * 14
            curva = math.radians(i * 90 + 45 + 25)
            xk = cx + math.cos(curva) * 26
            yk = cy + math.sin(curva) * 26
            x1 = cx + math.cos(a_base) * (r_ext - 14)
            y1 = cy + math.sin(a_base) * (r_ext - 14)
            pygame.draw.line(surf, cor_dark,
                             (int(x0),int(y0)),(int(xk),int(yk)), 4)
            pygame.draw.line(surf, cor,
                             (int(x0),int(y0)),(int(xk),int(yk)), 2)
            pygame.draw.line(surf, cor_dark,
                             (int(xk),int(yk)),(int(x1),int(y1)), 4)
            pygame.draw.line(surf, cor,
                             (int(xk),int(yk)),(int(x1),int(y1)), 2)
            for side in (-1, 1):
                ag = math.radians(i * 90 + 45 + side * 30)
                gx = x1 + math.cos(ag) * 7
                gy = y1 + math.sin(ag) * 7
                pygame.draw.line(surf, cor_brilho,
                                 (int(x1),int(y1)),(int(gx),int(gy)), 2)

        # Núcleo pulsante
        r_nucleo = 14
        pulso_r  = int(r_nucleo + 3 * math.sin(self._pulso))
        pygame.draw.circle(surf, (cor[0]//5, cor[1]//5, cor[2]//5),
                           (cx, cy), pulso_r + 5)
        pygame.draw.circle(surf, cor, (cx, cy), pulso_r, width=2)
        pygame.draw.circle(surf, cor_dark, (cx, cy), r_nucleo - 2)
        for a_deg in [0, 45, 90, 135]:
            a  = math.radians(a_deg + self._angulo_anel * 0.5)
            lx0 = cx + math.cos(a) * (r_nucleo - 2)
            ly0 = cy + math.sin(a) * (r_nucleo - 2)
            pygame.draw.line(surf, cor,
                             (int(lx0), int(ly0)),
                             (int(cx - math.cos(a)*(r_nucleo-2)),
                              int(cy - math.sin(a)*(r_nucleo-2))), 1)

        # Olho central rastreador
        pygame.draw.circle(surf, (255, 220, 255), (cx, cy), 7)
        px_olho = int(cx + math.cos(self._angulo_olho) * 2)
        py_olho = int(cy + math.sin(self._angulo_olho) * 2)
        cor_pupila = (80, 0, 120) if self.estado == self.FASE1 else (180, 0, 20)
        pygame.draw.circle(surf, cor_pupila, (px_olho, py_olho), 4)
        pygame.draw.circle(surf, (255,255,255), (px_olho-1, py_olho-2), 1)

        self.image    = surf
        self._img_base = surf.copy()

    def _criar_flash(self):
        surf = pygame.Surface((self._W, self._W), pygame.SRCALPHA)
        surf.fill((255, 255, 255, 230))
        return surf

    def sofrer_dano(self, valor):
        self.hp          -= valor
        self._flash_timer = 6
        if self.hp <= self.hp_max // 2 and self.estado == self.FASE1:
            self.estado    = self.FASE2
            self._fase_cor = self.COR_FASE2
            self._construir_imagem()

    def update(self, pos_jogador, lista_disparos):
        agora = pygame.time.get_ticks()
        self._tick  += 1
        vel_rot      = 1.2 if self.estado == self.FASE2 else 0.6
        self._angulo_anel = (self._angulo_anel + vel_rot) % 360
        self._pulso      += 0.12

        dir_olho = pos_jogador - self.pos
        if dir_olho.length() > 0:
            ang_alvo = math.atan2(dir_olho.y, dir_olho.x)
            diff     = (ang_alvo - self._angulo_olho + math.pi) % (2*math.pi) - math.pi
            self._angulo_olho += diff * 0.08

        self._construir_imagem()

        if self.estado == self.FASE1:
            self._update_fase1(pos_jogador, lista_disparos, agora)
        else:
            self._update_fase2(pos_jogador, lista_disparos, agora)

        if self._flash_timer > 0:
            self.image        = self._criar_flash()
            self._flash_timer -= 1
        else:
            self.image = self._img_base

        self.rect = self.image.get_rect(center=self.pos)

    def _update_fase1(self, pos_jogador, lista_disparos, agora):
        d = pos_jogador - self.pos
        if d.length() > 0:
            self.pos += d.normalize() * self.velocidade
        self.rect.center = self.pos
        if agora - self.ultimo_tiro_rajada > self.cadencia_rajada:
            self.ultimo_tiro_rajada = agora
            n_balas = 8 + (self.nivel_boss - 1) * 3   # 8 / 11 / 14 balas
            self._disparar_estrela(lista_disparos, n_balas=n_balas, cor=self.COR_FASE1)

    def _update_fase2(self, pos_jogador, lista_disparos, agora):
        if self.dash_duracao > 0:
            self.pos         += self.dir_dash * self.vel_dash
            self.vel_dash    *= 0.92
            self.dash_duracao -= 1
        else:
            d = pos_jogador - self.pos
            if d.length() > 0:
                self.pos += d.normalize() * self.velocidade * 1.6
            dash_chance = 0.003 + (self.nivel_boss - 1) * 0.002
            if random.random() < dash_chance:
                self._iniciar_dash(pos_jogador)
        self.rect.center = self.pos
        if agora - self.ultimo_tiro_espiral > self.cadencia_espiral:
            self.ultimo_tiro_espiral = agora
            self._disparar_espiral(lista_disparos)
        if agora - self.ultimo_tiro_rajada > self.cadencia_rajada * 0.7:
            self.ultimo_tiro_rajada = agora
            n_balas = 12 + (self.nivel_boss - 1) * 4   # 12 / 16 / 20 balas
            self._disparar_estrela(lista_disparos, n_balas=n_balas, cor=self.COR_FASE2)

    def _disparar_estrela(self, lista_disparos, n_balas=8, cor=VERMELHO):
        for i in range(n_balas):
            ang = math.radians(i * (360 / n_balas))
            lista_disparos.append({
                "pos": pygame.math.Vector2(self.pos),
                "dir": pygame.math.Vector2(math.cos(ang), math.sin(ang)),
                "tipo": "boss", "cor": cor})

    def _disparar_espiral(self, lista_disparos):
        for offset in [0, 120, 240]:
            ang = math.radians(self.angulo_espiral + offset)
            lista_disparos.append({
                "pos": pygame.math.Vector2(self.pos),
                "dir": pygame.math.Vector2(math.cos(ang), math.sin(ang)),
                "tipo": "boss", "cor": LARANJA})
        self.angulo_espiral = (self.angulo_espiral + self.vel_espiral) % 360

    def _iniciar_dash(self, pos_jogador):
        d = pos_jogador - self.pos
        if d.length() > 0:
            self.dir_dash     = d.normalize()
            self.vel_dash     = 14
            self.dash_duracao = 20

    def desenhar_barra_vida(self, superficie):
        barra_w   = 420
        barra_h   = 22
        x         = (superficie.get_width() - barra_w) // 2
        y         = superficie.get_height() - 55
        progresso = max(0, self.hp / self.hp_max)
        cor_vida  = self.COR_FASE2 if self.estado == self.FASE2 else self.COR_FASE1

        pygame.draw.rect(superficie, (20, 5, 25),
                         (x, y, barra_w, barra_h), border_radius=5)
        cor_d = tuple(c // 3 for c in cor_vida)
        pygame.draw.rect(superficie, cor_d,
                         (x, y, barra_w, barra_h), border_radius=5)
        pygame.draw.rect(superficie, cor_vida,
                         (x, y, int(barra_w * progresso), barra_h), border_radius=5)

        pulse     = int(180 + 75 * math.sin(pygame.time.get_ticks() * 0.005))
        cor_borda = tuple(min(255, c + pulse//3) for c in cor_vida)
        pygame.draw.rect(superficie, cor_borda,
                         (x, y, barra_w, barra_h), width=2, border_radius=5)

        fase_str = " ⚡ FASE 2 ⚡" if self.estado == self.FASE2 else ""
        label = self._fonte_nome.render(f"☠ {self.nome}{fase_str}", True, cor_vida)
        superficie.blit(label, (x + barra_w//2 - label.get_width()//2, y - 30))

        hp_txt = self._fonte_barra.render(
            f"{max(0, self.hp)} / {self.hp_max}", True, BRANCO)
        superficie.blit(hp_txt, hp_txt.get_rect(
            center=(x + barra_w//2, y + barra_h//2)))
