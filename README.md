## Instalar as dependências do projeto

## LINUX

### instalar o pyenv
https://github.com/pyenv/pyenv#installation

### dependências para compilar e instalar o Python
`sudo apt-get update; sudo apt-get install make gcc build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev`

### instalar a versão 3.12.1 do Python
`pyenv install 3.12.1`

### configurar versão 3.12.1 no terminal que está aberto
`pyenv shell 3.12.1`

### instalar depêdencias do projeto
`pip install --upgrade pip setuptools wheel poetry`

### criar o ambiente virtual através poetry
`poetry env use 3.12.1`

### ativar o ambiente virtual através poetry
`poetry shell`

### rodar o comando pra instalar as depedencias da aplicação
`make install-deps`