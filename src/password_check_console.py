import hashlib
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import requests

# ============================================================
# Configurações globais
# ============================================================
# Endpoint da API Pwned Passwords (Have I Been Pwned)
HIBP_URL = "https://api.pwnedpasswords.com/range/{}"

# Tempo máximo de espera para requisições HTTP (em segundos)
TIMEOUT = 10


# ============================================================
# Núcleo de verificação (compartilhado entre GUI e CLI)
# ============================================================
def senha_apareceu_em_vazamentos(senha: str) -> int:
    """
    Verifica se a senha já apareceu em vazamentos públicos conhecidos.

    Implementa o modelo de consulta segura baseado em prefixo de hash,
    garantindo que a senha nunca seja transmitida ou armazenada.

    :param senha: Senha informada pelo usuário
    :return: Número de ocorrências em vazamentos (0 = não encontrada)
    """
    sha1 = hashlib.sha1(senha.encode("utf-8")).hexdigest().upper()
    prefixo, sufixo = sha1[:5], sha1[5:]

    resposta = requests.get(
        HIBP_URL.format(prefixo),
        timeout=TIMEOUT,
        headers={"User-Agent": "PasswordAwarenessApp/1.0"},
    )
    resposta.raise_for_status()

    for linha in resposta.text.splitlines():
        hash_suffix, quantidade = linha.split(":")
        if hash_suffix.strip().upper() == sufixo:
            return int(quantidade.strip())

    return 0


def avaliar_senha_simples(senha: str):
    """
    Avalia a qualidade da senha com base em critérios básicos de segurança.

    Critérios considerados:
    - Comprimento mínimo
    - Diversidade de caracteres
    - Presença de padrões comuns

    :param senha: Senha informada pelo usuário
    :return: Tupla contendo (nível de força, lista de recomendações)
    """
    dicas = []
    pontos = 0
    tamanho = len(senha)

    tem_minuscula = any(c.islower() for c in senha)
    tem_maiuscula = any(c.isupper() for c in senha)
    tem_numero = any(c.isdigit() for c in senha)
    tem_simbolo = any(not c.isalnum() for c in senha)

    # Avaliação baseada no comprimento da senha
    if tamanho >= 16:
        pontos += 3
    elif tamanho >= 12:
        pontos += 2
    elif tamanho >= 8:
        pontos += 1
        dicas.append("Utilize pelo menos 12 caracteres.")
    else:
        dicas.append("Senha muito curta. O mínimo recomendado é 12 caracteres.")

    # Avaliação da diversidade de caracteres
    diversidade = sum([tem_minuscula, tem_maiuscula, tem_numero, tem_simbolo])
    if diversidade >= 3:
        pontos += 2
    else:
        dicas.append("Combine letras, números e símbolos.")

    # Identificação de padrões amplamente utilizados
    padroes_comuns = ["123", "senha", "password", "qwerty", "abc"]
    if any(p in senha.lower() for p in padroes_comuns):
        pontos -= 1
        dicas.append("Evite sequências ou padrões amplamente conhecidos.")

    # Classificação final
    if pontos >= 4:
        nivel = "Forte ✅"
    elif pontos >= 2:
        nivel = "Ok ⚠️"
    else:
        nivel = "Fraca ❌"

    dicas.append("Não reutilize a mesma senha em serviços diferentes.")
    dicas.append("Considere o uso de um gerenciador de senhas.")

    return nivel, dicas


