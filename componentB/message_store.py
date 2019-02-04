"""
Routines to save data in AVRO file format
"""
import fastavro
import os
from pathlib import Path
import yaml


class AvroPersist:
    """
    Support for Avro file format
    """
    schema = None
    output_filename = ""

    def __init__(self):
        # Load schema from schema.avsc for Avro file
        path = os.path.abspath(__file__)
        module_dir_path = os.path.dirname(path)

        # Loading defined schema for messages from schema.avsc
        self.schema = fastavro.schema.load_schema(
            module_dir_path + "/schema.avsc")

        with open("config.yaml", 'r') as yml_file:
            try:
                config = yaml.load(yml_file)
                self.output_filename = config["componentB"]["output_file"]
                print(f"Saving messages into \"{self.output_filename}\"")
            except yaml.YAMLError as ex:
                print(ex)
                raise

    def persist_messages(self, messages):
        """
        Appending messages to Avro file on disk

        :param messages:
        :type messages: list
        :return: None
        """

        if len(messages) == 0:
            return

        print(
            f"ComponentB: Flushing buffer to disk with {len(messages)} messages")

        avro_file = Path(self.output_filename)
        if avro_file.is_file():
            with open(self.output_filename, 'a+b') as out:
                fastavro.writer(out, self.schema, messages)
        else:
            with open(self.output_filename, 'wb') as out:
                fastavro.writer(out, self.schema, messages)
