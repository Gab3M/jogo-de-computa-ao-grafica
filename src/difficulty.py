##########################################################
#  Sistema de Balanceamento de Dificuldade
#
#  ESCALAS POR FASE:
#   - Velocidade dos inimigos
#   - HP dos inimigos
#   - Cadência de tiro
#   - Quantidade de inimigos
#   - Intervalo entre spawns
##########################################################

import sys
import os
import math

# Adiciona o diretório raiz do projeto ao PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import *


class BalanceadorDificuldade:
    """Ajusta parâmetros de jogo conforme a dificuldade aumenta."""
    
    # Configurações base
    VELOCIDADE_BASE = 2.5
    HP_BASE = 20
    CADENCIA_BASE = 800
    INTERVALO_SPAWN_BASE = 800
    
    def __init__(self):
        self.fase_atual = 1
    
    def atualizar_fase(self, nova_fase: int):
        """Atualiza a fase atual."""
        self.fase_atual = nova_fase
    
    def get_velocidade_inimigos(self) -> float:
        """Retorna velocidade dos inimigos para a fase atual."""
        # Crescimento exponencial suave
        # Fase 1 → 2.5
        # Fase 5 → ~3.5
        # Fase 10 → ~4.8
        escala = 1.0 + (self.fase_atual - 1) * 0.15
        return self.VELOCIDADE_BASE * escala
    
    def get_hp_inimigos(self, tipo_inimigo: str = "normal") -> int:
        """Retorna HP dos inimigos conforme tipo e fase."""
        # HP cresce gradually com as fases
        escala = 1.0 + (self.fase_atual - 1) * 0.2
        
        if tipo_inimigo == "rapido":
            return int(10 * escala)
        elif tipo_inimigo == "tank":
            return int(40 * escala)
        elif tipo_inimigo == "atirador":
            return int(15 * escala)
        elif tipo_inimigo == "viral":
            return int(12 * escala)
        elif tipo_inimigo == "necromante":
            return int(25 * escala)
        elif tipo_inimigo == "explosivo":
            return int(20 * escala)
        else:  # normal
            return int(20 * escala)
    
    def get_cadencia_disparo(self) -> int:
        """Retorna cadência de tiro dos inimigos (ms entre disparos)."""
        # Começa lentamente e fica mais rápido
        # Fase 1 → 800ms (~1.25/s)
        # Fase 5 → 600ms (~1.67/s)
        # Fase 10 → 450ms (~2.22/s)
        redacao = min(350, (self.fase_atual - 1) * 35)
        return max(400, self.CADENCIA_BASE - redacao)
    
    def get_intervalo_spawn(self) -> int:
        """Retorna intervalo entre spawns de inimigos (ms)."""
        # Decresce com as fases — mais inimigos aparecem mais rapidamente
        # Fase 1 → 800ms
        # Fase 5 → 600ms
        # Fase 10 → 400ms
        reducao = min(400, (self.fase_atual - 1) * 45)
        return max(300, self.INTERVALO_SPAWN_BASE - reducao)
    
    def get_quantidade_inimigos_onda(self, indice_onda: int) -> int:
        """Retorna quantidade total de inimigos em uma onda."""
        # Cresce com a fase
        # Fase 1 → 5-10 inimigos
        # Fase 5 → 12-18 inimigos
        # Fase 10 → 20-30 inimigos
        quantidade_base = 5 + self.fase_atual
        variacao = 1 + (self.fase_atual // 2)
        return quantidade_base + (indice_onda % variacao)
    
    def get_dano_inimigos(self) -> int:
        """Retorna dano dos inimigos ao jogador."""
        # Dano cresce lentamente
        # Fase 1 → 5
        # Fase 5 → 7
        # Fase 10 → 10
        dano = 5 + (self.fase_atual - 1) * 0.5
        return max(5, int(dano))
    
    def get_xp_drop_multiplicador(self) -> float:
        """Retorna multiplicador de XP para essa fase."""
        # Mais fases = mais XP recompensado
        # Fase 1 → 1.0x
        # Fase 5 → 1.4x
        # Fase 10 → 1.8x
        return 1.0 + (self.fase_atual - 1) * 0.1
    
    def get_info_balanceamento(self) -> dict:
        """Retorna informações de balanceamento para debug."""
        return {
            "fase": self.fase_atual,
            "velocidade_inimigos": f"{self.get_velocidade_inimigos():.2f}",
            "hp_inimigos": self.get_hp_inimigos(),
            "cadencia_disparo_ms": self.get_cadencia_disparo(),
            "intervalo_spawn_ms": self.get_intervalo_spawn(),
            "dano_inimigos": self.get_dano_inimigos(),
            "xp_multiplicador": f"{self.get_xp_drop_multiplicador():.2f}",
        }
