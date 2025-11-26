-- Criação do banco de dados (caso não exista)
CREATE DATABASE IF NOT EXISTS controle_gastos;
USE controle_gastos;

-- Garante que o usuário tenha as permissões corretas
GRANT ALL PRIVILEGES ON controle_gastos.* TO 'app_user'@'%';
FLUSH PRIVILEGES;
