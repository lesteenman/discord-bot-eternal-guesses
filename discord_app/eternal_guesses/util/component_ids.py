class ComponentIds:
    component_button_post_game_prefix = "button-post_game-"
    component_button_post_game_regex = r"button-post_game-(.*)"

    @classmethod
    def component_button_close_game_id(cls, game_id):
        return f"action-manage_game-close-{game_id}"

    @classmethod
    def component_button_post_game_id(cls, game_id: str):
        return f"{ComponentIds.component_button_post_game_prefix}{game_id}"

    @classmethod
    def component_button_edit_guess_id(cls, game_id):
        return f"action-manage_game-edit_guess-{game_id}"

    component_button_delete_guess_prefix = "action-manage_game-delete_guess-"
    component_button_delete_guess_regex = "action-manage_game-delete_guess-(.*)"

    @classmethod
    def component_button_delete_guess_id(cls, game_id):
        return f"{cls.component_button_delete_guess_prefix}{game_id}"

    component_button_guess_prefix = "button_trigger_guess_modal_"
    component_button_guess_regex = r"button_trigger_guess_modal_(.*)"

    @staticmethod
    def component_button_guess_id(game_id: str):
        return f"{ComponentIds.component_button_guess_prefix}{game_id}"

    submit_create_modal_id = "modal_create_game"
    submit_create_input_game_id = "modal_create_game_id"
    submit_create_input_title = "modal_create_game_title"
    submit_create_input_description = "modal_create_game_description"
    submit_create_input_min_value = "modal_create_game_min_value"
    submit_create_input_max_value = "modal_create_game_max_value"

    submit_guess_modal_prefix = "modal_submit_guess_"
    submit_guess_modal_regex = "modal_submit_guess_(.*)"
    submit_guess_input_value = "modal_input_guess_value"

    @classmethod
    def submit_guess_modal_id(cls, game_id):
        return f"modal_submit_guess_{game_id}"
