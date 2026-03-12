##########################################################
#  Cinematica de Entrada do Boss — personalizada por boss.
#
#  MÁQUINA DE ESTADOS:
#   IDLE      → aguarda ser ativada
#   ESCURECE  → overlay vai de 0 a 180 alpha (30 frames)
#   AVISO     → nome + subtítulo do boss piscam (70 frames)
#   SHAKE     → screen shake crescente (20 frames)
#   SPAWN     → sinaliza ao main.py para spawnar o boss
#   COMPLETO  → cinematica encerrada
#
#  Cada boss tem nome, cor e frase de entrada únicos.
##########################################################

import pygame
import math
from src.config import *


# ── Dados únicos por boss (nivel_boss: 1, 2, 3) ────────────────────
BOSS_DATA = {
    1: {
        "nome":    "K R O N O S",
        "titulo":  "Entidade Biomecânica",
        "frase":   "O Devorador de Tempo desperta...",
        "cor":     (220, 20,  60),
        "cor_sub": (180, 80, 100),
    },
    2: {
        "nome":    "E R E B U S",
        "titulo":  "Sombra do Vazio",
        "frase":   "Das profundezas, ele retorna...",
        "cor":     (40,  80, 255),
        "cor_sub": (80, 120, 220),
    },
    3: {
        "nome":    "N E M E S I S",
        "titulo":  "Juizo Final",
        "frase":   "Nao ha escapatoria. Nao ha misericordia.",
        "cor":     (220, 170,  0),
        "cor_sub": (200, 130,  30),
    },
}


class BossIntro:
    IDLE      = "idle"
    ESCURECE  = "escurece"
    AVISO     = "aviso"
    SHAKE     = "shake"
    SPAWN     = "spawn"
    COMPLETO  = "completo"

    def __init__(self, largura, altura, camera):
        self.largura = largura
        self.altura  = altura
        self.camera  = camera

        self.estado  = self.IDLE
        self.timer   = 0

        self._nivel_boss  = 1
        self._dados       = BOSS_DATA[1]

        self.overlay_alpha = 0
        self._overlay_surf = pygame.Surface((largura, altura), pygame.SRCALPHA)

        self._fonte_nome   = pygame.font.SysFont("Arial", 72, bold=True)
        self._fonte_titulo = pygame.font.SysFont("Arial", 28, bold=True)
        self._fonte_frase  = pygame.font.SysFont("Arial", 22)

        self._spawnou = False

    def iniciar(self, nivel_boss: int = 1):
        if self.estado == self.IDLE:
            self._nivel_boss = max(1, min(3, nivel_boss))
            self._dados      = BOSS_DATA[self._nivel_boss]
            self.estado      = self.ESCURECE
            self.timer       = 0

    @property
    def ativo(self):
        return self.estado not in (self.IDLE, self.COMPLETO)

    @property
    def completo(self):
        return self.estado == self.COMPLETO

    def pronto_para_spawnar(self):
        if self.estado == self.SPAWN and not self._spawnou:
            self._spawnou = True
            return True
        return False

    def resetar(self):
        self.estado        = self.IDLE
        self.timer         = 0
        self.overlay_alpha = 0
        self._spawnou      = False

    def update(self):
        if not self.ativo:
            return

        self.timer += 1

        if self.estado == self.ESCURECE:
            self.overlay_alpha = min(190, int(190 * self.timer / 30))
            if self.timer >= 30:
                self.estado = self.AVISO
                self.timer  = 0

        elif self.estado == self.AVISO:
            if self.timer >= 70:
                self.estado = self.SHAKE
                self.timer  = 0

        elif self.estado == self.SHAKE:
            intensidade = 0.3 + (self.timer / 20) * 0.7
            self.camera.adicionar_shake(intensidade * 0.15)
            if self.timer >= 20:
                self.estado = self.SPAWN
                self.timer  = 0

        elif self.estado == self.SPAWN:
            if self.timer >= 5:
                self.estado        = self.COMPLETO
                self.overlay_alpha = 0

    def desenhar(self, superficie):
        if not self.ativo:
            return

        dados = self._dados
        cor   = dados["cor"]
        cx    = self.largura  // 2
        cy    = self.altura   // 2

        if self.overlay_alpha > 0:
            self._overlay_surf.fill((
                cor[0] // 8,
                cor[1] // 8,
                cor[2] // 8,
                self.overlay_alpha,
            ))
            superficie.blit(self._overlay_surf, (0, 0))

        if self.estado == self.AVISO:
            pisca = (self.timer // 8) % 2 == 0

            # Linhas decorativas laterais que crescem
            larg_linha = int(280 * min(1.0, self.timer / 20))
            pygame.draw.line(superficie, cor,
                             (cx - larg_linha, cy - 55),
                             (cx - 20,         cy - 55), 2)
            pygame.draw.line(superficie, cor,
                             (cx + 20,         cy - 55),
                             (cx + larg_linha, cy - 55), 2)

            # Nome do boss piscando
            if pisca:
                sombra = self._fonte_nome.render(dados["nome"], True, (0, 0, 0))
                superficie.blit(sombra, sombra.get_rect(center=(cx + 3, cy - 10 + 3)))
                for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
                    glow = self._fonte_nome.render(dados["nome"], True,
                                                   (cor[0]//2, cor[1]//2, cor[2]//2))
                    superficie.blit(glow, glow.get_rect(center=(cx+dx, cy-10+dy)))
                nome_surf = self._fonte_nome.render(dados["nome"], True, cor)
                superficie.blit(nome_surf, nome_surf.get_rect(center=(cx, cy - 10)))

            # Subtítulo sempre visível
            titulo_surf = self._fonte_titulo.render(dados["titulo"], True, dados["cor_sub"])
            superficie.blit(titulo_surf, titulo_surf.get_rect(center=(cx, cy + 50)))

            # Frase aparece gradualmente após 20 frames
            if self.timer > 20:
                alpha_frase = min(255, int(255 * (self.timer - 20) / 30))
                frase_surf  = self._fonte_frase.render(dados["frase"], True, (200, 200, 200))
                frase_surf.set_alpha(alpha_frase)
                superficie.blit(frase_surf, frase_surf.get_rect(center=(cx, cy + 90)))

        elif self.estado == self.SHAKE:
            alpha = max(0, int(255 * (1 - self.timer / 20)))
            nome_surf = self._fonte_nome.render(dados["nome"], True, cor)
            nome_surf.set_alpha(alpha)
            superficie.blit(nome_surf, nome_surf.get_rect(center=(cx, cy - 10)))
