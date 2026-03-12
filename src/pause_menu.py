##########################################################
#  Menu de Pausa — Interface visual melhorada
#
#  OPÇÕES:
#   - Continuar jogo
#   - Reiniciar fase
#   - Voltar ao menu principal
#   - Sair do jogo
##########################################################

import pygame
import sys
import os

# Adiciona o diretório raiz do projeto ao PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import *


class MenuPausa:
    """Menu visual de pausa com opções interativas."""
    
    def __init__(self, largura: int, altura: int):
        self.largura = largura
        self.altura = altura
        self.visivel = False
        self._selecionado = 0
        self._tick = 0
        
        # Fontes
        self._fonte_titulo = pygame.font.SysFont("Arial", 64, bold=True)
        self._fonte_opcao = pygame.font.SysFont("Arial", 32, bold=True)
        self._fonte_hint = pygame.font.SysFont("Arial", 20)
        
        # Opções do menu
        self._opcoes = [
            {"label": "◄  CONTINUAR",     "acao": "continuar"},
            {"label": "↻  REINICIAR FASE", "acao": "reiniciar"},
            {"label": "⌂  MENU PRINCIPAL", "acao": "menu"},
            {"label": "✕  SAIR DO JOGO",   "acao": "sair"},
        ]
    
    def processar_evento(self, evento) -> str | None:
        """
        Processa eventos de entrada no menu de pausa.
        
        Returns:
            'continuar', 'reiniciar', 'menu', 'sair' ou None
        """
        if not self.visivel:
            return None
        
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_UP, pygame.K_w):
                self._selecionado = (self._selecionado - 1) % len(self._opcoes)
            elif evento.key in (pygame.K_DOWN, pygame.K_s):
                self._selecionado = (self._selecionado + 1) % len(self._opcoes)
            elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self._opcoes[self._selecionado]["acao"]
            elif evento.key == pygame.K_ESCAPE:
                return "continuar"  # ESC retorna ao jogo
        
        elif evento.type == pygame.JOYBUTTONDOWN:
            if evento.button == 0:  # A button (continuar)
                return self._opcoes[self._selecionado]["acao"]
            elif evento.button == 7:  # Start (voltar ao jogo)
                return "continuar"
            elif evento.button == 12:  # D-pad up
                self._selecionado = (self._selecionado - 1) % len(self._opcoes)
            elif evento.button == 13:  # D-pad down
                self._selecionado = (self._selecionado + 1) % len(self._opcoes)
        
        elif evento.type == pygame.MOUSEMOTION:
            # Hover com mouse
            for i in range(len(self._opcoes)):
                rect = self._rect_opcao(i)
                if rect.collidepoint(evento.pos):
                    self._selecionado = i
        
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:  # Click esquerdo
                for i in range(len(self._opcoes)):
                    if self._rect_opcao(i).collidepoint(evento.pos):
                        return self._opcoes[i]["acao"]
        
        return None
    
    def atualizar(self):
        """Atualiza animações do menu."""
        self._tick += 1
    
    def desenhar(self, tela: pygame.Surface):
        """Desenha o menu de pausa na tela."""
        if not self.visivel:
            return
        
        # ── Overlay escuro semi-transparente ────────────────
        overlay = pygame.Surface((self.largura, self.altura))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        tela.blit(overlay, (0, 0))
        
        # ── Título "PAUSADO" ───────────────────────────────
        titulo = self._fonte_titulo.render("II  PAUSADO", True, (255, 200, 0))
        titulo_rect = titulo.get_rect(center=(self.largura // 2, self.altura // 4))
        # Glow effect
        sombra = self._fonte_titulo.render("II  PAUSADO", True, (255, 100, 0))
        tela.blit(sombra, (titulo_rect.x + 4, titulo_rect.y + 4))
        tela.blit(titulo, titulo_rect)
        
        # ── Opções do menu ─────────────────────────────────
        cy = self.altura // 2 - 60
        for i, opcao in enumerate(self._opcoes):
            self._desenhar_opcao(tela, i, opcao, cy + i * 70)
        
        # ── Hints de controle ───────────────────────────────
        hint = self._fonte_hint.render("↑↓ Navegar   ENTER: Selecionar   ESC: Continuar", 
                                       True, (150, 150, 150))
        hint_rect = hint.get_rect(center=(self.largura // 2, self.altura - 40))
        tela.blit(hint, hint_rect)
    
    def _desenhar_opcao(self, tela: pygame.Surface, idx: int, opcao: dict, cy: int):
        """Desenha uma opção individual do menu."""
        selecionado = idx == self._selecionado
        
        # Cor baseia-se na seleção
        cor = (0, 255, 150) if selecionado else (200, 200, 200)
        
        # Escala pulsante se selecionado
        escala = 1.15 if selecionado else 1.0
        if selecionado:
            # Pulso sinusoidal
            import math
            escala += math.sin(self._tick * 0.1) * 0.05
        
        # Renderizar texto
        texto = self._fonte_opcao.render(opcao["label"], True, cor)
        
        if escala != 1.0:
            novo_tamanho = (int(texto.get_width() * escala), 
                          int(texto.get_height() * escala))
            texto = pygame.transform.scale(texto, novo_tamanho)
        
        # Desenhar com sombra de profundidade
        rect = texto.get_rect(center=(self.largura // 2, cy))
        
        if selecionado:
            # Sombra colorida
            sombra = self._fonte_opcao.render(opcao["label"], True, (0, 100, 50))
            if escala != 1.0:
                novo_tamanho = (int(sombra.get_width() * escala), 
                              int(sombra.get_height() * escala))
                sombra = pygame.transform.scale(sombra, novo_tamanho)
            tela.blit(sombra, (rect.x + 3, rect.y + 3))
            
            # Box de seleção
            box_rect = rect.inflate(40, 20)
            pygame.draw.rect(tela, (0, 255, 150), box_rect, 3, border_radius=10)
        
        tela.blit(texto, rect)
    
    def _rect_opcao(self, idx: int) -> pygame.Rect:
        """Retorna o rect aproximado de uma opção para hover detection."""
        cy = self.altura // 2 - 60 + idx * 70
        return pygame.Rect(self.largura // 2 - 200, cy - 25, 400, 50)
    
    def mostrar(self):
        """Mostra o menu de pausa."""
        self.visivel = True
        self._selecionado = 0
    
    def esconder(self):
        """Esconde o menu de pausa."""
        self.visivel = False
