import string
import random


def invalidValue(value=str(), minSize=int(), maxSize=int(), numberOnNick=False):
    if len(value) < minSize or len(value) > maxSize:
        return True

    if numberOnNick:
        if any(char.isdigit() for char in value):
            return True
        if any(char in string.punctuation for char in value):
            return True

    return False

def invalidCpf(CPF=str()):
    if len(CPF) != 11:
        return True

    return not CPF.isnumeric()

def limpar_cpf(cpf):
    cpf = cpf.replace(".", "").replace("-", "")
    return cpf

def gerarID():
    key = ""
    for i in range(10):
        value = random.randint(60, 90)
        key += chr(value)
    return key

def sorteio(arr):

    sorteados = []

    count = 0
    while count < len(arr):
        numero = random.randint(1,len(arr))
        if numero in sorteados or numero == arr[count]:
            pass
        else:
            sorteados.append(numero)
            count+=1
    
    for i in range(len(sorteados)):
        sorteados[i] = arr[sorteados[i]-1]
        

    return sorteados

def matrizParray(arr):
    lista = []
    for i in range(len(arr)):
        lista.append(arr[i][0])
    return lista

def processarSorteio(lista):
    value = random.randint(0, 1)
    cases = random.randint(1, len(lista)-1)

    if value == 50:
        lista = lista[-cases:] + lista[:-cases]
    else:
        lista = lista[+cases:] + lista[:+cases]

    return lista
