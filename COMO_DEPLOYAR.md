# Como colocar o projeto online (Grátis)

Para este projeto, que usa um banco de dados local (**SQLite**), a melhor opção gratuita é o **PythonAnywhere**. Ele permite que o banco de dados seja salvo e não "resetado" a cada reinicialização (como acontece no Render ou Vercel).

## Passo 1: Criar conta no PythonAnywhere
1. Acesse [pythonanywhere.com](https://www.pythonanywhere.com/).
2. Crie uma conta **"Beginner"** (Grátis).

## Passo 2: Subir os arquivos
Você tem duas opções: **Upload Manual** ou **GitHub**. O mais fácil para começar é o Upload Manual se não tiver git configurado.

### Opção A: Upload Manual
1. No PythonAnywhere, vá na aba **Files**.
2. Crie uma pasta chamada `mysite`.
3. Dentro dela, faça o upload de:
   - `app.py`
   - `requirements.txt`
   - A pasta `templates` (você terá que criar a pasta `templates` lá e subir os arquivos HTML dentro dela).

### Opção B: Via GitHub (Recomendado se usar Git)
1. No PythonAnywhere, vá em **Consoles** > **Bash**.
2. Clone seu repositório:
   ```bash
   git clone https://github.com/MikaelMarcos/instrumenta.git mysite
   ```

## Passo 3: Instalar Dependências
1. No PythonAnywhere, abra um console **Bash**.
2. Digite:
   ```bash
   cd mysite
   pip3 install -r requirements.txt
   ```

## Passo 4: Configurar a Web App
1. Vá na aba **Web** (canto superior direito).
2. Clique em **"Add a new web app"**.
3. Clique **Next**.
4. Escolha **Flask**.
5. Escolha a versão do Python (ex: **Python 3.10**).
6. No caminho do arquivo, coloque: `/home/SEU_USUARIO/mysite/app.py` (O sistema geralmente preenche automático, mas garanta que a pasta `mysite` está correta).

## Passo 5: Ajuste Final (WSGI)
1. Ainda na aba **Web**, role até a seção **Code**.
2. Clique no link do arquivo **WSGI configuration file** (algo como `/var/www/seuusuario_pythonanywhere_com_wsgi.py`).
3. O arquivo vai abrir no editor. Apague tudo e deixe algo parecido com isso (ou apenas descomente as linhas do Flask):
   ```python
   import sys
   import os

   path = '/home/SEU_USUARIO/mysite'
   if path not in sys.path:
       sys.path.append(path)

   from app import app as application
   ```
   *(Troque `SEU_USUARIO` pelo seu nome de usuário real)*.
4. Clique em **Save**.

## Passo 6: Rodar!
1. Volte na aba **Web**.
2. Clique no botão verde **Reload <seu-site>.pythonanywhere.com**.
3. Clique no link do seu site (topo da página) para abrir!

---

## Dica Importante sobre o Banco de Dados
O arquivo `field_assistant.db` será criado automaticamente na pasta `mysite` quando você rodar o app pela primeira vez. Como o PythonAnywhere mantém os arquivos, seus dados de aferição e tubulação ficarão salvos lá!
