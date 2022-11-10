class DiscordModalSubmit:
    def __init__(self, modal_custom_id: str, inputs: dict[str, str]):
        self.modal_custom_id = modal_custom_id
        self.inputs = inputs
