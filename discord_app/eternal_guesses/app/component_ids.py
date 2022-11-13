class ComponentIds:
    component_button_post_game_prefix = "button-post_game-"
    component_button_post_game_regex = r"button-post_game-(.*)"

    component_button_close_game_prefix = "action-manage_game-close-"

    @classmethod
    def component_button_close_game_id(cls, game_id):
        return f"{cls.component_button_close_game_prefix}{game_id}"

    component_button_reopen_game_prefix = "action-manage_game-reopen-"

    @classmethod
    def component_button_reopen_game_id(cls, game_id):
        return f"{cls.component_button_reopen_game_prefix}{game_id}"

    @classmethod
    def component_button_post_game_id(cls, game_id: str):
        return f"{ComponentIds.component_button_post_game_prefix}{game_id}"

    component_button_edit_guess_prefix = "button-manage_game-edit_guess-"

    @classmethod
    def component_button_edit_guess_id(cls, game_id):
        return f"{cls.component_button_edit_guess_prefix}{game_id}"

    component_button_delete_guess_prefix = "button-manage_game-delete_guess-"

    @classmethod
    def component_button_delete_guess_id(cls, game_id):
        return f"{cls.component_button_delete_guess_prefix}{game_id}"

    component_select_delete_guess_prefix = "selector-manage_game-delete_guess-"

    @classmethod
    def component_select_delete_guess_id(cls, game_id):
        return f"{cls.component_select_delete_guess_prefix}{game_id}"

    component_select_edit_guess_prefix = "selector-manage_game-edit_guess-"

    @classmethod
    def component_select_edit_guess_id(cls, game_id):
        return f"{cls.component_select_edit_guess_prefix}{game_id}"

    component_select_game_to_manage = "selector-select-game-to-manage"

    component_button_edit_game_prefix = "button-manage_game-edit-"

    @classmethod
    def component_button_edit_game_id(cls, game_id):
        return f"{cls.component_button_edit_game_prefix}{game_id}"

    component_button_guess_prefix = "button_trigger_guess_modal_"

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

    edit_guess_modal_prefix = "modal-edit_guess-game_"
    edit_guess_modal_regex = r"modal-edit_guess-game_(.*)-member_(.*)"

    @classmethod
    def edit_guess_modal_id(cls, game_id, member_id):
        return f"{cls.edit_guess_modal_prefix}{game_id}-member_{member_id}"

    edit_guess_modal_input_id = "modal-edit_guess-new_guess_input"

    selector_post_game_prefix = "select-post_game-"

    @classmethod
    def selector_post_game_id(cls, game_id):
        return f"{cls.selector_post_game_prefix}{game_id}"

    edit_game_title_modal_prefix = "modal-edit_game-title-"
    edit_game_min_guess_modal_prefix = "modal-edit_game-min_guess-"
    edit_game_max_guess_modal_prefix = "modal-edit_game-max_guess-"
    edit_game_description_modal_prefix = "modal-edit_game-description-"

    @classmethod
    def edit_game_title_modal_id(cls, game_id):
        return f"{cls.edit_game_title_modal_prefix}{game_id}"

    @classmethod
    def edit_game_min_guess_modal_id(cls, game_id):
        return f"{cls.edit_game_min_guess_modal_prefix}{game_id}"

    @classmethod
    def edit_game_max_guess_modal_id(cls, game_id):
        return f"{cls.edit_game_max_guess_modal_prefix}{game_id}"

    @classmethod
    def edit_game_description_modal_id(cls, game_id):
        return f"{cls.edit_game_description_modal_prefix}{game_id}"

    edit_game_title_input = "input-edit_game-title"
    edit_game_min_guess_input = "input-edit_game-min_guess"
    edit_game_max_guess_input = "input-edit_game-max_guess"
    edit_game_description_input = "input-edit_game-description"

    button_edit_game_title_prefix = "button-edit_game_title-"
    button_edit_game_min_guess_prefix = "button-edit_game_min_guess-"
    button_edit_game_max_guess_prefix = "button-edit_game_max_guess-"
    button_edit_game_description_prefix = "button-edit_game_description-"

    @classmethod
    def button_edit_game_title_id(cls, game_id):
        return f"{cls.button_edit_game_title_prefix}{game_id}"

    @classmethod
    def button_edit_game_min_guess_id(cls, game_id):
        return f"{cls.button_edit_game_min_guess_prefix}{game_id}"

    @classmethod
    def button_edit_game_max_guess_id(cls, game_id):
        return f"{cls.button_edit_game_max_guess_prefix}{game_id}"

    @classmethod
    def button_edit_game_description_id(cls, game_id):

        return f"{cls.button_edit_game_description_prefix}{game_id}"
