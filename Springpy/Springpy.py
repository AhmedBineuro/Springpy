from App import App
from typing import Tuple, List
from typing_extensions import Annotated, TypeAlias
import pygame
import pygame_gui  # New GUI library I guess!
import random
# Creates a type of a list with 2 entries
Vector2D: TypeAlias = Annotated[List[float], 2]
AppSize = [600, 600]


class Springpy:
    anchorSize = 10

    def __init__(self):
        # The position of each anchor
        self.anchors: List[Vector2D] = []
        # The velocities of each anchor
        self.velocities: List[Vector2D] = []
        # The accelerations of each anchor
        self.accelerations: List[Vector2D] = []
        # The force applied to each anchor
        self.forces: List[Vector2D] = []
        # Whether each point is affected by gravity and other forces
        self.locked: List[bool] = []
        # Gravity acceleration
        # Translated from meter/second to centimeters per millisecond
        self.gravityAcceleration = 9.8

    def add_anchor(self, position: Vector2D = [100, 100], initial_velocity: Vector2D = [0, 0], locked: bool = False):
        # We add an entry to each point to have matching indices in each list
        self.anchors.append(position)
        self.velocities.append(initial_velocity)
        self.accelerations.append([0, 0])
        self.forces.append([0, 0])
        self.locked.append(locked)

    def remove_anchor(self, index: int):
        self.anchors.pop(index)
        self.velocities.pop(index)
        self.accelerations.pop(index)
        self.forces.pop(index)
        self.locked.pop(index)

    def update(self, deltaTime: float = 0.016):
        for i in range(len(self.anchors)):
            # If the anchor is not locked apply updates
            if self.locked[i]:
                continue
            self.accelerations[i][0] = 0
            self.accelerations[i][1] = 0
            self.forces[i][0] = 0
            self.forces[i][1] = 0

            # Gravity step
            self.accelerations[i][1] += self.gravityAcceleration

            # Getting velocity
            self.velocities[i][0] += self.accelerations[i][0]
            self.velocities[i][1] += self.accelerations[i][1]

            # Collision with window frame
            if (((self.anchors[i][1] >= AppSize[1]-self.anchorSize) and (self.velocities[i][1] > 0)) or ((self.anchors[i][1] <= self.anchorSize) and (self.velocities[i][1] < 0))):
                self.velocities[i][1] = self.velocities[i][1]*-0.8
                self.velocities[i][0] = self.velocities[i][0]*0.9
            if (((self.anchors[i][0] >= AppSize[0]-self.anchorSize) and (self.velocities[i][0] > 0)) or ((self.anchors[i][0] <= self.anchorSize) and (self.velocities[i][0] < 0))):
                self.velocities[i][0] = self.velocities[i][0]*-0.8
            # Moving anchor
            self.anchors[i][0] += self.velocities[i][0]*deltaTime
            self.anchors[i][1] += self.velocities[i][1]*deltaTime

    def draw(self, surface):

        for i in range(len(self.anchors)):
            pygame.draw.circle(
                surface, "red", self.anchors[i], self.anchorSize)


if __name__ == "__main__":
    app = App(name="Sproingy", dimensions=AppSize, maxFPS=280)
    app.init()

    spring = Springpy()

    # GUI setup
    guiManager = pygame_gui.UIManager(AppSize)
    elementList = []

    def GuiSetup():
        global guiManager
        summonButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
            (40, 40), (200, 90)), text="Summon anchor", manager=guiManager)
        elementList.append(summonButton)

    def GuiEvent(event: pygame.Event):
        global guiManager
        if (event.type == pygame_gui.UI_BUTTON_PRESSED):
            if (event.ui_element == elementList[0]):
                spring.add_anchor(position=[random.randInt(10, AppSize-10), random.randInt(10, AppSize-10)],
                                  initial_velocity=[random.randInt(100, 1000), random.randInt(100, 1000)], locked=False)
        guiManager.process_events(event)
    app.appendToInvokeQueue(GuiSetup)
    app.appendToEventQueue(GuiEvent)

    app.appendToEventQueue(guiManager.process_events)
    app.appendToTaskQueue(spring.update)
    app.appendToTaskQueue(guiManager.update)

    app.appendToDrawQueue(guiManager.draw_ui)
    app.appendToDrawQueue(spring.draw)
    spring.add_anchor(position=[200, 200],
                      initial_velocity=[200, 0], locked=False)
    app.execute()
