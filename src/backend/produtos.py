class Item:
    def __init__(self, id_item, nome, valor, quantia, local_fabricacao="Mari"):
        self.id = id_item
        self.nome = nome
        self.valor = valor
        self.quantia = quantia
        self.local_fabricacao = local_fabricacao

class Salgado(Item):
    def __init__(self, id_item, nome, sabor, valor, quantia, local_fabricacao="Mari"):
        super().__init__(id_item, nome, valor, quantia, local_fabricacao)
        self.sabor = sabor
        self.categoria = "Salgado"

class Bebida(Item):
    def __init__(self, id_item, nome, sabor, valor, quantia,local_fabricacao="Mari"):
        super().__init__(id_item, nome, valor, quantia, local_fabricacao)
        self.sabor = sabor
        self.categoria = "Bebida"

