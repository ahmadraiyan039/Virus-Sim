"""The model classes maintain the state and logic of the simulation."""

from __future__ import annotations
from typing import List
from random import random
from projects.pj02 import constants
from math import sin, cos, pi, sqrt


__author__ = "730403230"  


class Point:
    """A model of a 2-d cartesian coordinate Point."""
    x: float
    y: float

    def __init__(self, x: float, y: float):
        """Construct a point with x, y coordinates."""
        self.x = x
        self.y = y

    def add(self, other: Point) -> Point:
        """Add two Point objects together and return a new Point."""
        x: float = self.x + other.x
        y: float = self.y + other.y
        return Point(x, y)

    def distance(self, other: Point) -> float:
        """Measures the distance between two line."""
        x: float = (self.x - other.x) ** 2
        y: float = (self.y - other.y) ** 2
        total: float = sqrt(x + y)
        return total


class Cell:
    """An individual subject in the simulation."""
    location: Point
    direction: Point
    sickness: int = constants.VULNERABLE

    def __init__(self, location: Point, direction: Point):
        """Construct a cell with its location and direction."""
        self.location = location
        self.direction = direction

    def tick(self) -> None:
        """Updates the screen."""
        self.location = self.location.add(self.direction)
        if self.is_infected():
            self.sickness += 1
        if self.sickness > constants.RECOVERY_PERIOD:
            self.immunize()

    def color(self) -> str:
        """Return the color representation of a cell."""
        vulnerbale_color: str = "gray"
        infected_color: str = "blue"
        immuned_color: str = "green"  
        if self.is_vulnerable():
            return vulnerbale_color
        elif self.is_immune():
            return immuned_color
        else:
            return infected_color

    def contract_disease(self) -> None:
        """Contracts disease to a vulnerable cell."""
        self.sickness = constants.INFECTED

    def is_vulnerable(self) -> bool:
        """Checks if a cell is vulnerable."""
        if self.sickness == constants.VULNERABLE:
            return True
        else:
            return False

    def is_infected(self) -> bool:
        """Checks if a cell is infected."""
        if self.sickness >= constants.INFECTED:
            return True
        else:
            return False

    def contact_with(self, other: Cell) -> None:  
        """Contracts disease if cell come in contact."""
        if self.is_infected() and other.is_vulnerable():
            other.contract_disease()
        elif self.is_vulnerable() and other.is_infected():
            self.contract_disease()

    def immunize(self) -> None:
        """Gives a cell immunity."""
        self.sickness = constants.IMMUNE

    def is_immune(self) -> bool:
        """Checks if a cell is immune."""
        if self.sickness == constants.IMMUNE:
            return True
        else:
            return False


class Model:
    """The state of the simulation."""

    population: List[Cell]
    time: int = 0
    infected_cells: int 

    def __init__(self, cells: int, speed: float, infected_cells: int, immune_cell: int = 0):
        """Initialize the cells with random locations and directions."""
        self.population = []
        self.infected_cells = infected_cells
        if infected_cells >= cells or infected_cells <= 0 or immune_cell >= cells or immune_cell <= 0:
            raise ValueError("Has to start with atleast one infected cell but less than total cells.")
        for i in range(0, immune_cell):
            start_loc = self.random_location()
            start_dir = self.random_direction(speed)
            self.population.append(Cell(start_loc, start_dir))
            self.population[i].immunize()
        for i in range(immune_cell, infected_cells + immune_cell):
            start_loc_2 = self.random_location()
            start_dir_2 = self.random_direction(speed)
            self.population.append(Cell(start_loc_2, start_dir_2))
            self.population[i].contract_disease()
        for i in range(infected_cells + immune_cell, cells):
            start_loc_3 = self.random_location()
            start_dir_3 = self.random_direction(speed)
            self.population.append(Cell(start_loc_3, start_dir_3))

    def tick(self) -> None:
        """Update the state of the simulation by one time step."""
        self.time += 1
        for cell in self.population:
            cell.tick()
            self.enforce_bounds(cell)
        self.check_contacts()

    def random_location(self) -> Point:
        """Generate a random location."""
        start_x = random() * constants.BOUNDS_WIDTH - constants.MAX_X
        start_y = random() * constants.BOUNDS_HEIGHT - constants.MAX_Y
        return Point(start_x, start_y)

    def random_direction(self, speed: float) -> Point:
        """Generate a 'point' used as a directional vector."""
        random_angle = 2.0 * pi * random()
        dir_x = cos(random_angle) * speed
        dir_y = sin(random_angle) * speed
        return Point(dir_x, dir_y)

    def enforce_bounds(self, cell: Cell) -> None:
        """Cause a cell to 'bounce' if it goes out of bounds."""
        if cell.location.x > constants.MAX_X:
            cell.location.x = constants.MAX_X
            cell.direction.x *= -1
        if cell.location.x < constants.MIN_X:
            cell.location.x = constants.MIN_X
            cell.direction.x *= -1
        if cell.location.y > constants.MAX_Y:
            cell.location.y = constants.MAX_Y
            cell.direction.y *= -1
        if cell.location.y < constants.MIN_Y:
            cell.location.y = constants.MIN_Y
            cell.direction.y *= -1

    def check_contacts(self) -> None:
        """Checks if cells have come in contact."""
        for i in range(0, len(self.population)):
            for j in range(i + 1, len(self.population)):
                if self.population[i].location.distance(self.population[j].location) < constants.CELL_RADIUS:
                    self.population[i].contact_with(self.population[j])

    def is_complete(self) -> bool:
        """Method to indicate when the simulation is complete."""
        count: int = 0
        stop: bool = False
        for i in range(0, len(self.population)):
            if self.population[i].is_immune() or self.population[i].is_vulnerable():
                count += 1
        if count == len(self.population):
            stop = True
        return stop