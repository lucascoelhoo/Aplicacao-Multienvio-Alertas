# Aplicacao-Multienvio-Alertas

- Desenvolvido por: Lucas Coelho de Almeida

- Objetivo: Aplicação que pode ser usada para interface com outros programas ou composições de software. Usada para envio de alertas por Telegram, Email e SMS. Pode ser útil também na interface com sistemas legados, como foi o caso da necessidade de criação. No caso, tratava-se de um sistema SCADA legado que monitorava um data center de grande porte e que tinha sérias limitações de envio de alertas, o que foi resolvido através do uso dessa aplicação.
 
- Forma de uso: Verificar os comentários dos arquivos de código fonte. A aplicação foi feita para uso em Windows, caso seja usada em ambientes Linux, é necessário revisar comandos de linha de comando e acessos usando "relative paths", entre outros. De forma básica, trata-se de um script mestre que, ao ser chamado, recebe três argumentos na linha de comando, um para a mensagem do email, outro com a mensagem do sms e outro com a mensagem a ser enviada para o bot Telegram. Os destinos ficam listados de forma simples em arquvos de texto na própria pasta. O envio de SMS é feito com gerenciamento de filas em servidor local que a própria aplicação cria, mas é necessário ter um modem GSM ligado ao computador e também colocar a porta de comunicação desse modem no sistema operacional (no caso do Windows, a COM).
