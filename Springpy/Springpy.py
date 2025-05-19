from App import App
from typing import Tuple, List
from typing_extensions import Annotated, TypeAlias
import pygame
import pygame_gui  # New GUI library I guess!
import random
import math
import numpy
import copy
# Creates a type of a list with 2 entries
Vector2f: TypeAlias = Annotated[List[float], 2]
Vector2i: TypeAlias = Annotated[List[int], 2]
AppSize = [600, 600]
app = App(name="Sproingy", dimensions=AppSize, maxFPS=280)
app.init()
guiManager = pygame_gui.UIManager(AppSize)


# Currently bruteforce the click handeling by iterating over every clickable object
class Spring:
    def __init__(self, anchor1: int = -1, anchor2: int = -2, stiffness: float = 1.0, length: float = 20):
        self.anchor1 = anchor1
        self.anchor2 = anchor2
        self.stiffness = stiffness
        self.length = length


class Springpy:

    # Gravity acceleration
    gravityAcceleration = 9.8
    Pause = False

    def __init__(self):
        # The position of each anchor
        self.anchors: List[Vector2f] = []
        # The sizes of eacj anchor
        self. anchorSizes: List[int] = []
        # The spring anchor pairs (As a pair of indices)
        self.springs: List[Spring] = []
        # The velocities of each anchor
        self.velocities: List[Vector2f] = []
        # The accelerations of each anchor
        self.accelerations: List[Vector2f] = []
        # The force applied to each anchor
        self.forces: List[Vector2f] = []
        # Whether each point is affected by gravity and other forces
        self.locked: List[bool] = []

    # return index of added anchor
    def add_anchor(self, position: Vector2f = [100, 100], size: int = 10, initial_velocity: Vector2f = [0, 0], locked: bool = False) -> int:
        # We add an entry to each point to have matching indices in each list
        self.anchors.append(copy.deepcopy(position))
        self.anchorSizes.append(size)
        self.velocities.append(copy.deepcopy(initial_velocity))
        self.accelerations.append(copy.deepcopy([0, 0]))
        self.forces.append(copy.deepcopy([0, 0]))
        self.locked.append(locked)
        return (len(self.anchors)-1)

    def remove_anchor(self, index: int):
        for s in self.springs:
            if (s.anchor1 == index):
                s.anchor1 = None
            if (s.anchor2 == index):
                s.anchor2 = None
        self.anchors.pop(index)
        self.anchorSizes.pop(index)
        self.velocities.pop(index)
        self.accelerations.pop(index)
        self.forces.pop(index)
        self.locked.pop(index)

    def add_spring(self, anchor1: int = 0, anchor2: int = 0, stiffness: float = 1.0, length: float = 20) -> Spring:
        self.springs.append(
            Spring(anchor1=anchor1, anchor2=anchor2, stiffness=stiffness, length=length))
        return self.springs[len(self.springs)-1]

    def update(self, realTimeStep: float = 0):
        deltaTime: float = 0.1
        if self.Pause:
            return
        for i in range(len(self.forces)):
            self.forces[i] = [0, 0]
            self.accelerations[i] = [0, 0]
        dampening = 0.4
        remove = []
        for spring in self.springs:
            if (spring.anchor1 == None or spring.anchor2 == None):
                remove.append(spring)
                continue
            vec1 = numpy.array(self.anchors[spring.anchor1])
            vec2 = numpy.array(self.anchors[spring.anchor2])
            # The direction vector of the force
            anchorVec = vec2-vec1

            # Current length
            currentLength = numpy.linalg.norm(anchorVec)
            if (currentLength <= 0):
                continue
            # Get each axis' movement factor
            movementFactor = anchorVec/currentLength
            offset = currentLength-spring.length

            distFromOG = movementFactor*offset
            invDistFromOG = -distFromOG
            force1 = (distFromOG*spring.stiffness)+(-dampening *
                                                    numpy.array(self.velocities[spring.anchor1]))
            force2 = (invDistFromOG*spring.stiffness)+(-dampening *
                                                       numpy.array(self.velocities[spring.anchor2]))
            # If not locked add force
            if not self.locked[spring.anchor1]:
                self.forces[spring.anchor1][0] += force1[0]
                self.forces[spring.anchor1][1] += force1[1]

            # If not locked add force
            if not self.locked[spring.anchor2]:
                self.forces[spring.anchor2][0] += force2[0]
                self.forces[spring.anchor2][1] += force2[1]
        for r in remove:
            self.springs.remove(r)
        for i in range(len(self.anchors)):
            # If the anchor is not locked apply updates
            if self.locked[i]:
                continue
            # F=m*g (For gravity)
            self.forces[i][1] += self.anchorSizes[i]*self.gravityAcceleration

            # F/m=a from F=ma, and the the m is the size of the anchor for now
            self.accelerations[i][0] += self.forces[i][0] / self.anchorSizes[i]
            self.accelerations[i][1] += self.forces[i][1] / self.anchorSizes[i]

            # Getting velocity
            self.velocities[i][0] += self.accelerations[i][0]*deltaTime
            self.velocities[i][1] += self.accelerations[i][1]*deltaTime

            # Collision with window frame
            if (((self.anchors[i][1] >= AppSize[1]-self.anchorSizes[i]) and (self.velocities[i][1] > 0)) or ((self.anchors[i][1] <= self.anchorSizes[i]) and (self.velocities[i][1] < 0))):
                self.velocities[i][1] = self.velocities[i][1]*-0.8
                self.velocities[i][0] = self.velocities[i][0]*0.9
            if (((self.anchors[i][0] >= AppSize[0]-self.anchorSizes[i]) and (self.velocities[i][0] > 0)) or ((self.anchors[i][0] <= self.anchorSizes[i]) and (self.velocities[i][0] < 0))):
                self.velocities[i][0] = self.velocities[i][0]*-0.8
                self.velocities[i][1] = self.velocities[i][1]*-0.9

            # Moving anchor
            self.anchors[i][0] += self.velocities[i][0]*deltaTime
            self.anchors[i][1] += self.velocities[i][1]*deltaTime

    def draw(self, surface):
        for i in range(len(self.anchors)):
            pygame.draw.circle(
                surface, "red", self.anchors[i], self.anchorSizes[i])
        for i in range(len(self.springs)):
            anchor1 = self.springs[i].anchor1
            anchor2 = self.springs[i].anchor2
            if (anchor1 != None and anchor2 != None):
                pygame.draw.line(
                    surface, "black", self.anchors[anchor1], self.anchors[anchor2], width=int(self.springs[i].stiffness))


