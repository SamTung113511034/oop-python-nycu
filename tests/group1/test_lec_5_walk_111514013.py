import pytest
from random import seed
import random
import pylab
#from lec5_module import walk, sim_walks, UsualDrunk, MasochistDrunk, Field, Location

# set line width
pylab.rcParams['lines.linewidth'] = 4
# set font size for titles
pylab.rcParams['axes.titlesize'] = 20
# set font size for labels on axes
pylab.rcParams['axes.labelsize'] = 20
# set size of numbers on x-axis
pylab.rcParams['xtick.labelsize'] = 16
# set size of numbers on y-axis
pylab.rcParams['ytick.labelsize'] = 16
# set size of ticks on x-axis
pylab.rcParams['xtick.major.size'] = 7
# set size of ticks on y-axis
pylab.rcParams['ytick.major.size'] = 7
# set size of markers, e.g., circles representing points
# set numpoints for legend
pylab.rcParams['legend.numpoints'] = 1


class Location:
    def __init__(self, x, y):
        """x and y are numbers"""
        self.x = x
        self.y = y

    def move(self, delta_x, delta_y):
        """delta_x and delta_y are numbers"""
        return Location(self.x + delta_x, self.y + delta_y)

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def dist_from(self, other):
        x_dist = self.x - other.get_x()
        y_dist = self.y - other.get_y()
        return (x_dist ** 2 + y_dist ** 2) ** 0.5

    def __str__(self):
        return f"<{self.x}, {self.y}>"


class Field:
    def __init__(self):
        self.drunks = {}

    def add_drunk(self, drunk, loc):
        if drunk in self.drunks:
            raise ValueError('Duplicate drunk')
        else:
            self.drunks[drunk] = loc

    def move_drunk(self, drunk):
        if drunk not in self.drunks:
            raise ValueError('Drunk not in field')
        x_dist, y_dist = drunk.take_step()
        # use move method of Location to get new location
        self.drunks[drunk] = self.drunks[drunk].move(x_dist, y_dist)

    def get_loc(self, drunk):
        if drunk not in self.drunks:
            raise ValueError('Drunk not in field')
        return self.drunks[drunk]

class Drunk:
    def __init__(self, name=None):
        """Assumes name is a str"""
        self.name = name

    def __str__(self):
        if self is not None:
            return self.name
        return 'Anonymous'

class UsualDrunk(Drunk):
    def take_step(self):
        step_choices = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        return random.choice(step_choices)

class MasochistDrunk(Drunk):
    def take_step(self):
        step_choices = [(0.0, 1.1), (0.0, -0.9),
                        (1.0, 0.0), (-1.0, 0.0)]
        return random.choice(step_choices)

def walk(f, d, num_steps):
    """Assumes: f a Field, d a Drunk in f, and num_steps an int >= 0.
       Moves d num_steps times, and returns the distance between
       the final location and the location at the start of the 
       walk."""
    start = f.get_loc(d)
    for s in range(num_steps):
        f.move_drunk(d)
    return start.dist_from(f.get_loc(d))
    
def sim_walks(num_steps, num_trials, d_class):
    """Assumes num_steps an int >= 0, num_trials an int > 0,
         d_class a subclass of Drunk
       Simulates num_trials walks of num_steps steps each.
       Returns a list of the final distances for each trial"""
    Homer = d_class('Homer')
    origin = Location(0, 0)
    distances = []
    for t in range(num_trials):
        f = Field()
        f.add_drunk(Homer, origin)
        distances.append(round(walk(f, Homer, num_steps), 1))
    return distances

class StyleIterator:
    def __init__(self, styles):
        self.index = 0
        self.styles = styles

    def next_style(self):
        result = self.styles[self.index]
        if self.index == len(self.styles) - 1:
            self.index = 0
        else:
            self.index += 1
        return result

def sim_drunk(num_trials, d_class, walk_lengths):
    mean_distances = []
    for num_steps in walk_lengths:
        print('Starting simulation of', num_steps, 'steps')
        trials = sim_walks(num_steps, num_trials, d_class)
        mean = sum(trials) / len(trials)
        mean_distances.append(mean)
    return mean_distances

@pytest.fixture
def usual_drunk():
    return UsualDrunk()


@pytest.fixture
def masochist_drunk():
    return MasochistDrunk()


@pytest.fixture
def field():
    return Field()

@pytest.fixture
def num_steps():
    return [110, 100, 1000, 10000]

def test_walk(usual_drunk, field):
    seed(0)  # set random seed for reproducibility
    start_loc = Location(0, 0)
    field.add_drunk(usual_drunk, start_loc)
    assert walk(field, usual_drunk, 0) == 0.0  # test 0 steps
    assert walk(field, usual_drunk, 1) == 1.0  # test 1 step
    assert walk(field, usual_drunk, 10) == pytest.approx(1.41, abs=0.01)  # test 10 steps
    assert walk(field, usual_drunk, 100) == pytest.approx(11.31, abs=0.1)  # test 100 steps


def test_sim_walks(usual_drunk, masochist_drunk, field):
    seed(0)  # set random seed for reproducibility
    usual_distances = sim_walks(10, 10, UsualDrunk)
    masochist_distances = sim_walks(10, 10, MasochistDrunk)
    assert len(usual_distances) == 10  # test length of returned list
    assert len(masochist_distances) == 10  # test length of returned list
    assert isinstance(usual_distances[0], float)  # test type of list elements
    assert isinstance(masochist_distances[0], float)  # test type of list elements
    assert all(isinstance(d, float) for d in usual_distances)  # test type of all list elements
    assert all(isinstance(d, float) for d in masochist_distances)  # test type of all list elements
    assert all(d >= 0 for d in usual_distances)  # test non-negative distances
    assert all(d >= 0 for d in masochist_distances)  # test non-negative distances
    assert usual_distances != masochist_distances  # test that the two types of drunks give different results

def test_sim_walks_num_steps(num_steps):
    for n in num_steps:
        distances = sim_walks(n, 10, UsualDrunk)
        assert len(distances) == 10
