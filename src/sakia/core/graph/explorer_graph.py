import logging
import networkx
import asyncio
from PyQt5.QtCore import pyqtSignal
from .base_graph import BaseGraph
from sakia.core.graph.constants import ArcStatus, NodeStatus


class ExplorerGraph(BaseGraph):

    graph_changed = pyqtSignal()

    def __init__(self, app, community, nx_graph=None):
        """
        Init ExplorerGraph instance
        :param sakia.core.app.Application app: Application instance
        :param sakia.core.community.Community community: Community instance
        :param networkx.Graph nx_graph: The networkx graph
        :return:
        """
        super().__init__(app, community, nx_graph)
        self.exploration_task = None
        self.explored_identity = None

    def start_exploration(self, identity, steps):
        """
        Start exploration of the wot from given identity
        :param sakia.core.registry.Identity identity: The identity source of exploration
        :param int steps: The number of steps from identity to explore
        """
        if self.exploration_task:
            if self.explored_identity is not identity:
                self.exploration_task.cancel()
            else:
                return
        self.explored_identity = identity
        self.exploration_task = asyncio.ensure_future(self._explore(identity, steps))

    def stop_exploration(self):
        """
        Stop current exploration task, if present.
        """
        if self.exploration_task:
            self.exploration_task.cancel()

    async def _explore(self, identity, steps):
        """
        Scan graph recursively
        :param sakia.core.registry.Identity identity:   identity instance from where we start
        :param int steps: The number of steps from given identity to explore
        :return: False when the identity is added in the graph
        """
        # functions keywords args are persistent... Need to reset it with None trick
        logging.debug("search %s in " % identity.uid)

        explored = []
        explorable = {0: [identity]}
        current_identity = identity
        for step in range(1, steps + 1):
            explorable[step] = []

        for step in range(0, steps):
            while len(explorable[step]) > 0:
                # for each pubkey connected...
                if current_identity not in explored:
                    self.add_identity(current_identity, NodeStatus.NEUTRAL)
                    logging.debug("New identity explored : {pubkey}".format(pubkey=current_identity.pubkey[:5]))
                    self.graph_changed.emit()

                    certifier_list = await current_identity.unique_valid_certifiers_of(self.app.identities_registry,
                                                                                             self.community)
                    await self.add_certifier_list(certifier_list, current_identity, identity)
                    logging.debug("New identity certifiers : {pubkey}".format(pubkey=current_identity.pubkey[:5]))
                    self.graph_changed.emit()

                    certified_list = await current_identity.unique_valid_certified_by(self.app.identities_registry,
                                                                                            self.community)
                    await self.add_certified_list(certified_list, current_identity, identity)
                    logging.debug("New identity certified : {pubkey}".format(pubkey=current_identity.pubkey[:5]))
                    self.graph_changed.emit()

                    for cert in certified_list + certifier_list:
                        if cert['identity'] not in explorable[step + 1]:
                            explorable[step + 1].append(cert['identity'])

                    explored.append(current_identity)
                    logging.debug("New identity explored : {pubkey}".format(pubkey=current_identity.pubkey[:5]))
                    self.graph_changed.emit()
                current_identity = explorable[step].pop()