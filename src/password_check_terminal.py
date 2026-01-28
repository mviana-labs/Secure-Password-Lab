import hashlib
import argparse
import getpass
import requests

# ============================================================
# Configurações globais
# ============================================================
# Endpoint da API Pwned Passwords (Have I Been Pwned)
HIBP_URL = "https://api.pwnedpasswords.com/range/{}"

# Tempo máximo de espera para requisições HTTP (em segundos)
TIMEOUT = 10


# ============================================================
# Núcleo de verificação (compartilhado com a versão GUI)
# ============================================================
def senha_apareceu_em_vazamentos(senha: str) -> int:
    """
    Verifica se a senha informada já apareceu em vazamentos públicos conhecidos.

    A verificação é realizada de forma segura, sem transmissão da senha em texto
    claro, respeitando boas práticas de privacidade.

    :param senha: Senha informada pelo usuário
    :return: Quantidade de ocorrências encontradas (0 = não encontrada)
    """
    sha1 = hashlib.sha1(senha.encode("utf-8")).hexdigest().upper()
    prefixo, sufixo = sha1[:5], sha1[5:]

    resposta = requests.get(
        HIBP_URL.format(prefixo),
        timeout=TIMEOUT,
        headers={"User-Agent": "PasswordAwarenessCLI/1.0"},
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
    - Comprimento mínimo recomendado
    - Diversidade de tipos de caracteres
    - Identificação de padrões amplamente utilizados

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

    # Avaliação do comprimento da senha
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

    # Identificação de padrões comuns
    padroes_comuns = ["123", "senha", "password", "qwerty", "abc"]
    if any(p in senha.lower() for p in padroes_comuns):
        pontos -= 1
        dicas.append("Evite sequências ou padrões amplamente conhecidos.")

    # Classificação final
    if pontos >= 4:
        nivel = "FORTE"
    elif pontos >= 2:
        nivel = "OK"
    else:
        nivel = "FRACA"

    dicas.append("Não reutilize a mesma senha em serviços diferentes.")
    dicas.append("Considere o uso de um gerenciador de senhas.")

    return nivel, dicas


# ============================================================
# Interface de linha de comando (CLI)
# ============================================================
def main():
    """
    Ponto de entrada da aplicação em modo terminal.

    Permite a execução em ambientes sem interface gráfica, como
    servidores, máquinas virtuais e conexões remotas (SSH).
    """
    parser = argparse.ArgumentParser(
        description="Teste de Senhas – Conscientização (CLI)"
    )
    parser.add_argument(
        "--senha",
        help="Senha para teste (evite utilizar em ambientes compartilhados)",
    )
    args = parser.parse_args()

    print("\n=== Teste de Senhas – Conscientização (Terminal) ===")
    print("Desenvolvido por Matheus Viana © 2026\n")

    if args.senha:
        senha = args.senha
    else:
        senha = getpass.getpass("Digite a senha para testar (entrada oculta): ")

    if not senha:
        print("\nNenhuma senha informada.\n")
        return

    nivel, dicas = avaliar_senha_simples(senha)

    print("\nResultado:")
    print(f"Força da senha: {nivel}")

    try:
        vezes = senha_apareceu_em_vazamentos(senha)
        if vezes > 0:
            print("⚠️ Senha encontrada em vazamentos públicos.")
            print(f"Ocorrências registradas: {vezes:,}.")
            print("Recomendação: utilize uma nova senha exclusiva.")
        else:
            print("✅ Nenhuma ocorrência encontrada em vazamentos conhecidos.")
    except Exception:
        print("⚠️ Não foi possível verificar vazamentos no momento.")

    print("\nRecomendações:")
    for d in dicas:
        print(f"- {d}")

    print("")


if __name__ == "__main__":
    main()
