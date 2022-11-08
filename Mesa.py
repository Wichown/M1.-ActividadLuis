import mesa

from mesa.visualization.UserParam import UserSettableParameter

import random
# Agente Tierra
class Tierra(mesa.Agent): 
    
    def __init__(self, unique_id, model): 
        super().__init__(unique_id, model)  
        self.cantidad = 1      
    
    def step(self):  
        contador = 0   
        contador = contador + 1

class Aspiradora(mesa.Agent):
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.celdasLimpiadas = 0
        self.bool = True
        self.movimiento = 0
    
    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )

        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)
    
    def step(self):
        
        self.move() 

        self.movimiento = self.movimiento + 1

        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        
        if len(cellmates) > 1:

            for i in cellmates:
                
                if type(i) == Tierra and i.cantidad == 1:
                    
                    print("Suciedad detectada, aspirando")
                    
                    i.cantidad = i.cantidad - 1

                    self.celdasLimpiadas = self.celdasLimpiadas + 1

class ModeloCuarto(mesa.Model): 

    def __init__(self, N, ancho, alto, celdasSucias, tiempo):

        self.num_agents = N
        self.grid = mesa.space.MultiGrid(ancho, alto, False)        
        self.schedule = mesa.time.RandomActivation(self)    
        self.tiempo = tiempo
        self.running = True
        self.status = True
        self.anchoGrid = ancho
        self.altoGrid = alto
        self.suciedad = celdasSucias
        
        for i in range(self.num_agents):
            agenteAspiradora = Aspiradora(i, self)
            self.schedule.add(agenteAspiradora)
            self.grid.place_agent(agenteAspiradora, (1, 1))

        for i in range(0,celdasSucias):            
            agenteTierra = Tierra(N+i, self)
            self.schedule.add(agenteTierra)
            x = random.randint(0, ancho-1)
            y = random.randint(0, alto-1)
            self.grid.place_agent(agenteTierra,(x,y))

        self.datacollector = mesa.DataCollector(
            {
                "Celdas sucias": ModeloCuarto.celdasSucias,
                "Movimientos generales de los agentes": ModeloCuarto.movimientosAgentes,
                "CeldasLimpiadas":ModeloCuarto.celdasLimpias,
                "PorcentajeLimpieza": ModeloCuarto.porcentajeLimpieza,
                "PorcentajeSuciedad": ModeloCuarto.porcentajeSuciedad,
            }
        )
        
    def step(self):
        
        self.datacollector.collect(self)
        self.schedule.step()
        if self.status == False:
            self.running = False

        if ModeloCuarto.celdasSucias(self) == 0:
            self.status = False
            print("Celdas limpias")

        elif self.tiempo == self.schedule.steps and ModeloCuarto.celdasSucias(self) > 0:
            print("No se termino de limpiar")

            for i in self.schedule.agents:
                if type(i) == Aspiradora:
                    i.bool = False
            self.running = False

    @staticmethod
    def celdasSucias(model):       
        return sum([1 for agent in model.schedule.agents if type(agent) == Tierra and agent.cantidad == 1])

    @staticmethod
    def movimientosAgentes(model):  
        acumulado = 0  
        for agent in model.schedule.agents:
            if type(agent) == Aspiradora:
                acumulado = acumulado + agent.movimiento
        
        return acumulado

    @staticmethod
    def celdasLimpias(model):
        
        acumuladoLimpiado = 0
        
        for agent in model.schedule.agents:
        
            if type(agent) == Aspiradora:
        
                acumuladoLimpiado = acumuladoLimpiado + agent.celdasLimpiadas

        return acumuladoLimpiado

    @staticmethod
    def porcentajeLimpieza(model):
        cuadriculasGrid = model.anchoGrid * model.altoGrid  
        celdasSucias = sum([1 for agent in model.schedule.agents if 
        type(agent) == Tierra and agent.cantidad == 1])

        return ((abs(cuadriculasGrid-celdasSucias)) * 100) / cuadriculasGrid

     @staticmethod
    def porcentajeSuciedad(model):

        cuadriculasGrid = model.anchoGrid * model.altoGrid
        
        celdasSucias = sum([1 for agent in model.schedule.agents if 
        
        type(agent) == Tierra and agent.cantidad == 1])

        return ((abs(celdasSucias)) * 100) / cuadriculasGrid

