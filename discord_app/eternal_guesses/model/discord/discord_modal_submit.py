class DiscordModalSubmit:
    def __init__(self, modal_custom_id: str, inputs: dict[str, str]):
        self.modal_custom_id = modal_custom_id
        self.inputs = inputs

    def __repr__(self):
        return f"<DiscordModalSubmit modal_custom_id={self.modal_custom_id} inputs={self.inputs}>"
