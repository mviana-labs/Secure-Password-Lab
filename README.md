# Laboratório de Conscientização sobre Senhas Seguras

Laboratório prático focado na análise de boas práticas de criação de senhas e na verificação de exposição em vazamentos públicos conhecidos, utilizando a API Pwned Passwords do Have I Been Pwned.

## Objetivo

Demonstrar a importância do uso de senhas fortes e únicas, evidenciando os riscos associados à reutilização de credenciais e ao uso de senhas já expostas em vazamentos de dados.

O projeto tem caráter educacional e pode ser aplicado em treinamentos, estudos individuais e ambientes de conscientização em segurança da informação.

## Ferramentas utilizadas

- Python 3  
- Biblioteca `requests`  
- API Pwned Passwords (Have I Been Pwned)  
- Tkinter (versão com interface gráfica)  

## Atividades realizadas

- Avaliação local da força da senha com base em critérios básicos de segurança  
- Verificação se a senha já apareceu em vazamentos públicos conhecidos  
- Exibição da quantidade de vezes que a senha foi encontrada em vazamentos  
- Apresentação de recomendações para melhoria da segurança da senha  
- Implementação de duas versões da aplicação:
  - Interface gráfica (GUI)  
  - Linha de comando (CLI)  

## Observações de segurança

- A aplicação não armazena senhas  
- A senha não é transmitida em texto claro  
- A verificação de vazamentos utiliza o modelo de **k-anonymity**, conforme recomendado pelo Have I Been Pwned  
- A verificação de vazamentos depende de conectividade com a internet  
- O projeto não deve ser utilizado como único mecanismo de validação de senhas em ambientes de produção  

**Desenvolvido por Matheus Viana © 2026**
