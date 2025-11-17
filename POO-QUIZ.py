from abc import ABC, abstractmethod
import datetime


class Pontuavel(ABC):

    @abstractmethod
    def calcular_pontuacao(self):
        pass


class Pergunta(Pontuavel, ABC):

    def __init__(self, texto, resposta_correta, valor_base):
        self.texto = texto
        self.resposta_correta = resposta_correta
        self.valor_base = valor_base

    @property
    def texto(self):
        return self._texto

    @texto.setter
    def texto(self, valor):
        if not valor or not valor.strip():
            raise ValueError("Texto da pergunta inválido")
        self._texto = valor

    @property
    def resposta_correta(self):
        return self._resposta_correta

    @resposta_correta.setter
    def resposta_correta(self, valor):
        if not valor or not valor.strip():
            raise ValueError("Resposta correta inválida")
        self._resposta_correta = valor.strip().upper()

    @property
    def valor_base(self):
        return self._valor_base

    @valor_base.setter
    def valor_base(self, valor):
        if valor <= 0:
            raise ValueError("Valor base deve ser positivo")
        self._valor_base = valor

    @abstractmethod
    def verificar_resposta(self, resposta):
        pass


class PerguntaME(Pergunta):

    def __init__(self, texto, resposta_correta, alternativas, valor_base):
        super().__init__(texto, resposta_correta, valor_base)
        self.alternativas = alternativas

    def verificar_resposta(self, resposta):
        if not resposta:
            return False

        resposta = resposta.strip().upper()

        if len(resposta) == 1:
            return resposta == self.resposta_correta
        
        for alternativa in self.alternativas:
            if resposta == alternativa.upper():
                return alternativa[0].upper() == self.resposta_correta
        return False

    def calcular_pontuacao(self):
        return self.valor_base

    def exibir_alternativas(self):
        return "\n".join(self.alternativas)


class PerguntaVF(Pergunta):

    def __init__(self, texto, verdadeiro, valor_base):
        resposta_correta = "V" if verdadeiro else "F"
        self.verdadeiro = verdadeiro
        super().__init__(texto, resposta_correta, valor_base)

    def verificar_resposta(self, resposta):
        if not resposta:
            return False

        resposta = resposta.strip().upper()

        if resposta in ["V", "VERDADEIRO", "TRUE"]:
            return self.verdadeiro
        if resposta in ["F", "FALSO", "FALSE"]:
            return not self.verdadeiro
        
        return False

    def calcular_pontuacao(self):
        return max(1, self.valor_base // 2)


class Jogador:

    def __init__(self, nome):
        self.nome = nome
        self.pontos = 0

    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, valor):
        if not valor or not valor.strip():
            raise ValueError("Nome inválido")
        self._nome = valor.strip()

    @property
    def pontos(self):
        return self._pontos

    @pontos.setter
    def pontos(self, valor):
        if valor < 0:
            raise ValueError("Pontos não podem ser negativos")
        self._pontos = valor

    def adicionar_pontos(self, valor):
        if valor < 0:
            raise ValueError("Valor de pontos inválido")
        self._pontos += valor


class SistemaLogs:

    @staticmethod
    def registrar_evento(msg, codigo=None, contexto=None):
        agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        texto = f"[{agora}] {msg}"

        if codigo is not None:
            texto += f" (COD={codigo})"
        if contexto is not None:
            texto += f" [{contexto}]"

        print(texto)


class Quiz:

    total_execucoes = 0
    maior_pontuacao_global = 0
    melhor_jogador_global = "Ninguém"

    def __init__(self, perguntas, jogador):
        self.perguntas = perguntas
        self.jogador = jogador
        Quiz.total_execucoes += 1

    @staticmethod
    def menu():
        perguntas = Quiz.criar_perguntas()
        jogador_atual = None

        while True:
            print("\n=========== MENU DO QUIZ ===========")
            print("1) Iniciar jogo")
            print("2) Criar novo jogador")
            print("3) Ver maior pontuação global")
            print("4) Ver total de quizzes jogados")
            print("5) Sair")
            print("====================================")
            opcao = input("Escolha uma opção: ").strip()

            if opcao == "1":
                if jogador_atual is None:
                    jogador_atual = Jogador(input("Nome do jogador: "))
                quiz = Quiz(perguntas, jogador_atual)
                quiz.iniciar()
            
            elif opcao == "2":
                jogador_atual = Jogador(input("Nome do novo jogador: "))
                print("Jogador atualizado!")
            
            elif opcao == "3":
                print("\n===== MAIOR PONTUAÇÃO GLOBAL =====")
                print("Jogador:", Quiz.melhor_jogador_global)
                print("Pontuação:", Quiz.maior_pontuacao_global)
            
            elif opcao == "4":
                print("Total de quizzes jogados:", Quiz.total_execucoes)
            
            elif opcao == "5":
                print("Saindo...")
                break
            
            else:
                print("Opção inválida.")

    def iniciar(self):
        SistemaLogs.registrar_evento("Iniciando quiz...", contexto="EXECUÇÃO")

        for indice, pergunta in enumerate(self.perguntas, start=1):
            print("\n(Digite MENU para voltar ao menu principal)")
            print(f"\nPergunta {indice}:")
            print(pergunta.texto)

            if isinstance(pergunta, PerguntaME):
                print(pergunta.exibir_alternativas())

            resposta = input("Sua resposta: ").strip()

            if resposta.upper() == "MENU":
                print("\nVoltando ao menu...")
                return

            acertou = pergunta.verificar_resposta(resposta)
            pontos = pergunta.calcular_pontuacao() if acertou else 0
            self.jogador.adicionar_pontos(pontos)

            SistemaLogs.registrar_evento(
                f"Pergunta {indice} respondida | Acertou: {acertou} | Pontos: +{pontos}",
                codigo=200
            )

        self.finalizar()

    def finalizar(self):
        print("\n=========== RESULTADO ===========")
        print("Jogador:", self.jogador.nome)
        print("Pontuação final:", self.jogador.pontos)

        if self.jogador.pontos > Quiz.maior_pontuacao_global:
            Quiz.maior_pontuacao_global = self.jogador.pontos
            Quiz.melhor_jogador_global = self.jogador.nome
            print("\nNOVO RECORDE GLOBAL!!!")

        print("=================================")

    @staticmethod
    def criar_perguntas():
        p1 = PerguntaME(
            "Qual o maior oceano do mundo?",
            "b",
            ["A) atlântico", "B) pacifico", "C) indico", "D) artico"],
            4
        )

        p2 = PerguntaVF(
            "O machado de Assis escreveu 11 Romances?",
            False,
            1
        )

        p3 = PerguntaME(
            "O coração é um?",
            "a",
            ["A) Musculo", "B) Cartilagem", "C) Tendão", "D) Osso"],
            4
        )

        p4 = PerguntaVF(
            "Marte é o maior planeta do sistema solar?",
            False,
            1
        )

        return [p1, p2, p3, p4]


if __name__ == "__main__":
    Quiz.menu()
