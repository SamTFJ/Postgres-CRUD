class Item:
    def __init__(self, id_item, nome, valor, quantia):
        self.id = id_item
        self.nome = nome
        self.valor = valor
        self.quantia = quantia

class Salgado(Item):
    def __init__(self, id_item, nome, sabor, valor, quantia):
        super().__init__(id_item, nome, valor, quantia)
        self.sabor = sabor
        self.categoria = "Salgado"

class Bebida(Item):
    def __init__(self, id_item, nome, sabor, valor, quantia):
        super().__init__(id_item, nome, valor, quantia)
        self.sabor = sabor
        self.categoria = "Bebida"

