# USJT Grades Bot

Este sistema tem como objetivo automatizar a consulta de notas no Ulife
Toda vez que uma nota for postada e/ou alterada, ele preservará o historico de mudanças

# Como usar
1) Preencha as informações dentro do arquivo ".env" na pasta "usjt" (são valores pessoais, não divulgue!);
2) Rode o comando "docker-compose up -d";
3) Se for colocar em um servidor, lembre-se de fazer as alterações necessárias.

Ele também pode ser alterado para mandar as notas por onde desejar, seja por e-mail (utilizando ferramentas como SendGrid), Discord (É uma API Rest, basta fazer a requisição pro seu endpoint) e entre outros, basta editar o arquivo popular a função "notify_changes" no arquivo "tasks.py" dentro do app "grades".


# Caracteristicas
- Autônomo;
- REST;
- Pessoal;
- Customizável.
