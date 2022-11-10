class CustomIdGenerator:
    trigger_post_game_action_prefix = "button-post_game-"
    trigger_post_game_action_regex = r"button-post_game-(.*)"

    @staticmethod
    def trigger_post_game_action(game_id: str):
        return f"{CustomIdGenerator.trigger_post_game_action_prefix}{game_id}"

    trigger_guess_modal_action_prefix = "button_trigger_guess_modal_"
    trigger_guess_modal_action_game_id_regex = r"button_trigger_guess_modal_(.*)"

    @staticmethod
    def trigger_guess_modal_action(game_id: str):
        return f"{CustomIdGenerator.trigger_guess_modal_action_prefix}{game_id}"

    submit_create_game_id = "modal_create_game_id"
    submit_create_game_title = "modal_create_game_title"
    submit_create_game_description = "modal_create_game_description"
    submit_create_game_min_value = "modal_create_game_min_value"
    submit_create_game_max_value = "modal_create_game_max_value"

    guess_modal_input_guess = "modal_input_guess_value"