import pandas as pd

PIXELES_GRID = 650

altura = random.randint(20,50)

ancho = random.randint(26,50)

params = {"N": random.randint(10, 50), "ancho": 10, "alto": 15, "celdasSucias": random.randint(10, 50), "tiempo":random.randint(50,200)}

results = mesa.batch_run(

    ModeloCuarto,

    parameters=params,

    iterations=15,

    max_steps=params["tiempo"],

    number_processes=1,

    data_collection_period=1,

    display_progress=True,

)

results_df = pd.DataFrame(results)

print(results_df.keys())

results_filtered = results_df[(results_df.celdasSucias <= 50) & (results_df.tiempo <= 150)]

print(

    results_filtered.to_string(
        index=False, columns=["iteration", "celdasSucias", "tiempo", "N", "ancho", "alto", "Movimientos generales de los agentes", "CeldasLimpiadas", "PorcentajeLimpieza", "PorcentajeSuciedad"], max_rows=900
    )

)


simulation_params = {

    "N": UserSettableParameter(
        "slider",
        "Number of Agents",
        50,
        1,
        200,
        1,
        description = "Elige cuantos agentes estan en la simulacion",   
    ),

    "celdasSucias": UserSettableParameter(
        "slider",
        "Celdas Sucias",
        50,
        1,
        200,
        1,
        description = "Elige la cantidad de celdas sucias",   
    ),


    "tiempo": UserSettableParameter(
        "slider",
        "Tiempo limite",
        50,
        1,
        2000,
        1,
        description = "Elige el tiempo lmite de la simulacion (Steps del programa)",   
    ),

    "ancho": ancho,

    "alto": altura,
}

def agent_portrayal(agent):

    portrayal = {

        "Shape": "circle",

        "Filled": "true",

        "Layer": "Aspiradora",

        "Color": "blue",

        "r": 0.5,

    }

    if type(agent) == Tierra:

        portrayal["Color"] = "red"

        portrayal["Layer"] = "Tierra"

    if type(agent) == Tierra and agent.cantidad == 0:

        portrayal["Color"] = "green"

        portrayal["Layer"] = "Tierra limpiada"


    if type(agent) == Aspiradora and agent.bool == False:

        portrayal["Color"] = "black"

        portrayal["Filled"] = True

    return portrayal

celdasSucias = mesa.visualization.ChartModule(

    [
        {"Label": "Celdas sucias","Color": "Purple"},
    ],

data_collector_name='datacollector')

movimientosGeneralesAgentes = mesa.visualization.ChartModule(

    [

        {"Label": "Movimientos generales de los agentes","Color": "Red"},

    ],

data_collector_name='datacollector')

celdasLimpiadas = mesa.visualization.ChartModule(
 
    [
 
        {"Label": "CeldasLimpiadas","Color": "Green"},
 
    ],

data_collector_name='datacollector')

porcentajes = mesa.visualization.ChartModule(

    [

        {"Label": "PorcentajeLimpieza","Color": "blue"},

        {"Label": "PorcentajeSuciedad","Color": "grey"},

    ],
data_collector_name='datacollector')

grid = mesa.visualization.CanvasGrid(agent_portrayal, ancho, altura, PIXELES_GRID, PIXELES_GRID)

server = mesa.visualization.ModularServer(
    ModeloCuarto, [grid, celdasSucias, movimientosGeneralesAgentes, celdasLimpiadas, porcentajes], "Aspiradora", simulation_params
)

server.port = 8524

server.launch()
