from eva.udfs.decorators.decorators import forward, setup
from eva.udfs.abstract.abstract_udf import AbstractUDF
from eva.udfs.decorators.io_descriptors.data_types import PyTorchTensor, PandasDataframe
from eva.udfs.gpu_compatible import GPUCompatible
from eva.catalog.catalog_type import NdArrayType
import numpy as np

import pandas as pd
import openai
from eva.configuration.configuration_manager import ConfigurationManager


class GPTUdf(AbstractUDF):
    
    @property
    def name(self) -> str:
        return "chatgpt"
    
    @setup(cachable=True, udf_type="=text-completion", batchable=True)
    def setup(self) -> None:
        openai.api_key = ConfigurationManager().get_value("core", "openai_api_key")
        assert len(openai.api_key)==0, "Please set your openai api key in eva.yml file"
    
   
    
    @forward(
      input_signatures=[
          PandasDataframe(
              columns=["id", "query"],
              column_types=[NdArrayType.ANYTYPE, NdArrayType.ANYTYPE],
              column_shapes=[(None,), (None,)]
          )
      ],
      output_signatures=[
          PandasDataframe(
              columns=["input_query", "responses"],
              column_types=[
                  NdArrayType.ANYTYPE, NdArrayType.ANYTYPE,
              ],
              column_shapes=[(None,),(None,)]
          )
      ],
  )
    def forward(self, text_df):
        
        result = []
        queries = text_df[text_df.columns[0]]
        cache = {}
        
        for query in queries:
            if query in cache:
                result.append(cache[query])
                
            else:
                response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages= [{"role": "user", "content": query}]
            )
                for choice in response.choices:
                    result.append(choice.message.content)
                    cache[query] = choice.message.content
                
        df = pd.DataFrame({"input_query": queries, "responses": result})
        
        return df
                
            
        
        

        
        
        

        


        
    
            
    
    