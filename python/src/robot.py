# #!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module ...

__author__ = "Magnus Kvendseth Øye"
__copyright__ = "Copyright 2019, Sparkie Quadruped Robot"
__credits__ = ["Magnus Kvendseth Øye", "Petter Drønnen", "Vegard Solheim"]
__version__ = "1.0.0"
__license__ = "MIT"
__maintainer__ = "Magnus Kvendseth Øye"
__email__ = "magnus.oye@gmail.com"
__status__ = "Development"
"""


from states.states import InitState

class Sparkie(object):
    """ 
    A state machine for different behaviours.
    """

    def __init__(self):
        """ 
        Initialize the components.
        """

        # Start with a default state.
        self.state = InitState()

    def onEvent(self, event):
        """
        Incoming events are delegated to the given states
        which then handle the event. The result is then 
        assigned as the new state.
        """

        # The next state will be the result of the on_event function.
        self.state = self.state.onEvent(event)
    
    def onAction(self, actionEvent):
        """
        Incoming action events are delegated to the given states
        which then handle the action.
        """

        self.action = self.state.onAction(actionEvent)