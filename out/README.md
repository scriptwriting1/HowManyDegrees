## Pasta `out/`

Esta pasta contém **arquivos de saída e exemplos** do projeto.

### Por que esses arquivos já existem no repositório?

Os arquivos `weather.csv` e `weather.txt` já vêm com algumas linhas de **teste/exemplo** de propósito, para que quem
estiver avaliando o projeto (portfólio) consiga entender rapidamente o formato da saída sem precisar executar nada.

### O que acontece quando você executa o projeto?

Tanto o CLI quanto a GUI gravam em:

- `out/weather.csv`
- `out/weather.txt`

E a gravação é feita em modo **append** (adiciona no final), ou seja:

- não apaga o que já estava ali
- cada execução adiciona mais 1 linha (por execução) nos arquivos

Se você quiser “zerar” seus testes locais (ou remover os exemplos do repositório), basta apagar o conteúdo desses arquivos
(ou removê-los) e rodar novamente.
