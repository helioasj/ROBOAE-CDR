from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import re
import shutil
import pymssql
import datetime
import os

# Atribuição de Variaveis
email = "emial@gmail.com"
senha = "senha2019"

destinatario = "emaildestino@gmail.com"
assunto = "E-mail enviado pelo robo"
mensagem = "Primeiro e-mail enviado pelo nosso robô."

driver = webdriver.Chrome('C:/.../webdriverChrome/chromedriver.exe')

print("Iniciando nosso robô...\n")
print("Acessando o Gmail...")
driver.get("https://gmail.com.br/")
driver.maximize_window()

# LOGIN
print("Realizando login...")
login = driver.find_element_by_id("identifierId")
login.clear()
login.send_keys(email)
login.send_keys(Keys.RETURN)
time.sleep(2)

password = driver.find_element_by_name("password")
password.clear()
password.send_keys(senha)
password.send_keys(Keys.RETURN)
time.sleep(6)
print("Login realizado...")

print("Localizando email...")
# list_of_elements = driver.find_element_by_class_name('yW')
list_of_elements = driver.find_elements_by_css_selector(".zA.zE.byw")
# print(list_of_elements)
texto = ''
for i in list_of_elements:
    txt = i.text
    print('O i.text:***', txt, '***')
    i.click()
    nomePdf = re.search(r"(Anexo:)(\n)([\d\D]*.pdf)", txt).group(3)
    print('O nome do arquivo anexo é:', '|||', nomePdf, '|||')

    print("Email selecionado. Abrindo...")
    time.sleep(6)
    corpo_do_email = driver.find_elements_by_css_selector('.a3s.aXjCH ')

    for body in corpo_do_email:
        print('Localizando Corpo do email...')
        texto += body.text

        con = pymssql.connect(host='localhost',
                              user='user',
                              password='password',
                              database='databasename')
        cursor = con.cursor()

        #Extrai o nome do Cliente e o CNPJ do corpo do email
        cliente = re.search(r"(Cliente:([\d\D]*}))", texto).group(2)
        cnpjCli = re.search(r"\d{2}.\d{3}.\d{3}\/\d{4}-\d{2}", texto).group(0)
        cnpj = dict(cnpj=cnpjCli)

        #Consulta nome e o diretorio da Empresa no banco de dados
        cursor.execute('SELECT ****  from **** where cnpj = %(cnpj)s', cnpj)
        result = cursor.fetchone()
        suporteQualitor = False
        diretorioFisicoExiste = True
        cadastroDiretorioExiste = True
        empresaDiretorio = ''

        if result:
            empresaNome = result[0]
            empresaDiretorio = result[1]
            cadastroDiretorioExiste = True
        else:
            suporteQualitor = True

        if os.path.isdir(empresaDiretorio):
            diretorioFisicoExiste = True
            print('Diretório Empresa Existe!!!')
        else:
            diretorioFisicoExiste = False
            suporteQualitor = True
            print('Diretório Empresa NÃO Existe!!!')

        #Extrai da data de Vencimento, Situação e Tipo de Certidão do corpo do email
        dataVenc = re.search(r"(Vencimento: )(\d{2}\/\d{2}\/\d{4})", texto).group(2)
        situacao = re.search(r"Situação:.*", texto).group(0).replace('Situação: ', '')
        tipoCertidao = re.search(r"Tipo de Certidão:.*", texto).group(0).replace('Tipo de Certidão: ', '')

        #Atualiza tabela CNDS, com a data de vencimento da CND
        dados = dict(dt_vencto=datetime.datetime.strptime(dataVenc, '%d/%m/%Y').date(),cnpj=cnpjCli)
        print(type(dados))
        print(dados)
        cursor.execute('UPDATE ******* dt_vencto=%(dt_vencto)s where cnpj = %(cnpj)s', dados)
        con.commit()

        # Consulta Banco do Qualitor para validar existencia de Empresa e Categorias
        sql = 'SELECT *****  FROM ******'
        cursor.execute(sql)
        rs = cursor.fetchall()
        print(rs)
        lista = []
        for i in range(len(rs)):
            # print(rs[i])
            lista.append(rs[i][0])

        #Verifica se a situação existe como categoria
        suporteQualitor = False
        if situacao in lista:
            print('Categoria 2 Existente("Situação")')
        else:
            print('Categoria 2 Inexistente("Situação")')
            suporteQualitor = True
        #Verifica se o Tipo de Certidão existe como categoria
        if tipoCertidao in lista:
            print('Categoria 3 Existente("Tipo de Certidão")')
        else:
            print('Categoria 3 Inexistente("Tipo de Certidão")')
            suporteQualitor = True

        if suporteQualitor == False and cadastroDiretorioExiste==True and diretorioFisicoExiste==True:
            tagcategoria1 = '<CATEGORIA 1>' + 'CND - ROBO' + '</CATEGORIA 1>'
            tagcategoria2 = '<CATEGORIA 2>' + situacao + '</CATEGORIA 2>'
            tagcategoria3 = '<CATEGORIA 3>' + tipoCertidao + '</CATEGORIA 3>'
            tagempresa = '<CLIENTE>' + empresaNome + '</CLIENTE>'
            tagcontato = '<CONTATO>Administrador</CONTATO>'
            tagdescricao = '<DESCRICAO>' + '' +'</DESCRICAO>'

        elif suporteQualitor == True and cadastroDiretorioExiste==False and diretorioFisicoExiste==True:
            tagcategoria1 = '<CATEGORIA 1>' + 'CND - Suporte' + '</CATEGORIA 1>'
            tagcategoria2 = '<CATEGORIA 2>' + 'Cadastro/Manutenção' + '</CATEGORIA 2>'
            tagcategoria3 = '<CATEGORIA 3>' + 'Cadastro de Diretório Inexistente(Portal Nexxus)' + '</CATEGORIA 3>'
            tagempresa = '<CLIENTE>' + 'Atmosfera Gestão e Higienização de Texteis S.A.' + '</CLIENTE>'
            tagcontato = '<CONTATO>Administrador</CONTATO>'
            tagdescricao = '<DESCRICAO>' + '\n' + \
                           'CATEGORIA 1:' + 'CND - ROBO' + '\n' + \
                           'CATEGORIA 2:' + situacao + '\n' + \
                           'CATEGORIA 3:' + tipoCertidao + '\n' + \
                           'CNPJ:' + cnpjCli + '\n' + \
                           '</DESCRICAO>'
        elif suporteQualitor == True and cadastroDiretorioExiste==True and diretorioFisicoExiste==False:
            tagcategoria1 = '<CATEGORIA 1>' + 'CND - Suporte' + '</CATEGORIA 1>'
            tagcategoria2 = '<CATEGORIA 2>' + 'Cadastro/Manutenção' + '</CATEGORIA 2>'
            tagcategoria3 = '<CATEGORIA 3>' + 'Diretório Inexistente' + '</CATEGORIA 3>'
            tagempresa = '<CLIENTE>' + 'Atmosfera Gestão e Higienização de Texteis S.A.' + '</CLIENTE>'
            tagcontato = '<CONTATO>Administrador</CONTATO>'
            tagdescricao = '<DESCRICAO>' + '\n' + \
                           'CATEGORIA 1:' + 'CND - ROBO' + '\n' + \
                           'CATEGORIA 2:' + situacao + '\n' + \
                           'CATEGORIA 3:' + tipoCertidao + '\n' + \
                           'CNPJ:' + cnpjCli + '\n' + \
                           'DIRETÓRIO:' + empresaDiretorio + '\n' + \
                           '</DESCRICAO>'
        else:
            tagcategoria1 = '<CATEGORIA 1>' + 'CND - Suporte' + '</CATEGORIA 1>'
            tagcategoria2 = '<CATEGORIA 2>' + 'Cadastro/Manutenção' + '</CATEGORIA 2>'
            tagcategoria3 = '<CATEGORIA 3>' + 'Empresas/Filiais/Categorias Qualitor' + '</CATEGORIA 3>'
            tagempresa    = '<CLIENTE>' + 'Atmosfera Gestão e Higienização de Texteis S.A.' + '</CLIENTE>'
            tagcontato    = '<CONTATO>Administrador</CONTATO>'
            tagdescricao  = '<DESCRICAO>' + '\n' + \
                            'CATEGORIA 1:' + 'CND - ROBO' + '\n' + \
                            'CATEGORIA 2:' + situacao + '\n' + \
                            'CATEGORIA 3:' + tipoCertidao + '\n' + \
                            '</DESCRICAO>'

        print('Clicando no email selecionado...')
        print('O conteudo a ser analisado é:***', texto, '***')
        print('A data de vencimento:', dataVenc)
        print('A Categoria 2 é:', situacao)
        print('A Categoria 3 é:', tipoCertidao)
        print('O CNPJ encontrado é:', cnpjCli)
        print('A Empresa é:', tagempresa)
        print('O Contato é:', tagcontato)

        print('Baixando o pdf...')

        # driver.find_element_by_css_selector("input[name='filePath'][type='file']")
        # baixarCNDPdf = driver.find_elements_by_css_selector('Fazer o download')
        baixarCNDPdf = driver.find_element_by_xpath('//div[@data-tooltip="Fazer o download"]')
        #print(baixarCNDPdf)
        time.sleep(5)
        baixarCNDPdf.click()
        baixarCNDPdf.send_keys(Keys.RETURN)
        baixarCNDPdf.send_keys(Keys.ENTER)
        baixarCNDPdf.click()
        baixarCNDPdf.click()
        baixarCNDPdf.click()
        baixarCNDPdf.click()

        print('Encaminhando...')
        time.sleep(3)
        encaminhar = driver.find_elements_by_css_selector(".ams.bkG")
        for j in encaminhar:
            print('Clicando no botão encaminhar...')
            j.click()
            time.sleep(3)

            inputUrlDestino = driver.find_elements_by_name('to')
            for k in inputUrlDestino:
                print('digitando email destinatário...')
                k.send_keys('email@gmail.com')
                k.send_keys(Keys.RETURN)

                corpoEmail = driver.find_elements_by_css_selector('.Am.aO9.Al.editable.LW-avf.tS-tW')
                for l in corpoEmail:
                    print('digitando corpo do email')

                    l.send_keys('\n')
                    l.send_keys(tagcategoria1 + '\n')
                    l.send_keys(tagcategoria2 + '\n')
                    l.send_keys(tagcategoria3 + '\n')
                    l.send_keys(tagempresa + '\n')
                    l.send_keys(tagcontato + '\n')
                    l.send_keys(tagdescricao + '\n')

                    time.sleep(3)

                    enviar = driver.find_elements_by_css_selector(".T-I.J-J5-Ji.aoO.v7.T-I-atl.L3")
                    for l in enviar:
                        print('Clicando no botão ENVIAR...')
                        l.send_keys(Keys.RETURN)
                        time.sleep(6)
                        driver.close()
                        # time.sleep(10)


                        diretorioDestino = empresaDiretorio



                        if tipoCertidao == 'FGTS' or tipoCertidao == 'Receita Federal' or tipoCertidao == 'Tributos Não Inscritos SP':
                            print('1)NOME EMPRESA ANTES:', cliente)
                            cliente = re.sub(r'(\{[\d\D]*\})', '', cliente)
                            print('1)NOME EMPRESA DEPOIS:', cliente)
                        elif tipoCertidao == 'Estadual':
                            print('2)NOME EMPRESA ANTES:', cliente)
                            cliente = re.sub(r'{([\d\D]*\/)', '', cliente)
                            print('2)NOME EMPRESA DEPOIS:', cliente)
                        else:
                            print('3)NOME EMPRESA ANTES:', cliente)
                            cliente = re.sub(r'\/', '-', cliente)
                            print('3)NOME EMPRESA DEPOIS:', cliente)

                        # conteudo    = re.search(r"(\{[\d\D]*\})" , empresaNome).group(1)

                        print('Novo diretorio destino:', diretorioDestino)
                        print('Movendo arquivo para diretório')
                        print('Renomeando Arquivo...')
                        origem = 'C:/.../Downloads/' + nomePdf

                        if diretorioFisicoExiste == True:
                            destino = diretorioDestino + '/' + cliente + ' CND ' + tipoCertidao + '.pdf'
                        else:
                            destino = 'C:/...../DIRETORIO INEXISTENTE/'
                        print('Local de Origem:', origem)
                        print('Local Destino:', destino)

                        dest = shutil.move(origem, destino)


                        break
                    break
                break
            break
        break
    break
