# Code of a model with cleaners agents
# Based on rules by Eduardo Mora - A01799440
# Last Modification: 07/11/2025

import mesa

class CleanerAgent(mesa.Agent):
    def __init__(self, model, startPos):
        super().__init__(model)
        self.pos = startPos
        self.moveCount = 0 
    def step(self):
        cleanedThisStep = self.clean()

        if not cleanedThisStep:
            self.move()

    def clean(self):
        cellContents = self.model.grid.get_cell_list_contents([self.pos])
        for obj in cellContents:
            if isinstance(obj, DirtCell) and not obj.isCleaned:
                obj.isCleaned = True
                return True  
        return False 

    def move(self):
        dx, dy = 0, 0
        while dx == 0 and dy == 0:
            dx = self.random.choice([-1, 0, 1])
            dy = self.random.choice([-1, 0, 1])

        newPos = (self.pos[0] + dx, self.pos[1] + dy)

        if not self.model.grid.out_of_bounds(newPos):
            self.model.grid.move_agent(self, newPos)
            self.moveCount += 1



class DirtCell(mesa.Agent):

    def __init__(self, pos, model):
        super().__init__(model)
        self.pos = pos
        self.isCleaned = False


class RoomModel(mesa.Model):

    def __init__(self, width, height, numAgents, dirtyPercentage, maxTime):
        super().__init__()

        self.width = width
        self.height = height
        self.numAgents = numAgents
        self.maxTime = maxTime

        self.grid = mesa.space.MultiGrid(width, height, torus=False)

        totalCells = width * height
        self.totalDirtyCells = int(totalCells * dirtyPercentage)

        allCoords = [(x, y) for x in range(width) for y in range(height)]
        self.random.shuffle(allCoords)
        dirtyCoords = allCoords[:self.totalDirtyCells]

        for pos in dirtyCoords:
            dirt = DirtCell(pos, self)
            self.grid.place_agent(dirt, pos)

        startPos = (1, 1)

        if self.grid.out_of_bounds(startPos):
            startPos = (0, 0)

        for i in range(self.numAgents):
            agent = CleanerAgent(self, startPos)
            self.grid.place_agent(agent, startPos)

        self.datacollector = mesa.DataCollector(
            {
                "PercentClean": lambda m: m.getPercentClean(),
                "TotalMoves": lambda m: m.getTotalMoves()
            }
        )

        self.running = True

    def getCleanedCellCount(self):
        return sum([1 for agent in self.agents_by_type[DirtCell] if agent.isCleaned])

    def getPercentClean(self):
        if self.totalDirtyCells == 0:
            return 1.0
        return self.getCleanedCellCount() / self.totalDirtyCells

    def getTotalMoves(self):
        return sum([agent.moveCount for agent in self.agents_by_type[CleanerAgent]])

    def step(self):
        self.datacollector.collect(self)

        self.agents_by_type[CleanerAgent].shuffle_do("step")

        if self.steps >= self.maxTime:
            self.running = False
        elif self.getCleanedCellCount() == self.totalDirtyCells:
            self.running = False


if __name__ == "__main__":

    WIDTH = 20
    HEIGHT = 20
    NUM_AGENTS = 10
    DIRTY_PERCENTAGE = 0.6
    MAX_TIME = 200
    print(f"Simulating: {WIDTH}x{HEIGHT}, {NUM_AGENTS} agents, {DIRTY_PERCENTAGE*100}% dirt, {MAX_TIME} max steps.")
    model = RoomModel(WIDTH, HEIGHT, NUM_AGENTS, DIRTY_PERCENTAGE, MAX_TIME)
    while model.running:
        model.step()
    print("\n--- Simulation Finished ---")
    finalData = model.datacollector.get_model_vars_dataframe()
    timeRequired = model.steps
    print(f"Time required: {timeRequired} steps")
    finalPercentClean = finalData["PercentClean"].iloc[-1]
    print(f"Percentage of clean cells: {finalPercentClean * 100:.2f}%")
    finalTotalMoves = finalData["TotalMoves"].iloc[-1]
    print(f"Total number of moves (all agents): {finalTotalMoves}")