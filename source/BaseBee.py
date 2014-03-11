import abc

class BaseBee:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def arguments():
        """Return all the arguments given to the bee."""
        return

    @abc.abstractmethod
    def move(self, perception):
        """Move according to the perception"""
        return

    @abc.abstractmethod
    def shortRangeCommunicate(self, perception):
        """Sent out short range communication message"""
        return

    @abc.abstractmethod
    def name():
        """Return name of the type of bee"""
        return
        

        