# ============================================================
# Interface gráfica (GUI)
# ============================================================
class App(tk.Tk):
    """
    Aplicação gráfica para conscientização sobre criação de senhas seguras.
    """

    def __init__(self):
        super().__init__()
        self.title("Teste de Senhas – Conscientização")
        self.geometry("760x520")
        self.minsize(760, 520)
        self._construir_interface()

    def _construir_interface(self):
        """Inicializa e organiza todos os componentes visuais da aplicação."""
        self.configure(padx=18, pady=14)

        ttk.Label(
            self,
            text="Teste sua senha de forma simples e segura",
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w")

        ttk.Label(
            self,
            text="Avalia a força da senha e verifica exposição em vazamentos conhecidos.",
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(4, 14))

        container = ttk.Frame(self, padding=14)
        container.pack(fill="x")

        ttk.Label(
            container,
            text="Digite uma senha para testar:",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w")

        self.senha_var = tk.StringVar()
        self.entrada = ttk.Entry(
            container,
            textvariable=self.senha_var,
            show="•",
            font=("Segoe UI", 12),
        )
        self.entrada.pack(fill="x", pady=8)

        linha_opcoes = ttk.Frame(container)
        linha_opcoes.pack(fill="x")

        self.mostrar = tk.BooleanVar()
        ttk.Checkbutton(
            linha_opcoes,
            text="Mostrar senha",
            variable=self.mostrar,
            command=self._alternar_visibilidade,
        ).pack(side="left")

        ttk.Label(
            linha_opcoes,
            text="Recomendação: 14–20 caracteres.",
            foreground="#444",
        ).pack(side="right")

        botoes = ttk.Frame(container)
        botoes.pack(fill="x", pady=(10, 0))

        self.btn_testar = ttk.Button(
            botoes,
            text="Testar senha",
            command=self._iniciar_verificacao,
        )
        self.btn_testar.pack(side="left")

        ttk.Button(
            botoes,
            text="Limpar",
            command=self._limpar,
        ).pack(side="left", padx=8)

        self.progresso = ttk.Progressbar(container, mode="indeterminate")
        self.progresso.pack(fill="x", pady=(10, 0))

        area_resultado = ttk.Frame(self, padding=14)
        area_resultado.pack(fill="both", expand=True)

        ttk.Label(
            area_resultado,
            text="Resultado",
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w")

        self.texto = tk.Text(
            area_resultado,
            wrap="word",
            font=("Segoe UI", 10),
        )
        self.texto.pack(fill="both", expand=True, pady=(8, 0))
        self._atualizar_texto("Digite uma senha e clique em “Testar senha”.")

        rodape = ttk.Frame(self)
        rodape.pack(fill="x", pady=(8, 0))
        ttk.Label(
            rodape,
            text="Desenvolvido por Matheus Viana © 2026",
            font=("Segoe UI", 9),
            foreground="#666",
        ).pack(side="right")

        self.entrada.focus_set()

    def _alternar_visibilidade(self):
        """Exibe ou oculta a senha digitada."""
        self.entrada.configure(show="" if self.mostrar.get() else "•")

    def _atualizar_texto(self, mensagem: str):
        """Atualiza o conteúdo da área de resultado."""
        self.texto.configure(state="normal")
        self.texto.delete("1.0", "end")
        self.texto.insert("1.0", mensagem)
        self.texto.configure(state="disabled")

    def _limpar(self):
        """Limpa o campo de entrada e o resultado."""
        self.senha_var.set("")
        self._atualizar_texto("Digite uma senha e clique em “Testar senha”.")
        self.entrada.focus_set()

    def _set_busy(self, ativo: bool):
        """Controla o estado de carregamento da interface."""
        if ativo:
            self.btn_testar.state(["disabled"])
            self.progresso.start(10)
        else:
            self.btn_testar.state(["!disabled"])
            self.progresso.stop()

    def _iniciar_verificacao(self):
        """Inicia a análise da senha e a verificação de vazamentos."""
        senha = self.senha_var.get()
        if not senha:
            messagebox.showwarning("Atenção", "Digite uma senha para testar.")
            return

        nivel, dicas = avaliar_senha_simples(senha)

        mensagem = [f"Força da senha: {nivel}", "", "Recomendações:"]
        for d in dicas:
            mensagem.append(f"• {d}")
        mensagem.append("")
        mensagem.append("Verificando exposição em vazamentos...")

        self._atualizar_texto("\n".join(mensagem))
        self._set_busy(True)

        threading.Thread(
            target=self._verificar_vazamentos,
            args=(senha, nivel, dicas),
            daemon=True,
        ).start()

    def _verificar_vazamentos(self, senha: str, nivel: str, dicas: list[str]):
        """Executa a consulta de vazamentos sem bloquear a interface."""
        try:
            vezes = senha_apareceu_em_vazamentos(senha)

            mensagem = [f"Força da senha: {nivel}", ""]
            if vezes > 0:
                mensagem.append("⚠️ Senha encontrada em vazamentos.")
                mensagem.append(f"Ocorrências registradas: {vezes:,}.")
                mensagem.append("Recomendação: utilize uma nova senha exclusiva.")
            else:
                mensagem.append("✅ Nenhuma ocorrência encontrada em vazamentos conhecidos.")

            mensagem.append("")
            mensagem.append("Recomendações:")
            for d in dicas:
                mensagem.append(f"• {d}")

            self.after(0, lambda: self._atualizar_texto("\n".join(mensagem)))
        finally:
            self.after(0, lambda: self._set_busy(False))


if __name__ == "__main__":
    App().mainloop()
