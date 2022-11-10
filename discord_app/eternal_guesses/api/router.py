import typing
from abc import ABC

from eternal_guesses.api.permission_set import PermissionSet
from eternal_guesses.api.route_definition import RouteDefinition, \
    ApplicationCommandDefinition, ComponentActionRouteDefinition, \
    ModalSubmitRouteDefinition
from eternal_guesses.api.route_handler import RouteHandler
from eternal_guesses.model.discord.discord_component import ComponentType
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.error.unkonwn_event_exception import \
    UnknownEventException
from eternal_guesses.model.lambda_response import LambdaResponse
from eternal_guesses.routes.route import Route
from eternal_guesses.util.component_ids import ComponentIds


class Router(ABC):
    async def route(self, event: DiscordEvent) -> LambdaResponse:
        pass


class RouterImpl(Router):
    def __init__(
        self,
        route_handler: RouteHandler,
        close_game_route: Route,
        list_games_route: Route,
        post_route: Route,
        create_route: Route,
        guess_route: Route,
        ping_route: Route,
        guild_info_route: Route,
        add_management_channel_route: Route,
        remove_management_channel_route: Route,
        add_management_role_route: Route,
        remove_management_role_route: Route,
        edit_guess_route: Route,
        delete_guess_route: Route,
        trigger_guess_modal_route: Route,
        modal_test_route: Route,
        message_with_buttons_route: Route,
        manage_game_route: Route,
        action_post_game_route: Route,
        action_trigger_edit_guess_route: Route,
        action_trigger_delete_guess_route: Route,
        submit_guess_route: Route,
        submit_create_route: Route,
    ):
        self.submit_guess_route = submit_guess_route
        self.submit_create_route = submit_create_route
        self.route_handler = route_handler
        self.list_games_route = list_games_route
        self.edit_guess_route = edit_guess_route
        self.delete_guess_route = delete_guess_route
        self.close_game_route = close_game_route
        self.post_route = post_route
        self.create_route = create_route
        self.guess_route = guess_route
        self.ping_route = ping_route
        self.guild_info_route = guild_info_route
        self.add_management_channel_route = add_management_channel_route
        self.remove_management_channel_route = remove_management_channel_route
        self.add_management_role_route = add_management_role_route
        self.remove_management_role_route = remove_management_role_route
        self.modal_test_route = modal_test_route
        self.trigger_guess_modal_route = trigger_guess_modal_route
        self.message_with_buttons_route = message_with_buttons_route
        self.manage_game_route = manage_game_route
        self.action_trigger_delete_guess_route = action_trigger_delete_guess_route
        self.action_trigger_edit_guess_route = action_trigger_edit_guess_route
        self.action_post_game_route = action_post_game_route

        self.routes = []
        self._register_routes()

    def _register_routes(self):
        routes = [
            ComponentActionRouteDefinition(
                self.trigger_guess_modal_route,
                component_type=ComponentType.BUTTON,
                custom_id_starts_with=ComponentIds.component_button_guess_prefix,
            ),
            ComponentActionRouteDefinition(
                self.action_post_game_route,
                component_type=ComponentType.BUTTON,
                custom_id_starts_with=ComponentIds.component_button_post_game_prefix,
            ),
            ComponentActionRouteDefinition(
                self.action_trigger_delete_guess_route,
                component_type=ComponentType.BUTTON,
                custom_id_starts_with=ComponentIds.component_button_delete_guess_prefix,
            ),
            ComponentActionRouteDefinition(
                self.action_trigger_edit_guess_route,
                component_type=ComponentType.BUTTON,
                custom_id_starts_with="action-manage_game-edit_guess-",
            ),
            ModalSubmitRouteDefinition(
                self.submit_guess_route,
                custom_id_starts_with=ComponentIds.submit_guess_modal_prefix,
            ),
            ModalSubmitRouteDefinition(
                self.submit_create_route,
                custom_id_starts_with=ComponentIds.submit_create_modal_id,
            ),
            ApplicationCommandDefinition(self.ping_route, 'ping'),
            ApplicationCommandDefinition(self.guess_route, 'guess'),
            ApplicationCommandDefinition(self.manage_game_route, 'manage-game'),
            ApplicationCommandDefinition(
                self.post_route, 'manage', 'post',
                permission=PermissionSet.MANAGEMENT
            ),
            ApplicationCommandDefinition(
                self.close_game_route, 'manage', 'close',
                permission=PermissionSet.MANAGEMENT
            ),
            ApplicationCommandDefinition(
                self.list_games_route, 'manage', 'list-games',
                permission=PermissionSet.MANAGEMENT
            ),
            ApplicationCommandDefinition(
                self.edit_guess_route, 'manage', 'edit-guess',
                permission=PermissionSet.MANAGEMENT
            ),
            ApplicationCommandDefinition(
                self.delete_guess_route, 'manage', 'delete-guess',
                permission=PermissionSet.MANAGEMENT
            ),
            ApplicationCommandDefinition(
                self.create_route, 'create-game', permission=PermissionSet.MANAGEMENT
            ),
            ApplicationCommandDefinition(
                self.guild_info_route, 'admin', 'info',
                permission=PermissionSet.MANAGEMENT
            ),
            ApplicationCommandDefinition(
                self.add_management_channel_route, 'admin',
                'add-management-channel', permission=PermissionSet.ADMIN
            ),
            ApplicationCommandDefinition(
                self.remove_management_channel_route, 'admin',
                'remove-management-channel', permission=PermissionSet.ADMIN
            ),
            ApplicationCommandDefinition(
                self.add_management_role_route, 'admin', 'add-management-role',
                permission=PermissionSet.ADMIN
            ),
            ApplicationCommandDefinition(
                self.remove_management_role_route, 'admin',
                'remove-management-role', permission=PermissionSet.ADMIN
            ),
            ApplicationCommandDefinition(
                self.modal_test_route, command='modal',
                permission=PermissionSet.MANAGEMENT
            ),
            ApplicationCommandDefinition(
                self.message_with_buttons_route, command='message-with-buttons',
                permission=PermissionSet.MANAGEMENT
            ),
        ]

        for r in routes:
            self._register(r)

    def _register_actions(self):
        pass

    def _register(self, definition: RouteDefinition):
        self.routes.append(definition)

    async def route(self, event: DiscordEvent) -> LambdaResponse:
        route = self.find_matching_route(event)

        if route is None:
            raise UnknownEventException(event)

        discord_response = await self.route_handler.handle(event, route)
        return LambdaResponse.success(discord_response.json())

    def find_matching_route(self, event: DiscordEvent) \
            -> typing.Optional[RouteDefinition]:
        for route in self.routes:
            if event.command is not None:
                if route.matches_command(event.command):
                    return route

            elif event.component_action is not None:
                if route.matches_component_action(event.component_action):
                    return route

            elif event.modal_submit is not None:
                if route.matches_modal_submit(event.modal_submit):
                    return route

        return None
