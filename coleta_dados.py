import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Configuração do Banco de Dados
db = create_engine("sqlite:///cinema.db")
Base = declarative_base()

class Filme(Base):
    __tablename__ = 'filmes'
    id = Column(Integer, primary_key=True)
    titulo = Column(String(255), nullable=False)

class Horario(Base):
    __tablename__ = 'horarios'
    id = Column(Integer, primary_key=True)
    filme_id = Column(Integer, ForeignKey('filmes.id'))
    horario = Column(String(255), nullable=False)

# Cria as tabelas se não existirem
Base.metadata.create_all(db)
Session = sessionmaker(bind=db)
sessao = Session()

# 2. Requisição e Parsing
url_cinema = 'https://cinema.maringa.com/cinema-avenida-center'

resposta = requests.get(url_cinema)
pagina_html = BeautifulSoup(resposta.text, 'html.parser')

# 3. Extração
blocos_filmes = pagina_html.find_all('div', class_='info-cine-horario')

print(f"Encontrados {len(blocos_filmes)} blocos de filmes. Iniciando importação...\n")

for bloco in blocos_filmes:
    titulo_tag = bloco.find('h1', class_='text-center titulo-filme mb-0 h1')
    
    if titulo_tag:
        titulo_texto = titulo_tag.text.strip()
        
        # Salva o filme
        novo_filme = Filme(titulo=titulo_texto)
        sessao.add(novo_filme)
        sessao.flush() # Gera o ID para o relacionamento

        # Busca os horários
        horarios_tags = bloco.find_all('div', class_='box-horarios badge badge-dark mr-2 mt-2')
        
        lista_horarios_print = []
        for h_tag in horarios_tags:
            horario_texto = h_tag.text.strip()
            novo_horario = Horario(filme_id=novo_filme.id, horario=horario_texto)
            sessao.add(novo_horario)
            lista_horarios_print.append(horario_texto)

        print(f" Salvo: {titulo_texto} | Horários: {', '.join(lista_horarios_print)}")


sessao.commit()
sessao.close()
print("\n--- Todos os dados foram salvos no cinema.db ---")