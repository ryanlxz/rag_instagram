class PromptLoader:
    """
    Class to load and store various text prompts from files.

    Designed to read prompts from specific filepaths and store them as
    attributes for easy access throughout application.
    """

    def __init__(self) -> None:
        """
        Initializes the PromptLoader instance.
        """
        self.extract_cuisine = self.load_prompt(
            filepath="src/prompts/extract_cuisine.txt"
        )
        self.extract_price = self.load_prompt(filepath="src/prompts/extract_price.txt")
        self.system_prompt = self.load_prompt(filepath="src/prompts/system_prompt.txt")

    def load_prompt(self, filepath: str) -> str:
        """
        Reads the content of a file and returns it as a string.

        This function opens a file at the specified `filepath`, reads its
        content, and then closes the file. It is intended for loading text data,
        such as prompts or configurations, from a file into a string variable.

        Args:
            filepath (str): The path to the file from which to read the content.

        Returns:
            str: The content of the file as a string.
        """
        with open(filepath) as file:
            return file.read()
