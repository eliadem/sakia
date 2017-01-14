import asyncio

from sakia.decorators import asyncify, once_at_a_time
from sakia.gui.sub.search_user.controller import SearchUserController
from .model import WotModel
from .view import WotView
from ..base.controller import BaseGraphController


class WotController(BaseGraphController):
    """
    The homescreen view
    """

    def __init__(self, parent, view, model, password_asker=None):
        """
        Constructor of the homescreen component

        :param sakia.gui.homescreen.view.HomeScreenView: the view
        :param sakia.gui.homescreen.model.HomeScreenModel model: the model
        """
        super().__init__(parent, view, model, password_asker)
        self.set_scene(view.scene())
        self.reset()

    @classmethod
    def create(cls, parent, app, connection, blockchain_service, identities_service):
        view = WotView(parent.view)
        model = WotModel(None, app, connection, blockchain_service, identities_service)
        wot = cls(parent, view, model)
        model.setParent(wot)
        search_user = SearchUserController.create(wot, app, currency=connection.currency)
        wot.view.set_search_user(search_user.view)
        search_user.identity_selected.connect(wot.center_on_identity)
        search_user.view.button_reset.clicked.connect(wot.reset)
        return wot

    def center_on_identity(self, identity):
        """
        Draw community graph centered on the identity

        :param sakia.core.registry.Identity identity: Center identity
        """
        self.draw_graph(identity)

    @once_at_a_time
    @asyncify
    async def draw_graph(self, identity):
        """
        Draw community graph centered on the identity

        :param sakia.core.registry.Identity identity: Center identity
        """
        self.view.busy.show()
        await self.model.set_identity(identity)
        self.refresh()
        self.view.busy.hide()

    def refresh(self):
        """
        Refresh graph scene to current metadata
        """
        nx_graph = self.model.get_nx_graph()
        self.view.display_wot(nx_graph, self.model.identity)

    def reset(self, checked=False):
        """
        Reset graph scene to wallet identity
        """
        self.draw_graph(None)