spring = Springpy()

# GUI setup
holdB1 = False
holdB2 = False
selected = -1
prevLocked = False
mode = 0  # 0 for manipulating the anchors and 1 for adding springs, 2 for adding anchors, 3 for deleting
currentAnchorSize = 10
currentSpringStiffness = 1

if __name__ == "__main__":

    # For adding springs

    def GuiSetup():
        global guiManager, AppSize
        summonButton = pygame_gui.elements.UIButton(object_id="#summoningButton", relative_rect=pygame.Rect(
            (40, 40), (AppSize[0]/4, AppSize[1]/20)), text="Summon anchor", manager=guiManager)
        modeButton = pygame_gui.elements.UIButton(object_id="#modeButton", relative_rect=pygame.Rect(
            (40, 40+AppSize[1]/20), (AppSize[0]/4, AppSize[1]/20)), text=f"Mode: Manipulation", manager=guiManager)
        pauseButton = pygame_gui.elements.UIButton(object_id="#pauseButton", relative_rect=pygame.Rect(
            (40, 40+(2*AppSize[1]/20)), (AppSize[0]/4, AppSize[1]/20)), text=f"Playing", manager=guiManager)

    def GuiEvent(event: pygame.Event):
        global guiManager, spring, holdB1, holdB2, selected, prevLocked, mode, currentAnchorSize, currentSpringStiffness
        mousePos = numpy.array(pygame.mouse.get_pos())
        resolved = False
        if (event.type == pygame_gui.UI_BUTTON_PRESSED):
            # Add anchor (summonButton)
            if (event.ui_object_id == "#summoningButton"):
                spring.add_anchor(position=[random.random()*(AppSize[0]-20.0)+10.0, random.random()*(AppSize[1]-20.0)+10],
                                  initial_velocity=[(random.random()*2.0+-1.0)*10.0, (random.random()*2.0+-1)*10], locked=False)
                resolved = True
            if (event.ui_object_id == "#modeButton"):
                mode = (mode+1) % 4
                if mode == 0:
                    event.ui_element.set_text("Mode: Manipulation")
                elif mode == 1:
                    event.ui_element.set_text("Mode: Spring")
                elif mode == 2:
                    event.ui_element.set_text("Mode: Anchor")
                elif mode == 3:
                    event.ui_element.set_text("Mode: Deletion")
                resolved = True
            if (event.ui_object_id == "#pauseButton"):
                state = spring.Pause
                if (state):
                    event.ui_element.set_text("Playing")
                else:
                    event.ui_element.set_text("Paused")
                spring.Pause = not state
                resolved = True
        if resolved:
            return
        if (event.type == pygame.MOUSEBUTTONDOWN):
            if (event.button == 1):
                for i in range(len(spring.anchors)):
                    xCondition = (((spring.anchors[i][0]-spring.anchorSizes[i]) <= mousePos[0]) and (
                        mousePos[0] <= (spring.anchors[i][0]+spring.anchorSizes[i])))
                    yCondition = (((spring.anchors[i][1]-spring.anchorSizes[i]) <= mousePos[1]) and (
                        mousePos[1] <= (spring.anchors[i][1]+spring.anchorSizes[i])))
                    if (xCondition and yCondition):
                        selected = i
                        prevLocked = spring.locked[i]
                        spring.locked[i] = True
                        holdB1 = True
                        break
                if ((mode == 3) and (selected != -1)):
                    spring.remove_anchor(selected)
                    selected = -1
                if ((mode == 2) and (selected == -1)):
                    spring.add_anchor(position=mousePos.tolist(),
                                      size=currentAnchorSize, locked=True)
            elif (event.button == 3):
                if (not holdB2):
                    if mode == 0:
                        for i in range(len(spring.anchors)):
                            xCondition = ((spring.anchors[i][0]-spring.anchorSizes[i]) <= mousePos[0]) and (
                                mousePos[0] <= (spring.anchors[i][0]+spring.anchorSizes[i]))
                            yCondition = (((spring.anchors[i][1]-spring.anchorSizes[i]) <= mousePos[1]) and (
                                mousePos[1] <= (spring.anchors[i][1]+spring.anchorSizes[i])))
                            if (xCondition and yCondition):
                                spring.locked[i] = not spring.locked[i]
                                break
                    if mode == 3:
                        minDist = float("inf")
                        removedSpring = -1
                        index = -1
                        for s in spring.springs:
                            index += 1
                            A = numpy.array(spring.anchors[s.anchor1])
                            B = numpy.array(spring.anchors[s.anchor2])

                            AB = B-A
                            AP = mousePos - A
                            AB_len_squared = numpy.dot(AB, AB)
                            if (AB_len_squared == 0):
                                closest = A
                            else:
                                t = (
                                    max(0, (min(1, numpy.dot(AP, AB)/AB_len_squared))))
                                closest = A+t*AB
                            dist = numpy.linalg.norm(mousePos-closest)
                            # numerator = (v1[1]*mousePos[0])-(v1[0]*mousePos[1])+(spring.anchors[s.anchor2][0] *
                            #                                                      spring.anchors[s.anchor1][1])-(spring.anchors[s.anchor2][1]*spring.anchors[s.anchor1][0])
                            # denom = math.sqrt(math.pow(spring.anchors[s.anchor2][1]-spring.anchors[s.anchor1][1], 2)+math.pow(
                            #     spring.anchors[s.anchor2][0]-spring.anchors[s.anchor1][0], 2))
                            # dist = numerator/denom
                            if (dist < minDist and dist < 4):
                                minDist = dist
                                removedSpring = index
                        if (removedSpring != -1):
                            spring.springs.pop(removedSpring)

                    holdB2 = True
        elif (event.type == pygame.MOUSEBUTTONUP):
            if (event.button == 1):
                if ((mode == 1) and (selected != -1)):
                    for i in range(len(spring.anchors)):
                        xCondition = (((spring.anchors[i][0]-spring.anchorSizes[i]) <= mousePos[0]) and (
                            mousePos[0] <= (spring.anchors[i][0]+spring.anchorSizes[i])))
                        yCondition = (((spring.anchors[i][1]-spring.anchorSizes[i]) <= mousePos[1]) and (
                            mousePos[1] <= (spring.anchors[i][1]+spring.anchorSizes[i])))
                        if ((xCondition and yCondition) and (i != selected)):
                            if (selected != -1):
                                spring.add_spring(
                                    selected, i, stiffness=currentSpringStiffness)
                                spring.locked[selected] = prevLocked
                                selected = -1
                                holdB1 = False
                if (selected != -1):
                    spring.locked[selected] = prevLocked
                    selected = -1
                    holdB1 = False
            elif (event.button == 3):
                holdB2 = False
        elif event.type == pygame.MOUSEWHEEL:
            if (mode == 2):
                currentAnchorSize += event.y
            elif (mode == 1):
                currentSpringStiffness += event.y
        elif event.type == pygame.MOUSEMOTION:
            if holdB1 and selected != -1 and mode == 0:
                spring.anchors[selected][0] = event.pos[0]
                spring.anchors[selected][1] = event.pos[1]
        guiManager.process_events(event)

    def GuiDraw(surface: pygame.Surface):
        global guiManager, mode, holdB1, spring, selected, currentAnchorSize, currentSpringStiffness
        # If something is selected in spring adding mode
        if (selected != -1 and mode == 1):
            mousePos = numpy.array(pygame.mouse.get_pos()) - \
                numpy.array(surface.get_offset())
            pygame.draw.line(surface=surface, color=pygame.Color(180, 180, 180), start_pos=spring.anchors[selected], end_pos=list(
                [mousePos[0], mousePos[1]]), width=currentSpringStiffness)
        # If anchor adding mode
        if (mode == 2):
            mousePos = numpy.array(pygame.mouse.get_pos()) - \
                numpy.array(surface.get_offset())
            pygame.draw.circle(center=mousePos.tolist(), surface=surface, color=pygame.Color(
                190, 160, 160), radius=currentAnchorSize)
        guiManager.draw_ui(surface)

    app.appendToInvokeQueue(GuiSetup)
    app.invoke()
    app.appendToEventQueue(GuiEvent)
    app.appendToTaskQueue(guiManager.update)
    app.appendToTaskQueue(spring.update)

    app.appendToDrawQueue(spring.draw)
    app.appendToDrawQueue(GuiDraw)

    app.execute()
