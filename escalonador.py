import time

class EstadoProcesso:
    READY = "Ready"
    RUNNING = "Running"
    BLOCKED = "Blocked"
    EXIT = "Exit"

class Processo:
    def __init__(self, nome, cpu_burst, duracao_io, tempo_total_cpu, ordem, prioridade):
        self.nome = nome
        self.cpu_burst = cpu_burst
        self.duracao_io = duracao_io
        self.tempo_total_cpu = tempo_total_cpu
        self.ordem = ordem
        self.prioridade = prioridade
        self.creditos = prioridade
        self.estado = EstadoProcesso.READY
        self.tempo_inicio = 0
        self.tempo_conclusao = 0
        self.tempo_bloqueado_restante = 0
        self.tempo_cpu_restante = tempo_total_cpu
        self.tempo_execucao = 0
    
    def __str__(self) -> str:
        return ", ".join([self.nome, self.estado])

class Escalonador:
    def __init__(self, processos):
        self.processos = processos
        self.tempo_atual = 0
        self.processo_executando = None
        self.proximo_processo = None
        self.ultimo_processo = None

    def executar(self):
        while not self.todos_processos_concluidos():
            self.imprimir_linha_do_tempo()
            self.atualizar_estados_processos()

            if all(p.creditos == 0 or p.estado == EstadoProcesso.BLOCKED for p in self.processos):
                self.redistribuir_creditos()
                if not self.processo_executando is None:
                    self.processo_executando.estado = EstadoProcesso.READY
            
            #if self.processo_executando is None or self.processo_executando.creditos == 0 or self.processo_executando.estado == EstadoProcesso.BLOCKED:
            #    self.proximo_processo = self.obter_proximo_processo()

            if (self.processo_executando is None) or (self.processo_executando.creditos == 0 or self.processo_executando.estado == EstadoProcesso.BLOCKED or self.processo_executando.estado == EstadoProcesso.READY): 
                self.proximo_processo = self.obter_proximo_processo(self.processo_executando)
                
            if self.proximo_processo:
                self.executar_processo(self.proximo_processo)
                
            self.tempo_atual += 1

    def todos_processos_concluidos(self):
        return all(p.estado == EstadoProcesso.EXIT for p in self.processos)

    def obter_proximo_processo(self, atual):
        
        proximo_processo = None

        # responsavel por seguir a ordem de execução a partir do atual 
        if not atual is None:
            indice_acessado = self.processos.index(atual)
            # se o processo atual for o último da lista, define a ordem original de processos 
            if indice_acessado + 1  >= len(self.processos):
                ordem_processos = self.processos
            else:
                # organiza a lista de processos para começar a partir do próximo processo após o atual
                ordem_processos = self.processos[indice_acessado+1:] + self.processos[:indice_acessado+1]
        else:
            ordem_processos = self.processos
        
        # ATENÇÃO!
        for processo in ordem_processos:
            if not processo.estado in [EstadoProcesso.BLOCKED, EstadoProcesso.EXIT]:
                if proximo_processo is None or (processo.creditos > proximo_processo.creditos and processo != self.ultimo_processo):
                    proximo_processo = processo
                #elif (processo.creditos == proximo_processo.creditos and processo.ordem < proximo_processo.ordem and processo != self.ultimo_processo):
                #    proximo_processo = processo
        self.ultimo_processo = self.processo_executando
        return proximo_processo

    def executar_processo(self, processo):
        if self.processo_executando != processo:
            if self.processo_executando:
                 # se há um processo sendo executado, muda seu estado para "READY"
                self.processo_executando.estado = EstadoProcesso.READY
            self.processo_executando = processo
            # atualiza o processo atual para o estado "RUNNING"
            processo.estado = EstadoProcesso.RUNNING
            if processo.tempo_inicio == 0:
                # se o processo está sendo executado pela primeira vez, define o tempo de início
                processo.tempo_inicio = self.tempo_atual

        # decrementa e inclementa os tempos e creditos
        processo.tempo_cpu_restante -= 1
        processo.creditos -= 1
        processo.tempo_execucao += 1

        if processo.tempo_cpu_restante == 0:
            # adiciona uma mensagem de quando cada processo acaba, pois eles não vão continuar aparecendo 
            print(f"Processo {processo.nome} EXIT no tempo {self.tempo_atual + 2} ms. Créditos no tempo anterior: {processo.creditos}\n") 
            processo.estado = EstadoProcesso.EXIT
            processo.tempo_conclusao = self.tempo_atual
            processo.creditos = 0
            self.processo_executando = None
        # verifica se o processo completou seu ciclo de CPU (CPU burst)
        # muda o estado do processo para "BLOCKED" (bloqueado para I/O)
        elif processo.tempo_execucao == processo.cpu_burst:
            processo.estado = EstadoProcesso.BLOCKED
            processo.tempo_bloqueado_restante = processo.duracao_io
            self.processo_executando = None


    def redistribuir_creditos(self):
        for processo in self.processos:
            if processo.estado != EstadoProcesso.EXIT:
                processo.creditos = (processo.creditos//2) + processo.prioridade
        self.ultimo_processo = self.processo_executando
        #self.processo_executando = None

    def atualizar_estados_processos(self):
        for processo in self.processos:
            if processo.estado == EstadoProcesso.BLOCKED:
                processo.tempo_bloqueado_restante -= 1
                if processo.tempo_bloqueado_restante == 0:
                    processo.estado = EstadoProcesso.READY
                    processo.tempo_execucao = 0
            if processo.estado == EstadoProcesso.RUNNING and processo.creditos == 0: # adicionado após o Processo A continuar como running no tempo 12 ms
                processo.estado = EstadoProcesso.READY

    def imprimir_linha_do_tempo(self):
        print(f"Tempo: {self.tempo_atual} ms")
        for processo in self.processos:
            if processo.tempo_inicio <= self.tempo_atual and (processo.tempo_conclusao == 0 or processo.tempo_conclusao > self.tempo_atual):
                print(f"{processo.nome} ({processo.estado} - crédito = {processo.creditos})")
        print()

# exemplo de escalonamento disponivel 
processos = [
    Processo("A", 2, 5, 6, 1, 3),
    Processo("B", 3, 10, 6, 2, 3),
    Processo("C", 0, 0, 14, 3, 3),
    Processo("D", 0, 0, 10, 4, 3)
]

escalonador = Escalonador(processos)
escalonador.executar()