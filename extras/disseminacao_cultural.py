import random
import sys
import pygame

# --- CONFIGURAÇÕES VISUAIS E DE TELA ---
GRID_SIZE = 10
CELL_SIZE = 60
BOARD_MARGIN_TOP = 80
BOARD_MARGIN_LEFT = 20
PANEL_WIDTH = 320

WIDTH = BOARD_MARGIN_LEFT + (GRID_SIZE * CELL_SIZE) + PANEL_WIDTH + 40
HEIGHT = BOARD_MARGIN_TOP + (GRID_SIZE * CELL_SIZE) + 40
FPS = 30

# Paleta de Cores
PALETA = {
    "fundo": (245, 247, 250),
    "grade": (200, 205, 215),
    "texto": (40, 44, 52),
    "texto_suave": (100, 110, 120),
    "painel": (255, 255, 255),
    "botao": (79, 70, 229),
    "botao_texto": (255, 255, 255),
    "destaque": (234, 179, 8),
    "sucesso": (16, 185, 129),
}

# --- DADOS DOS AGENTES ---
SEXOS = ["Masculino", "Feminino"]
PERIODOS = [f"{i}º Período" for i in range(1, 9)]

CURSOS_UFT = [
    "Agronomia", "Arquitetura e Urbanismo", "Ciência da Computação",
    "Ciências Biológicas", "Ciências Contábeis", "Ciências Econômicas",
    "Direito", "Enfermagem", "Engenharia Ambiental", "Engenharia Civil",
    "Engenharia de Alimentos", "Engenharia Elétrica", "Engenharia Florestal",
    "Farmácia", "Filosofia", "Física", "Geografia", "História", "Jornalismo",
    "Letras", "Matemática", "Medicina", "Medicina Veterinária", "Nutrição",
    "Pedagogia", "Psicologia", "Química", "Teatro", "Zootecnia"
]

RELIGIOES_BR = [
    "Catolicismo", "Evangelismo", "Sem Religião / Ateísmo", "Espiritismo",
    "Matriz Africana (Umbanda/Candomblé)", "Outras Cristãs", "Buddhismo / Outras Oriental"
]

ESTADOS_BR = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG",
    "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
]

CORES_RELIGIAO = {
    "Catolicismo": (239, 68, 68),
    "Evangelismo": (59, 130, 246),
    "Sem Religião / Ateísmo": (107, 114, 128),
    "Espiritismo": (168, 85, 247),
    "Matriz Africana (Umbanda/Candomblé)": (234, 179, 8),
    "Outras Cristãs": (16, 185, 129),
    "Buddhismo / Outras Oriental": (236, 72, 153),
}


class Agente:
    """Representa um participante do experimento sociocultural."""

    def __init__(self, agent_id, x, y):
        self.id = agent_id
        self.x = x
        self.y = y

        self.sexo = random.choice(SEXOS)
        self.periodo = random.choice(PERIODOS)
        self.curso = random.choice(CURSOS_UFT)
        self.religiao = random.choice(RELIGIOES_BR)
        self.origem = random.choice(ESTADOS_BR)

        self.cor = CORES_RELIGIAO[self.religiao]

    def calcular_similaridade(self, outro):
        """Mede a afinidade entre dois agentes. Religião e Origem têm mais peso."""
        pesos = {
            "religiao": 3.0,
            "origem": 3.0,
            "curso": 1.0,
            "periodo": 1.0,
            "sexo": 1.0,
        }

        pontos = 0.0
        if self.religiao == outro.religiao:
            pontos += pesos["religiao"]
        if self.origem == outro.origem:
            pontos += pesos["origem"]
        if self.curso == outro.curso:
            pontos += pesos["curso"]
        if self.periodo == outro.periodo:
            pontos += pesos["periodo"]
        if self.sexo == outro.sexo:
            pontos += pesos["sexo"]

        return pontos / sum(pesos.values())


