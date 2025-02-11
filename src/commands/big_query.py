# Copyright 2025 Google, LLC
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from model.chain import Command, Context
from google.cloud import bigquery
from google.cloud.bigquery.table import RowIterator
import tempfile
import json


def FQTN(project_id: str, dataset_name: str, table_name: str):
        return f"{project_id}.{dataset_name}.{table_name}"
    
bigquery_client = bigquery.Client()

class BQPersistenceCommand(Command):
    """
    Represents a command that can query BQ and if needed create the table from 
    the provided schema.
    """
    def __init__(self,
                 name: str,
                 input_variable_name: str,
                 project_id: str,
                 dataset_name: str,
                 table_name: str,
                 json_schema: str | None,
                 create_table_if_not_exists: bool = False):
        
        super().__init__(name, self.execute)
        self.fqtn = FQTN(project_id, dataset_name, table_name)
        self.json_schema = json_schema
        self.create_table_if_not_exists = create_table_if_not_exists
        self.table_created = bigquery.Table(self.fqtn).exists()
        self.input_variable_name = input_variable_name
        
        
        async def execute(self, context: Context):
            if not self.table_created and self.create_table_if_not_exists and json_schema is not None:
                with tempfile.TemporaryFile(mode="w+") as fp:
                    fp.write(json_schema)
                    fp.seek(0)
                    bigquery_client.schema_from_json(fp)
                    bigquery_client.create_table(self.fqtn, exists_ok=True)
                    self.table_created = True
            
            if context.has_key(self.input_variable_name):
                if isinstance(context.get(self.input_variable_name), list):
                    bigquery_client.insert_rows_json(self.fqtn, [context.get(self.input_variable_name)])
                else:
                    bigquery_client.insert_rows_json(self.fqtn, context.get(self.input_variable_name))
    
                    
class BQEnrichmentCommand(Command):
    """
    Allows the user to enrich their context with query results from big query.
    """
    def __init__(self, name: str,
                 project_id: str,
                 dataset_name: str,
                 table_name: str, 
                 query: str, 
                 output_variable_name: str) -> None:
        super().__init__(name, self.execute)
        self.fqtn = FQTN(project_id, dataset_name, table_name)
        self.query = query
        self.output_variable_name = output_variable_name
        
    async def execute(self, context: Context):
       query_text = f"SELECT * from `{self.fqtn}` {super.expand_variables(self.query, context)}"
       
       out = []
       row_iterator: RowIterator = bigquery_client.query_and_wait(query_text)
       
       for row in row_iterator:
           out.append(dict(row))
       
       export = json.dumps(out)
       context.set(self.output_variable_name, export)
                    
                
        