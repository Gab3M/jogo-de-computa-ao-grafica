#####################################################
#  Classe Itens. Define o comportamento dos itens.
#
#  ItemArma: exibe barra de timer visual acima do sprite.
#  A barra vai de verde → amarelo → vermelho conforme
#  o tempo restante diminui. Pisca nos últimos 30%.
#####################################################

import pygame
import math
from src.config import *


class ItemArma(pygame.sprite.Sprite):
    def __init__(self, pos_mundo, tipo):
        super().__init__()
        self.tipo = tipo
        self.cor  = AMARELO if tipo == "Metralhadora" else ROXO
        self._construir_imagem()

        self.pos        = pygame.math.Vector2(pos_mundo)
        self.rect       = self.image.get_rect(center=self.pos)
        self.tempo_vida = ITEM_VIDA
        self._bob       = 0

    def _construir_imagem(self):
        """Estrela de 5 pontas colorida por tipo de arma."""
        s = 24
        self.image = pygame.Surface((s, s), pygame.SRCALPHA)
        cx, cy = s // 2, s // 2
        pontos = []
        for i in range(10):
            ang = math.radians(i * 36 - 90)
            r   = (s // 2 - 2) if i % 2 == 0 else (s // 4)
            pontos.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
        cor_escura = tuple(max(0, c - 80) for c in self.cor)
        pygame.draw.polygon(self.image, cor_escura, pontos)
        pontos2 = []
        for i in range(10):
            ang = math.radians(i * 36 - 90)
            r   = ((s // 2 - 5) if i % 2 == 0 else (s // 4 - 2))
            pontos2.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
        pygame.draw.polygon(self.image, self.cor, pontos2)
        pygame.draw.circle(self.image, (255, 255, 220), (cx, cy), 3)
        self._img_base = self.image.copy()

    def update(self):
        self._bob += 0.1
        self.rect.center = self.pos
        self.tempo_vida -= 1

        # Pisca nos últimos 30% do tempo
        if self.tempo_vida < ITEM_VIDA * 0.3:
            if (self.tempo_vida // 10) % 2 == 0:
                self.image.set_alpha(0)
            else:
                self.image.set_alpha(255)
        else:
            self.image.set_alpha(255)

        if self.tempo_vida <= 0:
            self.kill()

    def desenhar_timer(self, superficie, offset):
        """
        Desenha uma barra de timer circular acima do item.
        Chamado pelo main.py a cada frame (após blit dos sprites).
        offset = camera offset para converter posição mundo → tela.
        """
        if self.tempo_vida <= 0:
            return

        pct = self.tempo_vida / ITEM_VIDA

        # Só mostra a barra quando restar menos de 70% do tempo
        if pct > 0.70:
            return

        # Posição na tela
        tela_x = int(self.pos.x + offset.x)
        tela_y = int(self.pos.y + offset.y)

        # Cor: verde → amarelo → vermelho
        if pct > 0.40:
            r = int(255 * (1 - (pct - 0.40) / 0.30))
            g = 220
        else:
            r = 255
            g = int(220 * (pct / 0.40))
        cor_barra = (r, g, 0)

        # Barra horizontal acima do item (30px largura, 4px altura)
        barra_w = 30
        barra_h = 4
        bx = tela_x - barra_w // 2
        by = tela_y - 22

        # Fundo escuro
        pygame.draw.rect(superficie, (20, 20, 20),
                         (bx - 1, by - 1, barra_w + 2, barra_h + 2), border_radius=2)
        # Barra colorida
        pygame.draw.rect(superficie, cor_barra,
                         (bx, by, int(barra_w * pct), barra_h), border_radius=2)

        # Texto do tipo de arma (só aparece nos últimos 50%)
        if pct < 0.50:
            fonte = pygame.font.SysFont("Arial", 11, bold=True)
            txt   = fonte.render(self.tipo, True, self.cor)
            superficie.blit(txt, txt.get_rect(center=(tela_x, tela_y - 30)))