class Simulacao:
    """Gerencia as regras de negócio e a movimentação dos agentes."""

    def __init__(self, num_agentes=40):
        self.num_agentes = num_agentes
        self.rodadas = 0
        self.rodando = False
        self.agentes = []
        self.agente_selecionado = None
        self.posicao_alvo = None
        self.reset()

    def reset(self, novo_num_agentes=None):
        if novo_num_agentes is not None:
            self.num_agentes = novo_num_agentes

        self.rodadas = 0
        self.rodando = False
        self.agente_selecionado = None
        self.posicao_alvo = None

        # Sorteia posições iniciais sem sobreposição
        posicoes = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)]
        random.shuffle(posicoes)

        self.agentes = [
            Agente(i + 1, posicoes[i][0], posicoes[i][1])
            for i in range(min(self.num_agentes, len(posicoes)))
        ]

    def obter_mapa_ocupacao(self):
        return {(ag.x, ag.y): ag for ag in self.agentes}

    def passo(self):
        """Executa uma rodada escolhendo um agente aleatório para buscar novos vizinhos."""
        if not self.agentes:
            return

        self.rodadas += 1
        agente = random.choice(self.agentes)
        self.agente_selecionado = agente

        mapa_ocupado = self.obter_mapa_ocupacao()
        melhor_posicao = (agente.x, agente.y)
        maior_satisfacao = self._avaliar_vizinhanca(agente, agente.x, agente.y, mapa_ocupado)

        # Procura por células vazias em um raio de até 2 casas
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx == 0 and dy == 0:
                    continue

                nx, ny = agente.x + dx, agente.y + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and (nx, ny) not in mapa_ocupado:
                    satisfacao = self._avaliar_vizinhanca(agente, nx, ny, mapa_ocupado)
                    if satisfacao > maior_satisfacao:
                        maior_satisfacao = satisfacao
                        melhor_posicao = (nx, ny)

        # Move o agente apenas se encontrar um lugar com maior afinidade
        if melhor_posicao != (agente.x, agente.y):
            self.posicao_alvo = melhor_posicao
            agente.x, agente.y = melhor_posicao
        else:
            self.posicao_alvo = None

    def _avaliar_vizinhanca(self, agente, x, y, mapa_ocupado):
        """Calcula a média de similaridade com os vizinhos diretos (raio 1)."""
        vizinhos = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                vizinho = mapa_ocupado.get((x + dx, y + dy))
                if vizinho and vizinho != agente:
                    vizinhos.append(vizinho)

        if not vizinhos:
            return 0.1  # Pequena atração por espaços abertos

        return sum(agente.calcular_similaridade(v) for v in vizinhos) / len(vizinhos)


