# 🧾 NotaWatch — Monitor de PDFs com envio automático para AWS S3

NotaWatch é uma aplicação em Python com interface gráfica que monitora uma pasta local (como C:/pdf) e realiza o envio automático de arquivos .pdf (por exemplo, notas fiscais eletrônicas) para um bucket S3 da AWS, com controle diário de envios e logs completos.

🚀 Funcionalidades
🧠 Detecção inteligente de arquivos novos
Monitora automaticamente arquivos .pdf criados hoje ou ontem.

☁️ Envio seguro para a AWS (S3)
Upload dos arquivos para um bucket S3, com verificação de duplicidade.

📊 Contador de notas enviadas
Exibe em tempo real o total de notas enviadas no dia.

🔒 Controle de arquivos já enviados
Garante que arquivos não sejam reenviados.

🧰 Interface gráfica com Tkinter
Simples, direta e com status visuais de conexão e envio.

📝 Logs de auditoria automáticos
Tudo registrado: início, parada, conexões e arquivos enviados.

🖼️ Interface
<img src="https://via.placeholder.com/400x250.png?text=NotaWatch+Interface+Mockup" alt="interface do sistema" width="400" />
🛠️ Instalação
Clone o repositório:

```bash
Copiar
Editar
git clone https://github.com/seu-usuario/notawatch.git
cd notawatch
Instale as dependências:

```bash
Copiar
Editar
pip install -r requirements.txt
Configure as variáveis de ambiente:

Crie um arquivo .env com o seguinte conteúdo:

env
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key
AWS_BUCKET_NAME=your_bucket_name
PDF_FOLDER_PATH=C:/pdf
Ou copie o exemplo:

```bash
cp .env.example .env
▶️ Execução
No terminal ou clicando duas vezes no main.py:

```bash
python main.py

📂 Estrutura de Diretórios
bash
Copiar
Editar
notawatch/
├── main.py
├── .env
├── .env.example
├── data/
│   └── count.json
├── logs/
│   ├── audit_log.txt
│   └── sent_files.txt
💡 Sugestões de Uso
Integre com um sistema de emissão de notas para envio automático.

Utilize em estações de atendimento ou servidores para monitoramento 24/7.

Pode ser usado em conjunto com agendamentos e scripts de backup.

🧪 Teste de Conexão AWS
Dentro da aplicação há um botão "Testar Conexão AWS" para validar suas credenciais com segurança.

📌 Requisitos
Python 3.7+

Bibliotecas: boto3, tkinter, python-dotenv

🛡️ Segurança
Nunca compartilhe sua chave .env com as chaves reais da AWS. Use sempre o .env.example ao distribuir o projeto.

👨‍💻 Autor
Desenvolvido por Anderson Mendes 🧠
📍 Fortaleza - CE | 💼 LinkedIn
