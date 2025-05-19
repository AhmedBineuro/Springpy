import pygame
from typing import Callable, List
from typing_extensions import Annotated, TypeAlias
# This is a general app framwork can be used for future purposes
Vector2D: TypeAlias = Annotated[List[float], 2]


class App:
    def __init__(self, name: str = "Tester", maxFPS: int = 60, dimensions: Vector2D = [600, 600]):
        self.running = False  # Boolean to see if the app is running
        self.displaySurface = None  # The display surface used to draw things
        self.dimensions: Vector2D = dimensions
        self.clock = None  # this clock will be used to control things independent of framerate
        self.deltaTime = 0
        self.maxFps = maxFPS
        self.name = name
        # Some functions that will be executed in the on_execute portion with a deltaTime parameter

        # Functions that will be performed after every delta time computation with a single parameter which is delta time
        self.taskQueue: List[Callable[[float], None]] = []
        # Functions that will be performed during the event loop with a single parameter which is the current event being evaluated
        self.eventQueue: List[Callable[[pygame.Event], None]] = []
        # Functions that will be performed during the drawing phase with a single parameter being the pygame.Surface which is the display surface
        self.drawQueue: List[Callable[[pygame.Surface], None]] = []
        # Functions that will be manually invoked using the invoke() function with no parameters
        self.invokeQueue: List[Callable[[], None]] = []

    # Initialize app attributes and pygame
    def init(self):
        pygame.init()
        self.displaySurface = pygame.display.set_mode(size=self.dimensions)

        pygame.display.set_caption(self.name)
        self.clock = pygame.time.Clock()
        self.running = True

    def invoke(self):
        for task in self.invokeQueue:
            task()

    def appendToInvokeQueue(self, func: Callable[[], None]):
        self.invokeQueue.append(func)

    def appendToEventQueue(self, func: Callable[[pygame.Event], None]):
        self.eventQueue.append(func)

    def appendToTaskQueue(self, func: Callable[[float], None]):
        self.taskQueue.append(func)

    def appendToDrawQueue(self, func: Callable[[pygame.Surface], None]):
        self.drawQueue.append(func)

    # To run the app
    def execute(self):
        while self.running:
            self.on_execute()
        pygame.quit()

    # Function that occurs every refresh of the app
    def on_execute(self):

        # Event section
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            for task in self.eventQueue:
                task(event)

                # Task section
        for task in self.taskQueue:
            task(self.deltaTime)

        # Drawing section
        self.displaySurface.fill("white")
        for task in self.drawQueue:
            task(self.displaySurface)
        pygame.display.flip()

        # To get deltaTime in milliseconds
        self.deltaTime = self.clock.tick(self.maxFps)/1000


if __name__ == "__main__":
    app = App(name="Sample App")
    app.init()
    app.execute()