class AplicacaoSimulador:
    """Gerencia a interface gráfica (Pygame) e a interação com o usuário."""

    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.tela = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Experimento Social - Agrupamento Espontâneo")
        self.relogio = pygame.time.Clock()

        # Fontes organizadas por tamanho
        self.fontes = {
            "grande": pygame.font.SysFont("Arial", 22, bold=True),
            "media": pygame.font.SysFont("Arial", 16, bold=True),
            "pequena": pygame.font.SysFont("Arial", 14),
        }

        self.simulacao = Simulacao(num_agentes=40)
        self._configurar_botoes()

    def _configurar_botoes(self):
        base_x = BOARD_MARGIN_LEFT + GRID_SIZE * CELL_SIZE + 30
        self.btn_iniciar = pygame.Rect(base_x, 20, 90, 36)
        self.btn_reiniciar = pygame.Rect(base_x + 100, 20, 90, 36)
        self.btn_menos = pygame.Rect(base_x + 200, 20, 36, 36)
        self.btn_mais = pygame.Rect(base_x + 242, 20, 36, 36)

    def executar(self):
        rodando = True
        while rodando:
            rodando = self._tratar_eventos()

            if self.simulacao.rodando:
                self.simulacao.passo()

            self._desenhar()
            self.relogio.tick(FPS)

        pygame.quit()
        sys.exit()

    def _tratar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False

            if evento.type == pygame.MOUSEBUTTONDOWN:
                self._tratar_cliques(evento.pos)

        return True

    def _tratar_cliques(self, pos):
        mx, my = pos

        # Cliques nos botões da interface
        if self.btn_iniciar.collidepoint(mx, my):
            self.simulacao.rodando = not self.simulacao.rodando

        elif self.btn_reiniciar.collidepoint(mx, my):
            self.simulacao.reset()

        elif self.btn_menos.collidepoint(mx, my):
            nova_qtd = max(10, self.simulacao.num_agentes - 5)
            self.simulacao.reset(nova_qtd)

        elif self.btn_mais.collidepoint(mx, my):
            nova_qtd = min(90, self.simulacao.num_agentes + 5)
            self.simulacao.reset(nova_qtd)

        # Clique nas células do tabuleiro
        elif self._clique_no_tabuleiro(mx, my):
            gx = (mx - BOARD_MARGIN_LEFT) // CELL_SIZE
            gy = (my - BOARD_MARGIN_TOP) // CELL_SIZE
            mapa = self.simulacao.obter_mapa_ocupacao()

            if (gx, gy) in mapa:
                self.simulacao.agente_selecionado = mapa[(gx, gy)]
                self.simulacao.posicao_alvo = None

    def _clique_no_tabuleiro(self, mx, my):
        tabuleiro_largura = GRID_SIZE * CELL_SIZE
        return (
            BOARD_MARGIN_LEFT <= mx < BOARD_MARGIN_LEFT + tabuleiro_largura
            and BOARD_MARGIN_TOP <= my < BOARD_MARGIN_TOP + tabuleiro_largura
        )

    # --- MÉTODOS DE RENDERIZAÇÃO ---
    def _desenhar(self):
        self.tela.fill(PALETA["fundo"])

        self._desenhar_cabecalho()
        self._desenhar_tabuleiro()
        self._desenhar_agentes()
        self._desenhar_painel_lateral()

        pygame.display.flip()

    def _desenhar_cabecalho(self):
        txt = self.fontes["grande"].render(
            "Experimento Social: Organização Espontânea", True, PALETA["texto"]
        )
        self.tela.blit(txt, (BOARD_MARGIN_LEFT, 25))

    def _desenhar_tabuleiro(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                x = BOARD_MARGIN_LEFT + r * CELL_SIZE
                y = BOARD_MARGIN_TOP + c * CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

                pygame.draw.rect(self.tela, (255, 255, 255), rect)
                pygame.draw.rect(self.tela, PALETA["grade"], rect, 1)

        # Destaque no agente selecionado
        ag = self.simulacao.agente_selecionado
        if ag:
            sx = BOARD_MARGIN_LEFT + ag.x * CELL_SIZE
            sy = BOARD_MARGIN_TOP + ag.y * CELL_SIZE
            pygame.draw.rect(
                self.tela, PALETA["destaque"], (sx, sy, CELL_SIZE, CELL_SIZE), 3
            )

    def _desenhar_agentes(self):
        for ag in self.simulacao.agentes:
            cx = BOARD_MARGIN_LEFT + ag.x * CELL_SIZE + CELL_SIZE // 2
            cy = BOARD_MARGIN_TOP + ag.y * CELL_SIZE + CELL_SIZE // 2
            raio = CELL_SIZE // 2 - 8

            pygame.draw.circle(self.tela, ag.cor, (cx, cy), raio)
            pygame.draw.circle(self.tela, (30, 30, 30), (cx, cy), raio, 1)

            # Rótulo com o ID
            txt = self.fontes["pequena"].render(str(ag.id), True, (255, 255, 255))
            txt_rect = txt.get_rect(center=(cx, cy))
            self.tela.blit(txt, txt_rect)

    def _desenhar_painel_lateral(self):
        px = BOARD_MARGIN_LEFT + GRID_SIZE * CELL_SIZE + 20
        py = BOARD_MARGIN_TOP
        painel_rect = pygame.Rect(px, py, PANEL_WIDTH, GRID_SIZE * CELL_SIZE)

        pygame.draw.rect(self.tela, PALETA["painel"], painel_rect, border_radius=8)
        pygame.draw.rect(self.tela, PALETA["grade"], painel_rect, 1, border_radius=8)

        self._desenhar_botoes()
        self._desenhar_estatisticas(px + 15, py + 20)

    def _desenhar_botoes(self):
        texto_iniciar = "Pausar" if self.simulacao.rodando else "Iniciar"

        self._desenhar_botao(self.btn_iniciar, texto_iniciar)
        self._desenhar_botao(self.btn_reiniciar, "Reiniciar")
        self._desenhar_botao(self.btn_menos, "-", fonte_ch="grande")
        self._desenhar_botao(self.btn_mais, "+", fonte_ch="grande")

    def _desenhar_botao(self, rect, texto, fonte_ch="media"):
        pygame.draw.rect(self.tela, PALETA["botao"], rect, border_radius=6)
        surf = self.fontes[fonte_ch].render(texto, True, PALETA["botao_texto"])
        self.tela.blit(surf, surf.get_rect(center=rect.center))

    def _desenhar_estatisticas(self, x, y):
        # Informações da rodada
        txt_rodadas = self.fontes["media"].render(
            f"Rodadas executadas: {self.simulacao.rodadas}", True, PALETA["texto"]
        )
        self.tela.blit(txt_rodadas, (x, y))

        txt_agentes = self.fontes["media"].render(
            f"Qtd. Agentes: {self.simulacao.num_agentes}", True, PALETA["texto"]
        )
        self.tela.blit(txt_agentes, (x, y + 25))

        # Divisor
        y_div = y + 60
        pygame.draw.line(
            self.tela, PALETA["grade"], (x, y_div), (x + PANEL_WIDTH - 30, y_div)
        )

        # Informações do Agente Selecionado
        y_detalhes = y_div + 15
        self.tela.blit(
            self.fontes["grande"].render("Agente Selecionado", True, PALETA["texto"]),
            (x, y_detalhes),
        )

        ag = self.simulacao.agente_selecionado
        if not ag:
            txt_vazio = self.fontes["pequena"].render(
                "Clique em um agente no tabuleiro", True, PALETA["texto_suave"]
            )
            self.tela.blit(txt_vazio, (x, y_detalhes + 35))
            return

        # Círculo com a cor representativa
        pygame.draw.circle(self.tela, ag.cor, (x + 10, y_detalhes + 42), 8)
        pygame.draw.circle(self.tela, (0, 0, 0), (x + 10, y_detalhes + 42), 8, 1)

        txt_id = self.fontes["media"].render(f"Agente ID: {ag.id}", True, PALETA["texto"])
        self.tela.blit(txt_id, (x + 28, y_detalhes + 32))

        # Lista de Atributos
        atributos = [
            ("Sexo:", ag.sexo),
            ("Período:", ag.periodo),
            ("Curso:", ag.curso),
            ("Religião:", ag.religiao),
            ("Origem:", ag.origem),
            ("Posição:", f"({ag.x}, {ag.y})"),
        ]

        curr_y = y_detalhes + 65
        for rótulo, valor in atributos:
            lbl_surf = self.fontes["media"].render(rótulo, True, PALETA["texto_suave"])
            val_surf = self.fontes["pequena"].render(str(valor), True, PALETA["texto"])
            self.tela.blit(lbl_surf, (x, curr_y))
            self.tela.blit(val_surf, (x + 75, curr_y + 2))
            curr_y += 24

        if self.simulacao.posicao_alvo:
            mov_txt = self.fontes["pequena"].render(
                f"-> Moveu para: {self.simulacao.posicao_alvo}", True, PALETA["sucesso"]
            )
            self.tela.blit(mov_txt, (x, curr_y + 8))


if __name__ == "__main__":
    app = AplicacaoSimulador()
    app.executar()