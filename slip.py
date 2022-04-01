class CamadaEnlace:
    ignore_checksum = False

    def __init__(self, linhas_seriais):
        """
        Inicia uma camada de enlace com um ou mais enlaces, cada um conectado
        a uma linha serial distinta. O argumento linhas_seriais é um dicionário
        no formato {ip_outra_ponta: linha_serial}. O ip_outra_ponta é o IP do
        host ou roteador que se encontra na outra ponta do enlace, escrito como
        uma string no formato 'x.y.z.w'. A linha_serial é um objeto da classe
        PTY (vide camadafisica.py) ou de outra classe que implemente os métodos
        registrar_recebedor e enviar.
        """
        self.enlaces = {}
        self.callback = None
        # Constrói um Enlace para cada linha serial
        for ip_outra_ponta, linha_serial in linhas_seriais.items():
            enlace = Enlace(linha_serial)
            self.enlaces[ip_outra_ponta] = enlace
            enlace.registrar_recebedor(self._callback)

    def registrar_recebedor(self, callback):
        """
        Registra uma função para ser chamada quando dados vierem da camada de enlace
        """
        self.callback = callback

    def enviar(self, datagrama, next_hop):
        """
        Envia datagrama para next_hop, onde next_hop é um endereço IPv4
        fornecido como string (no formato x.y.z.w). A camada de enlace se
        responsabilizará por encontrar em qual enlace se encontra o next_hop.
        """
        # Encontra o Enlace capaz de alcançar next_hop e envia por ele
        self.enlaces[next_hop].enviar(datagrama)

    def _callback(self, datagrama):
        if self.callback:
            self.callback(datagrama)


class Enlace:
    def __init__(self, linha_serial):
        self.linha_serial = linha_serial
        self.linha_serial.registrar_recebedor(self.__raw_recv)
        self.recebido = bytearray(b'')
        self.aux = bytearray(b'')

    def registrar_recebedor(self, callback):
        self.callback = callback

    def enviar(self, datagrama):
        # TODO: Preencha aqui com o código para enviar o datagrama pela linha
        # serial, fazendo corretamente a delimitação de quadros e o escape de
        # sequências especiais, de acordo com o protocolo CamadaEnlace (RFC 1055).

       a = bytearray(b'\xC0')
       c = bytearray(b'\xDB')
       d = bytearray(b'\xDC')
       e = bytearray(b'\xDD')

       for i in range(len(datagrama)):
        if bytes(datagrama[i:i+1]) == b'\xC0':
            a.append(c[0])
            a.append(d[0])
        elif bytes(datagrama[i:i+1]) == b'\xDB':
            a.append(c[0])
            a.append(e[0])
        else:
            a.append(datagrama[i])

       a.append(a[0])

       self.linha_serial.enviar(bytes(a))
       
    def __raw_recv(self, dados):
        # TODO: Preencha aqui com o código para receber dados da linha serial.
        # Trate corretamente as sequências de escape. Quando ler um quadro
        # completo, repasse o datagrama contido nesse quadro para a camada
        # superior chamando self.callback. Cuidado pois o argumento dados pode
        # vir quebrado de várias formas diferentes - por exemplo, podem vir
        # apenas pedaços de um quadro, ou um pedaço de quadro seguido de um
        # pedaço de outro, ou vários quadros de uma vez só.
             
        # print('len(dados):', len(dados))
         #print('dados:', bytes(dados))   
         for i in range(len(dados)):
            #print('dados:', bytes(dados[i:i+1]))
            #print('aux:', bytes(self.aux))
            #print('recebido:', bytes(self.recebido))
            if (bytes(dados[i:i+1]) != b'\xC0') & (bytes(dados[i:i+1]) != b'\xDC') & (bytes(dados[i:i+1]) != b'\xDD') & (bytes(dados[i:i+1]) != b'\xDB'):
                #print('bytes1:', bytes(dados[i:i+1]))
                self.recebido += dados[i:i+1]
                #print('recebido5:', bytes(self.recebido[i-1:i]))
                            
            elif (bytes(dados[i:i+1]) == b'\xDB'):
                
                if (bytes(dados[i+1:i+2]) == b'\xDC'):
                    self.recebido += bytearray(b'\xC0')
                #elif (bytes(dados[i+1:i+2]) == b'\xDD'):
                 #   self.recebido += dados[i:i+1]
                else:
                    self.aux = bytearray(b'\xDB')
                    
            elif (bytes(dados[i:i+1]) == b'\xDD') & (self.aux == b'\xDB'):       
                #print('aqui')
                self.recebido += self.aux
                self.aux = bytearray(b'')
            
            elif (bytes(dados[i:i+1]) == b'\xDC') & (self.aux == b'\xDB'):
                self.recebido += bytearray(b'\xC0')
           
           # Enviar Recebido
            elif (bytes(dados[i:i+1]) == b'\xC0') & (self.recebido != bytearray(b'')):
                print('recebido5:', self.recebido)
                self.callback(bytes(self.recebido))
                self.recebido = bytearray(b'')
                
            elif ((i+1) == len(dados)) & (self.recebido != bytearray(b'')) & (self.recebido != b'\xC0'):
                self.callback(bytes(self.recebido))
                print('recebido1:', self.recebido)
                self.recebido = bytearray(b'')
                
           
                

            
            